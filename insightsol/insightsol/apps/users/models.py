from django.db import models
from django.contrib.auth.models import (
	AbstractBaseUser,
	BaseUserManager,
	PermissionsMixin,
)


from django.core.validators import RegexValidator
import random

from django.template.defaultfilters import slugify

from utils.models import TimeMixin

class UserManager(BaseUserManager):
	def create_user(self, email, username, name, password=None):
		if not email:
			raise ValueError("Users must have an email address")

		user = self.model(
			username=username, name=name, email=self.normalize_email(email)
		)

		user.set_password(password)
		user.save(using=self._db)

		return user

	def create_superuser(self, email, username, name, password):
		user = self.create_user(
			email=email, password=password, username=username, name=name
		)
		user.is_superuser = True
		user.is_admin = True
		user.is_staff = True
		user.save(using=self._db)
		return user


class User(AbstractBaseUser, PermissionsMixin,TimeMixin):
	"""
	User model extending AbstractBaseUser class with custom fields
	"""


	MALE = 1
	FEMALE = 2
	OTHER = 3
	GENDER_CHOICES = (
		(MALE, "Male"), 
		(FEMALE, "Female"),
		(OTHER,"Other")
	)

	username = models.CharField(unique=True, max_length=235, blank=True, null=True)
	name = models.CharField(max_length=255, db_column='display_name')
	email = models.EmailField(verbose_name="email address", max_length=255,unique=True)

	dob = models.DateField(null=True)
	gender = models.IntegerField(choices=GENDER_CHOICES,default=1)


	isd_code = models.IntegerField(null=False, default=91)
	phone_regex = RegexValidator(
		regex=r"^\+?1?[6789]\d{9,12}$",
		message="Please enter a valid phone number. Up to 13 digits allowed.",
	)
	phone_number = models.CharField(
		validators=[phone_regex], max_length=20, blank=True, db_index=True, db_column='mobile_number'
	)  # validators should be a list

	is_active = models.BooleanField(default=True)
	is_staff = models.BooleanField(default=False)
	is_superuser = models.BooleanField(default=False)
	
	objects = UserManager()
	USERNAME_FIELD = "email"
	REQUIRED_FIELDS = ["username", "name"]

	class Meta:
		db_table = "users"
		verbose_name_plural = "Users"

	def __str__(self):
		return "%s - %s" % (self.id, self.email)


	def save(self, *args, **kwargs):
		if self.name and not self.username:
			self.username = slugify(self.name)
			# Append User id to make usernames unique
			self.username = self.username + "-" + str(random.randint(1, 9999))

		super(User, self).save(*args, **kwargs)