from django.shortcuts import render
from django.http import HttpResponseRedirect,HttpResponseNotFound, HttpResponse
from .models import User, Category, Product, Address
from .forms import UserForm, LoginForm, AddressForm
from cart.models import CartItem
from cart.forms import CartForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required


from django.http import Http404
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from myapp.serializers import ProductSerializer

from xhtml2pdf import pisa
from django.template.loader import get_template
from django.template import Context
outputFilename = 'invoice.pdf'
# Create your views here.

from django.conf import settings
from django.core.mail import EmailMessage
def create_user(request):
	if request.method == 'POST':
		form = UserForm(request.POST)
		if form.is_valid():
			form.save()
			return HttpResponseRedirect('/login/')
	else:
		form = UserForm()
	return render(request,'create_user.html',{'form':form})

def login_page(request):
	if request.method == "POST":
		form = LoginForm(request.POST)
		if form.is_valid():
			email = request.POST['email']
			password = request.POST['password']
			user =authenticate(email=email, password=password)
			if user is not None:
				login(request, user)
				return HttpResponseRedirect('/home/')
			else:
				return HttpResponseNotFound('<h1>Invalid login</h1>')
	else:
		form =LoginForm()
		return render(request, 'login_page.html', {'form': form})

def logout_page(request):
	logout(request)
	return HttpResponseRedirect('/login/')
	
@login_required(login_url='/login/')
def home(request):
	form = Category.objects.all()
	pro = Product.objects.filter(is_featured=True)
	return render(request, 'home.html', {'f':form, 'p':pro})

def category(request, slug):
	pro = Product.objects.filter(categories__slug =slug)
	
	return render(request, 'product.html', {'f':pro})

def prodet(request, slug):
	pro = Product.objects.get(slug=slug)
	if request.method == 'POST':
		if CartItem.objects.filter(product = pro, user_id= request.user.id):
			c =CartItem.objects.get(product = pro, user_id= request.user.id)
			d = pro.price*int(request.POST['quantity'])
			c.total_price += d 
			c.quantity += int(request.POST['quantity'])
			c.save()
			# return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
			return HttpResponseRedirect('/home/')

		else:
			d = pro.price*int(request.POST['quantity'])
			c = CartItem.objects.create(product=pro,quantity=request.POST['quantity'], user=request.user, total_price=d)
			return HttpResponseRedirect('/home')

	else:
		pro = Product.objects.get(slug=slug)
		form = CartForm()
		context_dict = {'p': pro, 'f': form}
		return render(request, 'prodet.html', context_dict)

def viewcart(request):

	form = CartItem.objects.filter(user_id = request.user.id)
	

	context_dict = {'f':form}




	

	return render(request, 'viewcart.html', context_dict)

def checkout(request):
	
	user = request.user

	if not user.address:
		return HttpResponseRedirect('/addaddress')
	else:
		cart = CartItem.objects.filter(user = request.user)
		item = []
		total = 0
		for c in cart:
			itemid  =  c.product.id
			product = Product.objects.get(id= itemid)
			total  = total + float(c.quantity)*float(product.price)
			item.append({'name':product.name,'quantity':c.quantity, 'price':product.price,
			 'total':float(c.quantity)*float(product.price)})
	
		context_dict= {
			'item':item, 
			'total': total
			}
		html = get_template('invoice.html').render(context_dict)
		res = open(outputFilename, "w+b")
		pdf = pisa.CreatePDF(html, dest=res)
		res.seek(0)
		pdf = res.read()
		res.close()

		email = EmailMessage('invice','Ivoice of purchased items',settings.EMAIL_HOST_USER,['infymee@gmail.com'])
		f= open(outputFilename,'rb')
		email.attach_file(outputFilename,'application/pdf')
		email.send()
		print ('email sent')
		return HttpResponse(pdf, 'application/pdf')




	for i in c:	
		i.product.quantity -= i.quantity

	return render(request, 'checkout.html', {'f':c})
		
def dashboard(request,):
	if request.method == 'POST':
		c = CartItem.objects.filter(date_added=request.POST['datetime'])
		return render(request, 'dashboard.html', {'f':c})
	else:
		
		return render(request, 'dashboard.html')
	
# HTMLto pdf

def addaddress(request):
	if request.method == 'POST':
		district = request.POST.get('district')
		city = request.POST.get('city')
		wardno = request.POST.get('wardno')
		a = Address.objects.create(district=district,city=city,wardno=wardno)
		u = User.objects.get(id=request.user.id)
		u.address = a 
		u.save()
		return HttpResponseRedirect('/checkout/')



	else:
		form =AddressForm()
		return render(request, 'add_address.html', {'f': form})


from rest_framework.permissions import IsAuthenticatedOrReadOnly

class ProductList(APIView):
	permission_classes = (IsAuthenticatedOrReadOnly,)

	def get(self, request, format=None):
		products = Product.objects.all()
		serializer = ProductSerializer(products, many=True)
		return Response(serializer.data)

	def post(self, request, format=None):
		serializer = ProductSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status=status.HTTP_201_CREATED)
		return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


from django.conf import settings

def payement_form(request):
	context = {"stripe_key":settings.STRIPE_PUBLIC_KEY}
	return render(request, 'stripe.html', context)


def order_checkout(request):
	new_checkout = Checkout(product = Product.objects.get(id =1), quantity=10, totalprice=1000)
	if request.method == "POST":
		token = request.POST.get("stripeToken")

	try:
		charge = stripe.Charge.create(
			amount = 2000,
			currency = "usd",
			source = token,
			description="The product charged to the user"
			)

		new_checkout.charge_id = charge.id
	except stripe.error.CardError as ce:
		return False, ce

	else:
		new_checkout.save()
		return HttpResponse("Thank You")

from django.db.models import Q
def get_transactionhistoy(request):
	product = Product.objects.all().order_by('-id')
	query = request.GET.get("q")
	if query:
		transaction = product.filter(
			Q(name__icontains=query)|
			Q(brand__icontains=query)|
			Q(description__icontains=query)
			)
		return render(request, 'producthistory.html', {'product': transaction})
	else:
		return render(request, 'producthistory.html', {'product':product})