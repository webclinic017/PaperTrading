from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager


"""
Notes
Normalize email means normalize the email address by lower casing the domain part of it.
One application of normalizing emails is to prevent multiple sign ups. 
If your application lets the public to sign up, your application might attract the "unkind" types,
and they could attempt to sign up multiple times with the same email address by mixing symbols, upper and lower cases 
to make variants of the same email address. 
"""


class UserManager(BaseUserManager):
    def create_user(self, email, username, broker, api_key, secret_key, password=None):
        if not email:
            raise ValueError("Users must have an email address")
        if not username:
            raise ValueError("Users must have a username")
        if not broker:
            raise ValueError("Broker must be specified")
        if not api_key:
            raise ValueError("API key must be specified")
        if not secret_key:
            raise ValueError("Broker must be specified")

        user = self.model(email=self.normalize_email(email),
                          username=username,
                          broker=broker,
                          api_key=api_key,
                          secret_key=secret_key)

        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, username, broker, api_key, secret_key, password):
        user = self.create_user(email=self.normalize_email(email),
                                username=username,
                                broker=broker,
                                api_key=api_key,
                                secret_key=secret_key
                                )

        user.set_password(password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


# Create your models here.
class CustomUser(AbstractBaseUser):
    email = models.EmailField(verbose_name="email", max_length=30, unique=True)
    username = models.CharField(max_length=10, unique=True)
    broker = models.CharField(max_length=30)
    api_key = models.CharField(max_length=100, unique=True)
    secret_key = models.CharField(max_length=100, unique=True)

    date_joined = models.DateTimeField(verbose_name="date joined", auto_now_add=True)
    last_login = models.DateTimeField(verbose_name="last login_page", auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    hide_email = models.BooleanField(default=True)

    objects = UserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'broker', 'api_key', 'secret_key']

    def __str__(self):
        return self.username

    def has_perm(self, perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True
