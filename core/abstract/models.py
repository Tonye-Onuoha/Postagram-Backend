from django.db import models
import uuid
from django.http import Http404
from django.core.cache import cache

class AbstractManager(models.Manager):
    def get_object_by_public_id(self, public_id):
        try:
            instance = self.get(public_id=public_id)
            return instance
        except (ValueError, TypeError):
            return Http404

    def _delete_cached_objects(app_label):
        if app_label == "core_post":
            cache.delete("post_objects")
        elif app_label == "core_comment":
            cache.delete("comment_objects")
        else:
            raise NotImplementedError

class AbstractModel(models.Model):
    public_id = models.UUIDField(db_index=True, unique=True, default=uuid.uuid4, editable=False)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    objects = AbstractManager()

    # In the following code, we retrieve app_label from the _meta attribute on the model.
    # If it corresponds to either core_post or core_comment, we invalidate the cache, and the rest of the instructions can proceed.
    def save(self, force_insert=False, force_update=False,using=None, update_fields=None):
        app_label = self._meta.app_label
        if app_label in ["core_post", "core_comment"]:
            _delete_cached_objects(app_label)
        return super(AbstractModel, self).save(force_insert=force_insert,force_update=force_update,using=using,update_fields=update_fields)

    def delete(self, using=None, keep_parents=False):
        app_label = self._meta.app_label
        if app_label in ["core_post", "core_comment"]:
            _delete_cached_objects(app_label)
        return super(AbstractModel, self).delete(using=using, keep_parents=keep_parents)

    class Meta:
        abstract = True # Django will ignore this class model and won’t generate migrations for this.


# Every model has at least one manager (even if you refuse to give it one, the defaults still exist).
# It’s the interface through which database query operations are provided to Django models and is used to retrieve the
# instances from the database. If no custom Manager is defined, the default name is objects.
# Managers are only accessible via model classes, not the model instances.
