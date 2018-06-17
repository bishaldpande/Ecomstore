"""webapp URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include,re_path
from django.conf import settings
from django.conf.urls.static import static
from myapp import views
from myapp.models import Category



from rest_framework import routers, serializers, viewsets

class CategorySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'

class CategoryViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer

router = routers.DefaultRouter()
router.register(r'category', CategoryViewSet)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', views.home, name='home'),
    path('user/',views.create_user,name='create_user'),
    path('login/',views.login_page,name='login_page'),
    path('logout/',views.logout_page,name='logout_page'),
    path('category/<slug:slug>/', views.category, name='cat_pro'),
    path('prodet/<slug:slug>/', views.prodet, name='product_detail'),
    path('viewcart/', views.viewcart, name='viewcart'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('checkout/', views.checkout, name="Checkedout"),
    path('addaddress/', views.addaddress, name='addaddress'),
    re_path(r'^api/', include(router.urls)),
    re_path(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('product/list/',views.ProductList.as_view()),
    path('payement/form/',views.payement_form, name='payement_form'),
    path('order/checkout/',views.order_checkout, name="order_checkout" ),
    path('transaction/history/', views.get_transactionhistoy, name="transactionhistoy")

]+static(settings.MEDIA_URL, document_root =settings.MEDIA_ROOT)