"""
Base model classes with UUID primary keys.
"""
import uuid
from django.db import models


class UUIDModel(models.Model):
    """
    Abstract base model with UUID primary key.
    All models should inherit from this instead of models.Model.
    """
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text='Unique identifier for this record'
    )
    
    class Meta:
        abstract = True
