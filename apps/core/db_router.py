"""
Database router for read replicas.
"""
from django.conf import settings


class ReadReplicaRouter:
    """
    Router to direct read queries to read replica.
    """
    
    def db_for_read(self, model, **hints):
        """Point read operations to read replica if enabled."""
        if getattr(settings, 'USE_READ_REPLICA', False):
            return 'read_replica'
        return 'default'
    
    def db_for_write(self, model, **hints):
        """Always write to default database."""
        return 'default'
    
    def allow_relation(self, obj1, obj2, **hints):
        """Allow relations between objects."""
        return True
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Only migrate on default database."""
        if db == 'read_replica':
            return False
        return True
