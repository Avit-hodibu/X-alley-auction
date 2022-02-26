from django import forms
from django.forms import ModelForm, Form
from auctions.models import Listing, ContactForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
User = get_user_model()



class CreateUserForm(UserCreationForm):
	class Meta:
		model = User
		fields = ['username', 'email', 'password1', 'password2']


class ListingForm(ModelForm):

    class Meta:
        model = Listing
        fields = '__all__'
        exclude = ['created_by', 'active', 'close_price', 'special']

    def __init__(self, *args, **kwargs):
        super(ListingForm, self).__init__(*args, **kwargs)
        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'w3-light-gray w3-input w3-margin w3-large'


class CommentFormInline(Form):
    text = forms.CharField()


class BidForm(Form):
    price = forms.IntegerField()


class ContactFormData(forms.ModelForm):
    
    class Meta:
        model = ContactForm
        fields = ('name', 'email', 'message')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name', 'name':'dzother[Name]','id':'name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email Address', 'name': 'dzother[Email]','id':'email'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Your Message..', 'rows':'4' , 'name': 'message','id':'message'}),
        }
