from django.db import models


class SingletonManager(models.Manager):
    def get(self, *args, **kwargs):
        """
        Get will return the singleton instance if it exists and None otherwise.
        """
        return super().first()

    def create(self, *args, **kwargs):
        """
        Creates an object if it doesn't already exist.
        Otherwise updates the existing object.
        """
        singleton = self.get()

        if not singleton:
            return super().create(*args, **kwargs)

        singleton.save(*args, **kwargs)

        return singleton


class SoftDeletableManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(removed_at__isnull=True)
