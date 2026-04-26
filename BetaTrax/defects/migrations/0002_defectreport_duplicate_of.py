from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('defects', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='defectreport',
            name='duplicate_of',
            field=models.ForeignKey(
                blank=True,
                help_text='Original report if this report is marked as duplicate.',
                null=True,
                on_delete=models.SET_NULL,
                related_name='duplicates',
                to='defects.defectreport',
            ),
        ),
    ]
