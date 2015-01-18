from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from content_management.models import Post, Category, PostForm, CategoryForm 
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime
from django.http import Http404
from django.db.models import F, Min, Max, Count
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
import re
from django.utils import timezone
import pyrax, os

def upload(request):
	if request.method == "POST":
		print request.POST
		print request.FILES
		pyrax.set_setting("identity_type", "rackspace")
		pyrax.set_default_region('HKG')
		pyrax.set_credentials('teachoo','b705ba1b54364caf8c057941a0171dd4')
		container = pyrax.cloudfiles.get_container("images")
		obj = container.store_object("i", request.FILES["img"])
		return HttpResponse("thanks for uploading image")
	else:
		return render_to_response('content_management/upload.html',{},RequestContext(request))

def slugify_url( url ):
	url = url.replace(' ', "-").replace('_','-')
	url = url.lower()
	if not url.startswith('/'):
		url = '/'+url
	if not url.endswith('/'):
		url = url + '/'
	return url
	
def retrieve_post ( request, url, author_username=None):#store author username in post url which will make diff in url of categories and posts
	context = RequestContext(request)
	url = slugify_url(url)
	if author_username is not None:
		#requested_post = Post.objects.select_related('category').only('category__id').get( url = url, author__username = author_username, published = True )
		requested_post = get_object_or_404( Post, url = url, author__username = author_username, published = True, draft = False, trash=False)
		sibbling_posts = posts(requested_post.category_id)		 
		return render_to_response('content_management/content_management_render_post.html', {'requested_post':requested_post, 'sibbling_posts':sibbling_posts }, context)

	else:
		requested_posts_count = Post.objects.filter( url = url, published = True, trash = False, draft = False).count()
		if requested_posts_count == 0:
			raise Http404
		elif requested_posts_count == 1:
			requested_post = Post.objects.select_related('author__username').only('author__username').get( url = url, published = True )
			return HttpResponseRedirect('/subjects' + url + 'author/' +  requested_post.author.username )	
		elif requested_posts_count >1:
			requested_posts = Post.objects.filter( url = url, published = True)
			return render_to_response('content_management/content_management_render_post.html', {'requested_posts':requested_posts }, context)
		else:
			raise Http404

def retrieve_category( request, url ):
	context = RequestContext(request)
	url = slugify_url(url)
	try:
		requested_category = Category.objects.get( url = url, published = True)
		if (requested_category.rt == requested_category.lt + 1):
			result_type = "post"
			results = posts( requested_category.id )
		else:
			result_type = "category"
			results = subcategories( requested_category.id )

		return render_to_response('content_management/content_management_render_category.html', {'requested_category':requested_category, 'results':results, 'result_type':result_type}, context)
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

def posts( category_id ):
	'''
	This function returns list of all the posts in the category whose 'id' is equal to 'category_id'.
	'''

	posts = Post.objects.filter( category__id = category_id, published = True, draft = False, trash = False).order_by( 'sequence' )
	return posts

def check_key(key):
	return re.match(r'^id{1,2}',key)

@login_required()
def delete_posts( request, delete_type ):
	'''
	This view deletes the posts. Only post author or staff users can delete post.
	Two types to delete post - 'temp' and 'permanent'
	'temp' - 'trash' boolean variable is set to True and 'publish' is set to False
	'permanent' - Permanently deletes the post object.
	'''

	count=0
	if delete_type == "trash":
		for key,post_id in request.POST.iteritems():
			if check_key(key):
				if request.user.is_superuser:
					post=Post.objects.filter( id = post_id )
				else:
					post=Post.objects.filter( id = post_id, author = request.user )
				post.update( trash = True, published = False, draft = False, user_sequence = 0, sequence = 0 )
				count+=1
				# TODO:send notification to admin that author __ has deleted his post
	elif delete_type == 'delete':
		for key,post_id in request.POST.iteritems():
			if check_key(key): 
				if request.user.is_superuser:
					post=Post.objects.filter( id = post_id )
				else:
					post=Post.objects.get( id = post_id, author = request.user )
				post.update(trash=True, published=False, draft=False, hidden=True, user_sequence=0, sequence=0)
				count +=1
				# TODO:send notification to admin that author __ has deleted his post
		
	else:
		return Http404
	warnings = [str(count) + 'Posts deleted']
	return warnings


@login_required()
def edit_post(request, post_id):
	'''
	This view is used to edit the post only by the post authors.
	'''
# take previous status under consideration i.e. draft or published, so that on editing published post its sequence and user_sequence does not change
	context = RequestContext(request)
	try:
		post = Post.objects.select_for_update().get( id = post_id )
		if request.user.id == post.author_id:
			if request.method == 'POST':
				form = PostForm( request.POST, instance = post)
				if form.is_valid():
					edited_post = form.save( commit = False )
					edited_post.date_time_last_modified = timezone.now()
					edited_post.url = create_url(edited_post.category.url, edited_post.post_name)
					if 'draft' in request.POST:
						edited_post.draft = True
						edited_post.published = False
						edited_post.trash = False
						edited_post.user_sequence=0
						edited_post.sequence=0
					elif 'publish' in request.POST and post.published==False:
						if request.user.is_staff:
							edited_post.published = True
							edited_post.draft = False
							edited_post.trash = False
							temp = Post.objects.filter( category = edited_post.category, author = edited_post.author, published=True, draft=False, trash=False ).aggregate(Max('user_sequence')) 
							edited_post.user_sequence = temp['user_sequence__max']+1
							temp = Post.objects.filter( category = edited_post.category, published=True, draft=False, trash=False ).aggregate(Max('sequence'))
							edited_post.sequence = temp['sequence__max'] +1
							
						else:
							edited_post.published = False
							edited_post.draft = False
							edited_post.trash = False
					edited_post.save()
					return HttpResponse("post edited. Thank YOu.")
	
			else:
				form = PostForm(instance = post)
				return render_to_response('content_management/content_management_edit_post.html',{'form': form, 'post_id': post.id}, context)
		else:
			raise PermissionDenied
	except Post.DoesNotExist:
		raise Http404	

	except Post.MultipleObjectsReturned:
		print "waheguru"
		#TODO: send notification to admin about the issue with reference of post id


@login_required()
def set_draft( request ):
	''' 
	This view saves all the posts in drafts whose post_id's are passed as POST parameters.
	'''
	count=0
	for key,post_id in request.POST.iteritems():
		if check_key(key):
			Post.objects.filter( id=post_id, author=request.user ).update( draft=True, published=False, trash=False, user_sequence=0, sequence=0 )
			count +=1
	warnings=[str(count) + 'posts sent to draft']
	return warnings

@login_required
def set_published( request ):
	"""
	This view is only for admin to publish posts of other users.
	"""
	
	if request.user.is_superuser:
		count=0
		warnings = []
		for key, post_id in request.POST.iteritems():
			if check_key(key):
				try:
					post = Post.objects.get( id=post_id )
					post.published = True
					post.draft = False
					post.trash = False
					temp = Post.objects.filter( category = post.category, published=True, draft=False, trash=False, post_name = post.post_name )
					if temp:
						post.sequence = temp[0].sequence
					else:
						temp = Post.objects.filter( category = post.category, published=True, draft=False, trash=False ).aggregate(Max('sequence'))
						if temp['sequence__max']:
							post.sequence = temp['sequence__max'] +1
						else:
							post.sequence = 1;

					post.save()
					count+=1
				except Post.DoesNotExist:
					warnings.append(" post with post id" + str(post_id) + "does Not exist")

		warnings.append(str(count)+ 'posts published')
		return warnings
	
	else:
		raise PermissionDenied

@login_required
def reject_post( request ):
	if request.user.is_superuser:
		count=0
		warnings = []
		for key, post_id in request.POST.iteritems():
			if check_key(key):
				try:
					post = Post.objects.get(id=post_id)
					post.draft=True
					count+=1
				except Post.DoesNotExist:
					warnings.append("post with post id" + str(post_id) + "does not exist")
		 
		warnings.append(str(count) + "posts rejected")	

@login_required()
def create_post(request):
	'''
    This view creates new post.
    If accessed by GET request than empty 'PostForm' is displayed.
    If POST request than a new post is created with the data submitted.
    '''
	
	pyrax.set_setting("identity_type", "rackspace")
        pyrax.set_default_region('HKG')
        pyrax.set_credentials(os.environ["RACKSPACE_USERNAME"],os.environ["RACKSPACE_API_KEY"])
        upload_container = pyrax.cloudfiles.get_container("post_images")
        upload_container.set_metadata({'Access-Control-Allow-Origin': 'http://localhost:8000'})

        upload_url = pyrax.cloudfiles.get_temp_url(upload_container, "jaspre", 60*60, method='PUT')





	context = RequestContext(request)
	if request.method == 'POST':
		form = PostForm(request.POST, author=request.user)
			
		if form.is_valid():
			post=form.save(commit=False)
			post.date_time_created = timezone.now()
			post.date_time_last_modified  = timezone.now()
			post.author = request.user
			post.sequence = 0
			post.user_sequence = 0
			post.likes = 0
			post.url = create_url(post.category.url, post.post_name)
			if 'draft' in request.POST:
				post.draft = True
				post.save()
				return HttpResponseRedirect("/dashboard/posts/drafts/")
			elif 'publish' in request.POST:
				temp = Post.objects.filter( category = post.category, author = post.author, published=True, draft=False, trash=False ).aggregate(Max('user_sequence')) 
				if temp['user_sequence__max']:
					post.user_sequence = temp['user_sequence__max']+1
				else:
					post.user_sequence = 1;

				if request.user.is_staff:
					post.published = True
					temp = Post.objects.filter( category = post.category, published=True, draft=False, trash=False, post_name = post.post_name )
					if temp:
						post.sequence = temp[0].sequence
					else:
						temp = Post.objects.filter( category = post.category, published=True, draft=False, trash=False ).aggregate(Max('sequence'))
						if temp['sequence__max']:
							post.sequence = temp['sequence__max'] +1
						else:
							post.sequence = 1;
					post.save()
					return HttpResponseRedirect("/subjects" + post.url + "author/" + post.author.username)
				else:
					post.save()
					return HttpResponseRedirect("/dashboard/posts/pending/")
		else:
			print form.errors
	else:
		form=PostForm(initial={'title':'', 'post_name':'', 'excerpt':'', 'metadata':'', 'content':''})
       	return render_to_response('content_management/content_management_create_post.html', {'form':form, 'upload_url':upload_url}, context)

def test(request):
	return HttpResponse("thank you")			


@login_required
def create_category(request):
	'''
	This view creates new category.
	If accessed by GET request than empty 'CategoryForm' is displayed.
	If POST request than a new post is created with the data submitted.
	'''
	if request.user.is_superuser:
		context = RequestContext(request)
	
		if request.method == 'POST':
			form = CategoryForm(request.POST)
			if form.is_valid():
				
				new_category = form.save(commit=False)

				parent = new_category.parent	
				try:
					new_category_created, created = Category.objects.get_or_create( name=new_category.name,url=create_url(parent.url, new_category.name),parent=new_category.parent,defaults={'lt':parent.rt, 'rt':parent.rt+1, 'level':parent.level+1, 'date_time':timezone.now(), 'published':True, 'description':new_category.description} )
					if created:
						Category.objects.filter(lt__gt=parent.rt).order_by('-lt').update(lt=F('lt')+2,rt=F('rt')+2)
						Category.objects.filter(lt__lte=parent.lt, rt__gte=parent.rt).order_by('lt').update(rt=F('rt')+2)
						return HttpResponse("Category added successfully")
					else:
						return HttpResponse("Category not added because same Category already exist plz check db")
				except Category.MultipleObjectsReturned:
						return HttpResponse("There are already multiple Category with this name (db error)")
			else:
				print form.errors
		else:
			form = CategoryForm(initial={'name':'', 'description':''})
		return render_to_response('content_management/content_management_create_category.html', {'form':form}, context)
	
	else:
		raise PermissionDenied

def create_url(parent_url, current_url):
	url = slugify_url(parent_url + current_url)
	return url

@user_passes_test(lambda u: u.is_staff)
def delete_category(request):
	'''This view deletes the category...take care of posts inside categories...delete them first otherwise appropriate action
	cannot delete "subjects" category
	'''
	warnings=[]
	flag=False
	for category_id in request.POST.itervalues():
		if Post.objects.filter(category_id=category_id, published=True).exists(): 
			warnings.append="delete all posts in category id" + category_id
			flag=True
		if Category.objects.filter(parent_id=category.id).exists():
			warnings.append="delete all the subcategories first form category id" + category_id
			flag=True
		if Post.objects.filter(category_id=category_id, published=False, trash=False, draft=False).exists():
			warnings.append="clear all the pending publish requests realted to category id"+ category_id
			flag=True
	
		if not flag:
			try:
				Post.objects.filter(category__id=category_id).update(category=None)
				category = Category.objects.get(id=category_id)
				Category.objects.filter(lt__gt = category.rt).update(lt=F('lt')-2, rt=F('rt')-2)
				Category.objects.filter(rt__gt = category.rt).update(rt=F('lt')-2)
				category.delete()
			except Category.DoesNotExist:
				print "error"
	return dashboard_categories(request, warnings)		
	
@user_passes_test(lambda u: u.is_staff)
def dashboard_categories(request, warnings=None):
	
	categories = Category.objects.filter(lt__gt=1).order_by('lt')
	return render_to_response('content_management/content_management_dashboard_categories.html', {'categories':categories,'warnings':warnings}, RequestContext(request))

@login_required()
def dashboard_posts(request, post_type, warnings=None):

	if request.method == "POST":
		action_type = request.POST['action']
		if action_type=="trash" or action_type=="delete":
			warnings = delete_posts(request, action_type)
		elif action_type=="draft":
			warnings = set_draft(request)
		elif action_type=="publish":
			warnings = set_published(request)

	if post_type=="published":
		if request.user.is_superuser:
			posts = Post.objects.filter( published=True, draft=False, trash=False ).order_by('category__lt', 'id')
		else:
			posts = Post.objects.filter( author=request.user, published=True, draft=False, trash=False ).order_by('category__lt', 'user_sequence')

	elif post_type=="drafts":
		posts = Post.objects.filter( author=request.user, draft=True, published=False, trash=False ).order_by('category__lt', 'id')

	elif post_type=="trash":
		posts = Post.objects.filter( author=request.user, trash=True, published=False, draft=False, hidden=False ).order_by('category__lt', 'id')

	elif post_type=="pending":
		if request.user.is_superuser:
			posts = Post.objects.filter( published=False, draft=False, trash=False ).order_by('category__lt', 'id')
		else:
			posts = Post.objects.filter( author=request.user, published=False, draft=False, trash=False ).order_by('category__lt', 'id')

	else:
		raise Http404
	
	return render_to_response( 'content_management/content_management_dashboard_posts.html', {'posts':posts, 'warnings':warnings, 'type':post_type}, RequestContext(request) )


