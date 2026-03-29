from django.apps import AppConfig

class DefectsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'defects'

    def ready(self):
        # This line imports your signals and connects them to your models
        import defects.signals