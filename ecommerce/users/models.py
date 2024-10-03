from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from .producer import get_kafka_producer

class CustomUserManager(BaseUserManager):
    def create_user(self, email, username, password=None):
        if not email:
            raise ValueError('Users must have an email address')

        # Check for existing user with the same email
        if User.objects.filter(email=email).exists():
            raise ValueError('A user with this email already exists.')

        user = self.model(
            email=self.normalize_email(email),
            username=username,
        )
        user.set_password(password)
        user.save(using=self._db)
        
        # Emit user created event
        user.emit_user_created_event()
        return user

    def create_superuser(self, email, username, password):
        user = self.create_user(email=email, username=username, password=password)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    username = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.username

    def emit_user_created_event(self):
        producer = get_kafka_producer()
        event_data = {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
        }
        producer.send('user_created', value=event_data)
        producer.flush()  # Ensure the message is sent

    def emit_user_updated_event(self):
        producer = get_kafka_producer()
        event_data = {
            "user_id": self.id,
            "username": self.username,
            "email": self.email,
        }
        producer.send('user_updated', value=event_data)
        producer.flush()  # Ensure the message is sent

    class Meta:
        app_label = 'users'
