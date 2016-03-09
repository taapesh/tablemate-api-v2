from __future__ import unicode_literals

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.db import models
import uuid

class Table(models.Model):
    table_id    = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    size        = models.IntegerField(default=0)
    server_id   = models.CharField(max_length=64)
    server_name = models.CharField(max_length=255)
    restaurant_name = models.CharField(max_length=255)
    restaurant_addr = models.CharField(max_length=255)
    table_number    = models.IntegerField(default=-1)
    requested       = models.BooleanField(default=False)
    time_start      = models.DateTimeField(auto_now_add=True)
    time_end        = models.DateTimeField(null=True)

    class Meta:
        ordering = ('time_start',)

class ServerRegistration(models.Model):
    server_id = models.CharField(max_length=64)
    restaurant_name = models.CharField(max_length=255)
    restaurant_addr = models.CharField(max_length=255)
    time_start  = models.DateTimeField(auto_now_add=True)
    time_end    = models.DateTimeField(null=True)

class TablemateUserManager(BaseUserManager):
    def create_user(self, first_name, last_name, email, password):
        if not email:
            raise ValueError("Users must have an email address")

        user = self.model(
            email=self.normalize_email(email),
            first_name=first_name,
            last_name=last_name,
        )
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, first_name, last_name):
        user = self.create_user(
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name
        )
        user.is_admin = True
        user.save(using=self._db)
        return user

class TablemateUser(AbstractBaseUser):
    user_id     = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    email       = models.EmailField(verbose_name="email address", max_length=255, unique=True,)
    first_name  = models.CharField(max_length=255)
    last_name   = models.CharField(max_length=255)
    active_table_id = models.CharField(max_length=64)
    is_active   = models.BooleanField(default=True)
    is_admin    = models.BooleanField(default=False)

    objects = TablemateUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    def get_full_name(self):
        return self.email

    def get_short_name(self):
        return self.email

    def __unicode__(self):
        return self.email

    def has_perm(self, perm, obj=None):
        return True
        
    def has_module_perms(self, app_label):
        return True

    @property
    def is_staff(self):
        return self.is_admin

