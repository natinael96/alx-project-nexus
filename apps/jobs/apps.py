from django.apps import AppConfig


class JobsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.jobs'
    
    def ready(self):
        """Import signals when app is ready."""
        import apps.jobs.signals  # noqa

