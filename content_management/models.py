from django.db import models
from django.db.models import ForeignKey, F
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User

class Category(models.Model):
	'''
	This model saves the subjects(categories) in MPTT or Nested Set Model form to maintain hierarchy.
	'''

	date_time = models.DateTimeField("Time when created or last modified")
	name = models.CharField("Name of the category", max_length=70)
	description = models.TextField("Category description", blank=True)
	url = models.CharField("Url", max_length=200)
	published = models.BooleanField("Published or not", default=False)
	lt = models.BigIntegerField ("MPTT left")
	rt = models.BigIntegerField("MPTT right")
	level = models.IntegerField("Depth level in the tree")
	parent = models.ForeignKey("self", blank=True, null=True)
        
	def __unicode__(self):
                return self.url


class Post(models.Model):
	'''
	This model contains post. One post corresponds to one small topic.
	'''

	category = models.ForeignKey(Category)
	author = models.ForeignKey(User)
	date_time_created = models.DateTimeField("Created Time")
	date_time_last_modified = models.DateTimeField("Last Modified Time")
	title = models.CharField("Title of the post", max_length=70)
	metadata = models.CharField("Metadata for seo", max_length=140, blank=True)
	post_name = models.CharField("Name", max_length=100)#used in url
	content = models.TextField("Content", blank=True)
	excerpt = models.CharField("Excerpt for hidden posts or search results", max_length=500, blank=True)
	published = models.BooleanField("Published or not", default=False)
	draft = models.BooleanField("Draft or not", default=False)
	hidden = models.BooleanField("Hidden or available to all", default=False)
	trash = models.BooleanField("If Post is deleted by user", default=False)
	user_sequence = models.IntegerField("Sequence defined by user")
	sequence = models.IntegerField("Sequence by teachoo")
	likes = models.IntegerField("Likes")
	url = models.CharField('Url', max_length=400)
        
	def __unicode__(self):
		return self.post_name
	


class PostForm(ModelForm):
	'''
	ModelForm for creating or editing posts.
	'''

	def __init__(self, *args, **kwargs):
		super(PostForm, self).__init__(*args, **kwargs)
		self.fields['category'] = forms.ModelChoiceField( queryset=Category.objects.filter(lt__gt=1, rt=F('lt')+1).order_by('lt'))

	class Meta:
		model = Post
		fields = ['title', 'metadata', 'post_name', 'excerpt', 'category', 'content']




class CategoryForm(ModelForm):
	'''
	ModelForm for creating or editing subjects.
	'''

	class Meta:
		model = Category
		fields = ['name', 'description', 'parent'] 
	
	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		self.fields['parent'] = forms.ModelChoiceField(  queryset=Category.objects.filter(lt__gte=0).order_by('lt'))
