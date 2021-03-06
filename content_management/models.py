from django.db import models
from django.db.models import ForeignKey, F, Q
from django.forms import ModelForm
from django import forms
from django.contrib.auth.models import User
from helper import create_url
from django.utils import timezone
from django.core.exceptions import ValidationError

class CategoryManager(models.Manager):
	def create_category(self, parent, name, url, description):
		 
		category = self.create(parent = parent,name = name,url = url,description = description, lt=parent.rt, rt=parent.rt+1, level=parent.level+1, date_time=timezone.now(), published=timezone.now() )

		Category.objects.filter(lt__gt=parent.rt).order_by('-lt').update(lt=F('lt')+2,rt=F('rt')+2)
		Category.objects.filter(lt__lte=parent.lt, rt__gte=parent.rt).order_by('lt').update(rt=F('rt')+2)

		return category		

class Category(models.Model):
	'''
	This model saves the subjects(categories) in MPTT or Nested Set Model form to maintain hierarchy.
	'''

	date_time = models.DateTimeField("Time when created or last modified")
	name = models.CharField("Name of the category", max_length=70)
	description = models.TextField("Category description", blank=True)
	url = models.CharField("Url", max_length=200, db_index=True)
	published = models.DateTimeField("Published or not", blank=True, null=True, default=None)
	lt = models.BigIntegerField ("MPTT left", db_index=True)
	rt = models.BigIntegerField("MPTT right")
	level = models.IntegerField("Depth level in the tree")
	parent = models.ForeignKey("self", blank=True, null=True)
	objects = CategoryManager() # CRUD operations        
	def __unicode__(self):
                return self.url


	
	def delete_category(self):
		Category.objects.filter(lt__gt = self.rt).update(lt=F('lt')-2, rt=F('rt')-2)
		Category.objects.filter(lt__lt = self.lt, rt__gt = self.rt).update(rt=F('rt')-2)
		self.delete()


class Post(models.Model):
	'''
	This model contains post. One post corresponds to one small topic.
	'''

	category = models.ForeignKey(Category)
	author = models.ForeignKey(User)
	date_time_created = models.DateTimeField("Created Time")
	date_time_last_modified = models.DateTimeField("Last Modified Time")
	title = models.CharField("Title of the post", max_length=140)
	transcript = models.TextField("Transcript: text version of image or other form", blank=True)
	post_name = models.CharField("Name", max_length=100, db_index=True)
	content = models.TextField("Content", blank=True)
	keywords = models.CharField("space separated keywords", max_length=500, blank=True)
	published = models.DateTimeField("Published or not", blank=True, null=True, default=None)
	draft = models.DateTimeField("Draft or not", default=None, blank=True, null=True)
	hidden = models.DateTimeField("Hidden or available to all", default=None, blank=True, null=True)
	trash = models.DateTimeField("If Post is deleted by user", default=None, blank=True, null=True)
	user_sequence = models.IntegerField("Sequence defined by user")
	sequence = models.IntegerField("Sequence by teachoo")
	likes = models.IntegerField("Likes")
	url = models.CharField('Url', max_length=400, db_index=True)
        
	def __unicode__(self):
		return self.post_name
	


class PostForm(ModelForm):
	'''
	ModelForm for creating or editing posts.
	'''
	def __init__(self, *args, **kwargs):
		self.author = kwargs.pop('author',None)
		self.post_id = kwargs.pop('id_post', None)
		super(PostForm, self).__init__(*args, **kwargs)

	class Meta:
		model = Post
		fields = ['transcript', 'post_name', 'keywords', 'category', 'content']

	def clean(self):
		cleaned_data = super(PostForm, self).clean()
		post_name = cleaned_data.get("post_name")
		category = cleaned_data.get("category")
		if Post.objects.filter( ~Q(id = self.post_id), category = category, author = self.author, post_name = post_name, draft=None, trash=None, hidden = None).exists(): 
			error = u"Post with same name is already published or is in request queue"	
			print self.post_id 
		
			self._errors["post_name"] = self.error_class([error])
			del cleaned_data["post_name"]
			
		return cleaned_data #this statement is not required in django1.7

class CategoryForm(ModelForm):
	'''
	ModelForm for creating or editing subjects.
	'''
	url = forms.CharField(max_length=200, required=False)

	class Meta:
		model = Category
		fields = ['name', 'description', 'parent'] 
	
	def __init__(self, *args, **kwargs):
		super(CategoryForm, self).__init__(*args, **kwargs)
		self.fields['parent'] = forms.ModelChoiceField(  queryset=Category.objects.filter(lt__gte=0).order_by('lt'))

	def clean(self):
		cleaned_data = super(CategoryForm, self).clean()
		category_name = cleaned_data.get("name")
		category_parent = cleaned_data.get("parent")
		# create and store url with the help of its parent category url
		if category_name and category_parent:
			self.cleaned_data["url"] = create_url(category_parent.url, category_name)
			category_url = cleaned_data.get("url")
			if Category.objects.filter(parent = category_parent, url=category_url).exists():
				error = u"Category with same name already exists."
				self.errors["name"] = self.error_class([error])
				del cleaned_data["name"]
		return cleaned_data
