from __future__ import unicode_literals

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.db import models
import uuid


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
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(verbose_name="email address", max_length=255, unique=True,)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)
    token = models.CharField(max_length=255, blank=True)

    objects = TablemateUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password", "first_name", "last_name"]

    def to_json(self):
        return {
            "id": self.id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
            "token": self.token
        }

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

class Table(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    server = models.ForeignKey("Server", related_name="tables")
    place = models.ForeignKey("Place", related_name="tables")
    requested = models.BooleanField()

class Server(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    place = models.ForeignKey("Place", related_name="servers")
    user = models.ForeignKey("TablemateUser", related_name="servers")

class Tab(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    table = models.ForeignKey("Table", related_name="tabs")
    user = models.ForeignKey("TablemateUser", related_name="tabs")
    active = models.BooleanField(default=True)
    total = models.DecimalField(max_digits=8, decimal_places=2)

class Order(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    tab = models.ForeignKey("Tab", related_name="orders")
    total = models.DecimalField(max_digits=8, decimal_places=2)

class OrderItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    order = models.ForeignKey("Order", related_name="items")
    item = models.ForeignKey("MenuItem", related_name="items")
    price = models.DecimalField(max_digits=8, decimal_places=2)

class Menu(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class MenuItem(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey("Menu", related_name="items")
    category = models.ForeignKey("Category", related_name="items")
    price = models.DecimalField(max_digits=8, decimal_places=2)

class MenuCategory(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    menu = models.ForeignKey("Menu", related_name="categories")
    name = models.CharField(max_length=255)

class Place(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    menu = models.OneToOneField("Menu")

class Review(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey("TablemateUser", related_name="reviews")
    server = models.ForeignKey("Server", related_name="reviews")
    rating = models.IntegerField(null=False)
    comment = models.TextField()
