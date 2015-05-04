from django import forms

class ContactForm( forms.Form ):
	message = forms.CharField( widget=forms.Textarea )
	sender_email = forms.EmailField( label="Your email" )
	sender_name = forms.CharField( label="Your name", max_length=100 )
