from django.db import models
import uuid
from django.contrib.auth.models import AbstractUser,User,BaseUserManager
import datetime
from django.utils import timezone
import django
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils.translation import gettext_lazy as _
import os
import magic
# Create your models here.

class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

class User(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    name = models.CharField(max_length=200, blank=True)

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']
    objects = UserManager() ## This is the new line in the User model. ##

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile_pic = models.ImageField(upload_to="profile_pics", blank=True,null=True,default='default.png')
    job_function=models.CharField(max_length=50,blank=True,null=True)
    
    def __str__(self):
        return self.user.username
        
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


class UserFiles(models.Model):
    unique_file_num=models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    title = models.CharField(max_length=100)
    message = models.TextField()
    user=models.ForeignKey(User, on_delete=models.CASCADE)
    created_at=models.DateTimeField(default=datetime.datetime.now)
    def __str__(self):
        return self.title

class SharedFiles(models.Model):
    email_to = models.EmailField(blank=True, null=True)
    user_email = models.EmailField(blank=True,null=True)
    created_at=models.DateTimeField(auto_now_add=True)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False)
    userfile = models.ForeignKey(UserFiles, on_delete=models.CASCADE)


class DownloadFile(models.Model):
    userfile = models.ForeignKey(UserFiles, on_delete=models.CASCADE)
    uploads = models.FileField(upload_to ='uploads/%Y/%m/%d')
    file_name=models.CharField(max_length=200)
    unique_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    is_image=models.BooleanField(default=False)

    def __str__(self):
        return self.file_name +" from "+ self.userfile.title

    def extension(self):
        name, extension = os.path.splitext(self.uploads.name)
        temp = magic.from_file(self.uploads.path, mime=True)
        if temp.startswith('video'):
            print('It is a video', dir(temp))
            return 'video'
        return extension



# These two auto-delete files from filesystem when they are unneeded:

@receiver(models.signals.post_delete, sender=DownloadFile)
def auto_delete_file_on_delete(sender, instance, **kwargs):
    """
    Deletes file from filesystem
    when corresponding `MediaFile` object is deleted.
    """
    if instance.uploads:
        if os.path.isfile(instance.uploads.path):
            os.remove(instance.uploads.path)

@receiver(models.signals.pre_save, sender=DownloadFile)
def auto_delete_file_on_change(sender, instance, **kwargs):
    """
    Deletes old file from filesystem
    when corresponding `MediaFile` object is updated
    with new file.
    """
    if not instance.pk:
        return False

    try:
        old_file = MediaFile.objects.get(pk=instance.pk).uploads
    except MediaFile.DoesNotExist:
        return False

    new_file = instance.uploads
    if not old_file == new_file:
        if os.path.isfile(old_file.path):
            os.remove(old_file.path)
