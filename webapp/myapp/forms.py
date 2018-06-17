from django import forms
from .models import User, Product, Address


class ProductAdminForm(forms.ModelForm):
	class Meta:
		model = Product
		fields ='__all__'

		def clear_price(self):
			if self.cleaned_dat['price'] <= 0:
				raise form.validationError('Price must be graeater than zero')
			return self.cleaned_data['price']


class UserForm(forms.ModelForm):
	password1 = forms.CharField(label='Passsword', widget=forms.PasswordInput)
	password2 = forms.CharField(label='Passsword conformation', widget=forms.PasswordInput)
	class Meta:
		model = User
		fields = ('username','email')

	def clean_password2(self):
		password1 = self.cleaned_data.get('password1')
		password2 = self.cleaned_data.get('password2')

		if password1 and password2 and password1 != password2:
			raise forms.ValidationError("passwords don't match")
			return password2

	def save(self, commit=True):
		user = super(UserForm, self).save(commit=False)
		user.set_password(self.cleaned_data["password1"])
		if commit:
			user.save()
		return user

class LoginForm(forms.Form):
	email = forms.EmailField()
	password = forms.CharField(widget=forms.PasswordInput())
	class Meta:
		fields = ('email', 'password')

class AddressForm(forms.ModelForm):
	class Meta:
		model = Address
		fields ='__all__'


