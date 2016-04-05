from __future__ import unicode_literals

from django.contrib.auth.models import (
    BaseUserManager, AbstractBaseUser
)

from django.db import models
import uuid

class Table(models.Model):
    table_id    = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    server      = models.ForeignKey('Server', null=True, blank=True)       # Each table belongs to one server
    restaurant  = models.ForeignKey('Restaurant')   # Each table belongs to one restaurant
    size        = models.IntegerField(default=0)
    table_number    = models.IntegerField(default=-1)
    requested       = models.BooleanField(default=False)
    time_start      = models.DateTimeField(auto_now_add=True)
    active          = models.BooleanField(default=True)

    def to_json(self):
        return {
            "table_id": self.table_id,
            "server": self.server.to_json(),
            "restaurant": self.restaurant.to_json(),
            "size": self.size,
            "table_number": self.table_number,
            "requested": self.requested,
            "time_start": self.time_start,
            "active": self.active,
        }

class Restaurant(models.Model):
    restaurant_id = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def to_json(self):
        return {
            "restaurant_id": self.restaurant_id,
            "name": self.name,
            "address": self.address
        }

class Server(models.Model):
    server_id   = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    restaurant  = models.ForeignKey('Restaurant')
    user        = models.ForeignKey('TablemateUser')
    time_start  = models.DateTimeField(auto_now_add=True)
    time_end    = models.DateTimeField(null=True)
    active      = models.BooleanField(default=True)

    def to_json(self):
        return {
            "server_id": self.server_id,
            "first_name": self.user.first_name,
            "last_name": self.user.last_name,
            "email": self.user.email,
            "restaurant": self.restaurant.to_json(),
            "time_start": self.time_start,
            "time_end": self.time_end,
            "active": self.active
        }

class MenuCategory(models.Model):
    category_id = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    name = models.CharField(max_length=100)
    restaurant = models.ForeignKey('Restaurant')

    def to_json(self):
        return {
            "category_id": self.category_id,
            "name": self.name,
        }

class MenuItem(models.Model):
    item_id = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    restaurant = models.ForeignKey('Restaurant')
    category = models.ForeignKey('MenuCategory')
    name = models.CharField(max_length=64)
    price = models.DecimalField(max_digits=5, decimal_places=2)
    description = models.TextField(null=True, blank=True)

    def to_json(self):
        return {
            "item_id": self.item_id,
            "name": self.name,
            "category": self.category.name,
            "price": str(self.price),
            "description": self.description,
            "restaurant": self.restaurant.to_json(),
        }

class Order(models.Model):
    order_id = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    item = models.ForeignKey('MenuItem') # which menu item?
    table = models.ForeignKey('Table') # which table?
    customer = models.ForeignKey('TablemateUser') # who ordered it?
    receipt = models.ForeignKey('Receipt', null=True, blank=True) # The receipt that this order belongs to
    time = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)

    def to_json(self):
        return {
            "order_id": self.order_id,
            "item": self.item.to_json(),
            "active": self.active,
            "pending": self.pending,
            "customer": self.customer.to_json(),
        }

class Receipt(models.Model):
    receipt_id = models.CharField(primary_key=True, max_length=64, editable=False, blank=True, default=uuid.uuid4)
    customer = models.ForeignKey('TablemateUser')  # Each receipt belongs to one customer
    restaurant = models.ForeignKey('Restaurant') # Each receipt belongs to one restaurant
    total_bill = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    time = models.DateTimeField(auto_now_add=True)

    def to_json(self):
        return {
            "receipt_id": self.receipt_id,
            "restaurant": self.restaurant.to_json(),
            "total_bill": str(self.total_bill),
            "time": self.time,
        }

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
    is_active   = models.BooleanField(default=True)
    is_admin    = models.BooleanField(default=False)
    table = models.ForeignKey('Table', null=True, blank=True) # Each customer belongs to one table

    objects = TablemateUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["password"]

    def to_json(self):
        return {
            "user_id": self.user_id,
            "email": self.email,
            "first_name": self.first_name,
            "last_name": self.last_name,
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

