from django.apps import AppConfig
from django.db.models.signals import post_migrate

def create_default_groups(sender, **kwargs):
    """
    Automatically generate 'Developer' and 'ProductOwner' groups 
    after database migrations are run.
    """
    from django.contrib.auth.models import Group
    Group.objects.get_or_create(name='Developer')
    Group.objects.get_or_create(name='ProductOwner')

class DefectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'defects'

    def ready(self):
        # This line imports your signals and connects them to your models
        import defects.signals
        
        # Hook up post_migrate signal to automatically create default groups
        post_migrate.connect(create_default_groups, sender=self)