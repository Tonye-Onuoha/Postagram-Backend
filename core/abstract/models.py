from django.db import models
import uuid
from django.http import Http404

class AbstractManager(models.Manager):
    def get_object_by_public_id(self, public_id):
        try:
            instance = self.get(public_id=public_id)
            return instance
        except (ValueError, TypeError):
            return Http404

class AbstractModel(models.Model):
    public_id = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = AbstractManager()

    class Meta:
        abstract = True # Django will ignore this class model and won’t generate migrations for this.


# Every model has at least one manager (even if you refuse to give it one, the defaults still exist).
# It’s the interface through which database query operations are provided to Django models and is used to retrieve the
# instances from the database. If no custom Manager is defined, the default name is objects.
# Managers are only accessible via model classes, not the model instances.
