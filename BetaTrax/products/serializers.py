from rest_framework import serializers
from django.contrib.auth.models import User, Group

from .models import Product, DeveloperAssignment


class ProductSerializer(serializers.ModelSerializer):
    # Accept product_owner as a PK and developers as a list of PKs
    product_owner = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    developers = serializers.ListField(
        child=serializers.PrimaryKeyRelatedField(queryset=User.objects.all()),
        allow_empty=True,
        required=False,
    )

    class Meta:
        model = Product
        fields = ['id', 'product_id', 'version', 'name', 'status', 'created_at', 'product_owner', 'developers']
        read_only_fields = ['created_at']

    def validate(self, data):
        owner = data.get('product_owner')
        developers = data.get('developers', [])

        # Owner must be a ProductOwner or superuser
        if not (owner.is_superuser or owner.groups.filter(name='ProductOwner').exists()):
            raise serializers.ValidationError({'product_owner': 'Selected owner must be in ProductOwner group or be superuser.'})

        # Developers must be in Developer group or superuser
        for dev in developers:
            if not (dev.is_superuser or dev.groups.filter(name='Developer').exists()):
                raise serializers.ValidationError({'developers': f'User {dev.username} is not in Developer group.'})

        # Owner cannot also be a developer
        if owner in developers:
            raise serializers.ValidationError('Owner cannot also be listed as a developer.')

        return data

    def _save_developers(self, product, developers):
        # Remove existing assignments not in incoming list
        existing = {a.developer_id: a for a in product.developer_assignments.select_related('developer').all()}
        incoming_ids = {d.id for d in developers}

        # Delete assignments for developers no longer present
        for dev_id, assignment in existing.items():
            if dev_id not in incoming_ids:
                assignment.delete()

        # Create assignments for new developers
        for dev in developers:
            if dev.id not in existing:
                DeveloperAssignment.objects.create(developer=dev, product=product)

    def create(self, validated_data):
        developers = validated_data.pop('developers', [])
        product = super().create(validated_data)
        # persist developer assignments
        if developers:
            self._save_developers(product, developers)
        return product

    def update(self, instance, validated_data):
        developers = validated_data.pop('developers', None)
        product = super().update(instance, validated_data)
        if developers is not None:
            self._save_developers(product, developers)
        return product