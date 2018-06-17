from django.db import models
from myapp.models import User, Product

# Create your models here.

class CartItem(models.Model):
	date_added = models.DateField(auto_now_add=True)
	quantity = models.IntegerField(default=1)
	product = models.ForeignKey(Product, unique=False, on_delete=models.CASCADE)
	user = models.ForeignKey(User, on_delete=models.CASCADE)
	total_price = models.DecimalField(max_digits=9, decimal_places=2)
