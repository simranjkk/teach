from django import forms

class ContactForm( forms.Form ):
	message = forms.CharField( label="Message", initial='' )
	sender_email = forms.EmailField( label="Your email", initial='' )
	sender_name = forms.CharField( label="Your name", max_length=100, initial='' )
