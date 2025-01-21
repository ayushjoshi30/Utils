from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import BaseUserManager
from django.utils.translation import gettext_lazy as _

class AppUserManager(BaseUserManager):
    def create_user(self, user_name, email, password=None, **extra_fields):
        """
        Creates and returns a user with an email, user_name and password.
        """
        if not email:
            raise ValueError(_('The Email field must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, user_name=user_name, **extra_fields)
        user.set_password(password)  # Hash the password
        user.save(using=self._db)
        return user

    def create_superuser(self, user_name, email, password=None, **extra_fields):
        """
        Creates and returns a superuser with an email, user_name and password.
        """
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('is_admin', True)

        return self.create_user(user_name, email, password, **extra_fields)
class AppUser(AbstractBaseUser):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    user_name = models.CharField(max_length=255, unique=True)
    email = models.EmailField(unique=True)
    mobile_no = models.CharField(max_length=15, unique=True)
    created_on_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    is_deleted = models.BooleanField(default=False)
    last_login = models.DateTimeField(auto_now=True)
    password = models.CharField(max_length=255)
    is_admin = models.BooleanField(default=False)

    # Custom manager
    objects = AppUserManager()

    USERNAME_FIELD = 'user_name'  # This specifies that 'user_name' will be the unique identifier
    REQUIRED_FIELDS = ['email','first_name','last_name','mobile_no']  # These are fields that are required for creating a user

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.user_name})"
    
    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return self.is_admin
