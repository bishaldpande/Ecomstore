from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.core.mail import send_mail
from django.utils import timezone

# Create your models here.
class Address(models.Model):
	district = models.CharField(max_length=250 )
	city = models.CharField(max_length=250 )
	wardno = models.IntegerField()


class UserManager(BaseUserManager):
	def _create_user(self, username, email,password, **extra_fields):
		if not email:
			raise ValueError('User must ener a email')

		email = self.normalize_email(email)

		user = self.model(username=username, email=email, **extra_fields)
		user.set_password(password)
		user.save(using=self._db)
		return user

	def create_user(self, username, email=None, password=None, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		return self._create_user(username, email, password, **extra_fields)
	
	def create_superuser(self, username, email, password, **extra_fields):
		extra_fields.setdefault('is_staff', True)
		extra_fields.setdefault('is_superuser', True)
		if extra_fields.get('is_staff')is not True:
			raise ValueError('Super user must have is_staff = True')
		if extra_fields.get('is_superuser') is not True:
			raise ValueError('Superuser must have is_superuser=True')



		return self._create_user(username, email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
	username= models.CharField(
		_('username'),
		max_length=150, blank=True, 
		help_text=_('Required 150 or fewer charecters. Letters digits and @/..only'),
		error_messages={
			'unique': _("A user with the uername already exists"),
		},
		)
	email = models.EmailField(_('email address'), unique=True, null=True)

	address = models.ForeignKey(Address, on_delete= models.CASCADE, blank=True, null=True)

	is_staff= models.BooleanField(
		_('staff status'),
		default = False,
		help_text=_('Designates whether this user an log into admin site'))
	
	is_superuser= models.BooleanField(
		_('Superuser status'),
		default = False,
		help_text=_('Designates whether this user can log into admin site'))

	is_active = models.BooleanField(
		_('active'), default = True,
		help_text=_('designates whetjer this user should be treated as active'
					'Unselect this instead of deleating accounts.')
		)
	date_joined = models.DateTimeField(_('date joined'), default = timezone.now)

	objects = UserManager()

	EMAIL_FIELD = 'email'
	USERNAME_FIELD = 'email'
	REQUIRED_FIELDS = ['username']

	def get_full_name(self):
		full_name = '%s'%self.username
		return full_name.strip()

	def get_short_name(self):
		return self.email

	def email_user(self, subject, message, from_email=None, **kwargs):
		send_mail(subject, message, from_email, [self.email], **kwargs)

class Category(models.Model):
	name = models.CharField(max_length=50)
	slug = models.SlugField(max_length=50, unique=True, help_text='Unique value for product page URl, created from name')
	description = models.TextField()
	is_acticve = models.BooleanField(default=True)
	meta_keywords = models.CharField(max_length=255, help_text="comma seperated for SEO key for meta tag")
	meta_description = models.CharField("Meta Description", max_length=255, help_text="Content for description of Meta tag")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)

	class Meta:
		db_table = 'Categories'
		ordering = ['-created_at']
		verbose_name_plural = 'Categories'

	def __str__(self):
		return("%s"%self.name)
	# this method is used to generate the link/URL 
	@models.permalink
	def get_absolute_url(self):
		return ("catalog_category", [self.slug,])

class Product(models.Model):
	name = models.CharField(max_length=255, unique=True)
	slug = models.SlugField(max_length=255, unique=True, help_text="Unique value for product page URl, created from name")
	brand = models.CharField(max_length=50)
	sku = models.CharField(max_length=50)
	price = models.DecimalField(max_digits=9, decimal_places=2)
	old_price = models.DecimalField(max_digits=9, decimal_places=2, blank=True,default=0.00)
	image = models.ImageField(upload_to="product/%y/%m/%d")
	is_active = models.BooleanField(default=True)
	is_featured = models.BooleanField(default=False)
	quantity = models.IntegerField()
	description = models.TextField()
	meta_keywords = models.CharField(max_length=255, help_text="comma seperated for SEO key for meta tag")
	meta_description = models.CharField("Meta Description", max_length=255, help_text="Content for description of Meta tag")
	created_at = models.DateTimeField(auto_now_add=True)
	updated_at = models.DateTimeField(auto_now=True)
	categories = models.ManyToManyField(Category)
 
	class Meta:
		db_table = 'products'
		ordering = ['-created_at']
		

	def __str__(self):
		return("%s"%self.name)

	@models.permalink
	def get_absolute_url(self):
		return ("catalog_product", [self.slug,])

	def sale_price(self):
		if self.old_priec> self.price:
			return self.price
		else:
			return None

class Checkout(models.Model):
	product = models.ForeignKey(Product, on_delete=models.CASCADE)
	quantity = models.IntegerField()
	totalprice = models.DecimalField(decimal_places=2, max_digits=10)
	chargeid = models.CharField(max_length=255)
	