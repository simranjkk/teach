from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from content_management.models import Post, Category 
from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.db.models import F, Min, Max, Count, Q
from django.contrib.auth.decorators import login_required, user_passes_test
import re, json
from django.core import serializers
from content_management.helper import slugify_url 
import uuid

def search(request):
	term=request.GET['query']
	categories = Category.objects.filter(name__icontains=term)
	posts = Post.objects.filter(post_name__icontains=term)

	return render_to_response('webapp/search_results.html',{'result_posts':posts, 'result_categories':categories},RequestContext(request))	

def subCategoriesHtml(request):
	"""updates level 2 categories on home page."""

	if request.method=="GET":
		subCategories = subcategories(request.GET["category_id"])
		if subCategories:
			options='<option value=\"#\">Select Sub-Topic</option>'
			for category in subCategories:
				options+="<option value=\"/subjects" + str(category.url) + "\">" + category.name + "</option>"
			return HttpResponse(options)
		else:
			return HttpResponse("")
	else:
		return HttpResponse("")

	
def nextCategory(category_id):
	'''
	Returns the next category. Used as a pager in render_post.
	'''

	try:
		category = Category.objects.get(id=category_id)
		next_categories = Category.objects.filter(lt__gt=category.lt, rt=F('lt')+1, published__isnull=False).order_by('lt')	
		if next_categories:
			return next_categories[0]
			
	except Category.DoesNotExist:
		return None	
	
	
def retrieve_post ( request, url, author_username=None):#store author username in post url which will make diff in url of categories and posts
	context = RequestContext(request)
	url = slugify_url(url)
	if author_username is not None:
		#requested_post = Post.objects.select_related('category').only('category__id').get( url = url, author__username = author_username, published__isnull = False )
		requested_post = get_object_or_404( Post, url = url, author__username = author_username, published__isnull = False, draft = None, trash = None)
		sibbling_posts = posts(requested_post.category_id)		 
		next_category = nextCategory(requested_post.category_id)
		return render_to_response('webapp/render_post.html', {'requested_post':requested_post, 'sibbling_posts':sibbling_posts , 'next_category':next_category}, context)

	else:
		requested_posts_count = Post.objects.filter( url = url, published__isnull = False, trash = None, draft = None).count()
		if requested_posts_count == 0:
			raise Http404
		elif requested_posts_count == 1:
			requested_post = Post.objects.select_related('author__username').only('author__username').get( url = url, published__isnull = False )
			return HttpResponseRedirect('/subjects' + url + 'author/' +  requested_post.author.username )	
		elif requested_posts_count >1:
			requested_posts = Post.objects.filter( url = url, published__isnull = False)
			return render_to_response('webapp/render_post.html', {'requested_posts':requested_posts }, context)
		else:
			raise Http404

def retrieve_category( request, url ):
	context = RequestContext(request)
	url = slugify_url(url)
	try:
		requested_category = Category.objects.get( url = url, published__isnull = False)
		result_type = "category"
		if (requested_category.rt == requested_category.lt + 1):
			results=posts(requested_category.id)
			if results.exists():			
				first_post = results[0]
				return HttpResponseRedirect('/subjects' + first_post.url + 'author/' +  first_post.author.username )	
		else:
			results = subtree( requested_category.lt, requested_category.rt, requested_category.level )

		return render_to_response('webapp/render_category.html', {'requested_category':requested_category, 'results':results, 'result_type':result_type}, context)
	except Category.DoesNotExist:
	# try if url matches any post
		return retrieve_post( request, url )		

def subcategories( parent_category_id ):
	'''
	This functions returns the list of subcategories.
	Parent category's 'id' is passed as parameter to this function.
	'''
	
	sub_categories = Category.objects.filter( parent__id = parent_category_id ).order_by( 'lt' )	
	return sub_categories

def subtree( parent_category_lt, parent_category_rt, parent_category_level):
	'''
	This function returns subtree upto 2 levels
	'''
	
	sub_tree = Category.objects.filter( lt__gt = parent_category_lt, rt__lt = parent_category_rt, published__isnull=False, level__lte=parent_category_level+2 ).order_by('lt')
	return sub_tree

def posts( category_id ):
	'''
	This function returns list of all the posts in the category whose 'id' is equal to 'category_id'.
	'''

	posts = Post.objects.filter( category__id = category_id, published__isnull = False, draft = None, trash = None).order_by( 'sequence' )
	return posts

