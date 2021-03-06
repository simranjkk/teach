from django.template import RequestContext
from django.shortcuts import render_to_response, redirect, get_object_or_404
from content_management.models import Post, Category, PostForm, CategoryForm 
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseRedirect, HttpResponse
from datetime import datetime
from django.http import Http404
from django.db.models import F, Min, Max, Count, Q
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.exceptions import PermissionDenied
import json
from django.utils import timezone
import pyrax, os
from django.core import serializers
from content_management.helper import *
import uuid
from webapp.views import posts, subcategories
from django.forms.models import modelformset_factory


def leafCategoriesHtml(request):
    """updates leaf categories select list. Main Category lt and rt values are send using ajax $.get is used - createpost and reorder page"""

    if request.method=="GET":
        leaf_categories = leafCategories(request.GET['category_lt'], request.GET['category_rt'])
        if leaf_categories:
            options=''
            for category in leaf_categories:
                options+="<option value=" + str(category.id) + " >" + category.url.split("/",2)[2] + "</option>"

            return HttpResponse(options)
        else:
            return HttpResponse("") 
    else:
        return HttpResponse("") 

    

def leafCategories(category_lt, category_rt):
    leaf_categories =  Category.objects.filter(lt__gt=category_lt, rt__lt=category_rt, rt=F('lt')+1).order_by('lt')
    return leaf_categories


def postHtml(request):
    """creates list of posts in a category for ordering on reorder page """

    if request.method == "GET":
        distinct_posts = posts(request.GET["category_id"]).distinct('sequence')
        listItems=''
        for post in distinct_posts:
            listItems+= '<li class=\"ui-state-default\" id=\"id_' + post.post_name + '\"><span class=\"ui-icon ui-icon-arrowthick-2-n-s\"></span>' + post.post_name + '</li>'
        return HttpResponse(listItems)



def reorder(request):	
	'''
	This function is to reorder published posts. 
	'''

	if request.method == "POST":
		print request.POST	
		i=1
		post_name_hash=request.POST['sequence_hash'].split(",");
		for post_name in post_name_hash:
			post_name=post_name[3:]
			Post.objects.filter(post_name=post_name, published__isnull=False, category_id=request.POST['category_id']).update(sequence=i)
			i=i+1
		return HttpResponse("thank you")
	if request.method == "GET":
		return render_to_response('content_management/reorder_post.html', {}, RequestContext(request))



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
				post.update( trash = timezone.now(), published = None, draft = None, user_sequence = 0, sequence = 0 )
				count+=1
				# TODO:send notification to admin that author __ has deleted his post
	elif delete_type == 'delete':
		for key,post_id in request.POST.iteritems():
			if check_key(key): 
				if request.user.is_superuser:
					post=Post.objects.filter( id = post_id )
				else:
					post=Post.objects.get( id = post_id, author = request.user )
				post.update(trash=timezone.now(), published=None, draft=None, hidden=timezone.now(), user_sequence=0, sequence=0) #in case of hard delete hidden is also set
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
		post = Post.objects.get( id = post_id )
		if request.user.id == post.author_id:
			if request.method == 'POST':
				form = PostForm( request.POST, author = request.user, id_post = post.id, instance = post)
				if form.is_valid():
					edited_post = form.save( commit = False )
					edited_post.title=edited_post.category.url.replace('/',' ')
					edited_post.date_time_last_modified = timezone.now()
					edited_post.url = create_url(edited_post.category.url, edited_post.post_name)
					if 'draft' in request.POST:
						edited_post.draft = timezone.now() 
						edited_post.published =None 
						edited_post.trash = None
						edited_post.user_sequence=0
						edited_post.sequence=0
						edited_post.save()
						return HttpResponseRedirect("/dashboard/posts/drafts/")
					elif 'publish' in request.POST:
						
						if request.user.is_staff and post.published==None:
							edited_post.published = timezone.now() 
							edited_post.draft = None
							edited_post.trash = None
							temp = Post.objects.filter( category = edited_post.category, author = edited_post.author, published__isnull=False, draft=None, trash=None ).aggregate(Max('user_sequence')) 
							if temp['user_sequence__max']:
								edited_post.user_sequence = temp['user_sequence__max']+1
							else:
								edited_post.user_sequence = 1
							temp = Post.objects.filter( category = edited_post.category, published__isnull=False, draft=None, trash=None ).aggregate(Max('sequence'))
							if temp['sequence__max']:
								edited_post.sequence = temp['sequence__max'] +1
							else:
								edited_post.sequence = 1
							edited_post.save()
							return HttpResponseRedirect("/subjects" + edited_post.url + "author/" + edited_post.author.username)
							
						elif not request.user.is_staff:
							edited_post.published = None
							edited_post.draft = None 
							edited_post.trash = None 
							edited_post.save()
							return HttpResponseRedirect("/dashboard/posts/pending/")
						else:
							edited_post.save()
							return HttpResponseRedirect("/subjects"+ edited_post.url + "author/" + edited_post.author.username )
				else:
					print form.errors	
					return render_to_response('content_management/edit_post.html',{'form': form, 'post_id': post.id}, context)
			else:
				form = PostForm(instance = post)
				return render_to_response('content_management/edit_post.html',{'form': form, 'post_id': post.id}, context)
		else:
			raise PermissionDenied
	except Post.DoesNotExist:
		raise Http404	

	except Post.MultipleObjectsReturned:
		raise Http404
		#TODO: send notification to admin about the issue with reference of post id


@login_required()
def set_draft( request ):
	''' 
	This view saves all the posts in drafts whose post_id's are passed as POST parameters.
	'''
	count=0
	for key,post_id in request.POST.iteritems():
		if check_key(key):
			Post.objects.filter( id=post_id, author=request.user ).update( draft=timezone.now(), published=None, trash=None, user_sequence=0, sequence=0 )
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
					post.published = timezone.now() 
					post.draft = None
					post.trash = None
					temp = Post.objects.filter( category = post.category, published__isnull=False, draft=None, trash=None, post_name = post.post_name )
					if temp:
						post.sequence = temp[0].sequence
					else:
						temp = Post.objects.filter( category = post.category, published__isnull=False, draft=None, trash=None ).aggregate(Max('sequence'))
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
					post.draft=timezone.now()
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
	


	context = RequestContext(request)
	if request.method == 'POST':
		form = PostForm( request.POST, author = request.user )
			
		if form.is_valid():
			post=form.save(commit=False)
			post.title=post.category.url.replace('/',' ')
			post.date_time_created = timezone.now()
			post.date_time_last_modified  = timezone.now()
			post.author = request.user
			post.sequence = 0
			post.user_sequence = 0
			post.likes = 0
			post.url = create_url(post.category.url, post.post_name)
			if 'draft' in request.POST:
				post.draft = timezone.now() 
				post.save()
				return HttpResponseRedirect("/dashboard/posts/drafts/")
			elif 'publish' in request.POST or 'publishandcreate' in request.POST:
				temp = Post.objects.filter( category = post.category, author = post.author, hidden=None, draft=None, trash=None ).aggregate(Max('user_sequence')) 
				if temp['user_sequence__max']:
					post.user_sequence = temp['user_sequence__max']+1
				else:
					post.user_sequence = 1;

				if request.user.is_staff:
					post.published = timezone.now()
					temp = Post.objects.filter( category = post.category, published__isnull=False, draft=None, trash=None, post_name = post.post_name )
					if temp:
						post.sequence = temp[0].sequence
					else:
						temp = Post.objects.filter( category = post.category, published__isnull=False, draft=None, trash=None ).aggregate(Max('sequence'))
						if temp['sequence__max']:
							post.sequence = temp['sequence__max'] +1
						else:
							post.sequence = 1;
					post.save()
					if 'publish' in request.POST:
						return HttpResponseRedirect("/subjects" + post.url + "author/" + post.author.username)
					elif "publishandcreate" in request.POST:
						return HttpResponseRedirect("/create/post/")
				else:
					post.save()
					return HttpResponseRedirect("/dashboard/posts/pending/")
	else:
		form=PostForm(initial={'post_name':'', 'keywords':'', 'transcript':'', 'content':''})
       	return render_to_response('content_management/create_post.html', {'form':form}, context)

def generateUploadUrl(request):
	if request.is_ajax():
		original_filename = request.GET['filename']
		cleaned_filename = original_filename.replace(' ', "-").replace('_','-').lower()
		unique_filename=str(uuid.uuid4()) + cleaned_filename 
		CurrentDomain = request.META['HTTP_HOST']
		CurrentDomain = "http://" + CurrentDomain
		AllowedDomains = ["http://www.teachoo.com", "http://teachoo.com", os.environ["DOMAIN_NAME"]] # Change this when https is used
		if CurrentDomain in AllowedDomains: 
			if request.GET['FileType'] == "post_image":
				from teachoo_web_project.urls import post_images_container
				post_images_container.set_metadata({'Access-Control-Allow-Origin': CurrentDomain})
				UploadUrl = pyrax.cloudfiles.get_temp_url(post_images_container, unique_filename, 60, method='PUT')

			elif request.GET['FileType'] == "download_file":
				from teachoo_web_project.urls import download_files_container
				download_files_container.set_metadata({'Access-Control-Allow-Origin': CurrentDomain})
				UploadUrl = pyrax.cloudfiles.get_temp_url(download_files_container, unique_filename, 60, method='PUT')

			data={"UploadUrl":UploadUrl, "Filename":unique_filename}
			return HttpResponse(json.dumps(data), content_type='application/json')			


@user_passes_test(lambda u: u.is_staff)
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
				name = form.cleaned_data["name"]
				parent = form.cleaned_data["parent"]	
				url = form.cleaned_data["url"]
				description = form.cleaned_data["description"]	
				new_category = Category.objects.create_category(parent, name, url, description)
				if new_category:
					return HttpResponseRedirect("/subjects" + new_category.url)
				else:
					return HttpResponse("Some Problem occured. Try again later.")

		else:
			form = CategoryForm(initial={'name':'', 'description':'', 'url':''})
		return render_to_response('content_management/create_category.html', {'form':form}, context)
	
	else:
		raise PermissionDenied


@user_passes_test(lambda u: u.is_staff)
def delete_category(request):
	'''This view deletes the category...take care of posts inside categories...delete them first otherwise appropriate action
	cannot delete "subjects" category
	'''
	warnings=[]
	flag=False
	for key,category_id in request.POST.iteritems():
		if check_key(key):
			if Post.objects.filter(category_id=category_id, published__isnull=False).exists(): 
				warnings.append("delete all posts in category id " + category_id)
				flag=True
			elif Category.objects.filter(parent_id=category_id).exists():
				warnings.append("delete all the subcategories first from category id " + category_id)
				flag=True
			elif Post.objects.filter(category_id=category_id, published=None, trash=None, draft=None).exists():
				warnings.append("clear all the pending publish requests realted to category id "+ category_id)
				flag=True
	
			if not flag:
				try:
					category = Category.objects.get(id=category_id)
					category.delete_category()
				except Category.DoesNotExist:
					warnings.append("category does not exist with category id " + category_id)
	return  warnings		
	
@user_passes_test(lambda u: u.is_staff)
def dashboard_categories(request, warnings=None):
	
	if request.method == "POST":
		action_type = request.POST['action']
		if action_type=="delete":
			warnings = delete_category(request)
			
	categories = Category.objects.filter(lt__gt=1, published__isnull=False).order_by('lt')
	return render_to_response('content_management/dashboard_categories.html', {'categories':categories,'warnings':warnings}, RequestContext(request))

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
			posts = Post.objects.filter( published__isnull=False, draft=None, trash=None ).order_by('category__lt', 'id')
		else:
			posts = Post.objects.filter( author=request.user, published__isnull=False, draft=None, trash=None ).order_by('category__lt', 'user_sequence')

	elif post_type=="drafts":
		posts = Post.objects.filter( author=request.user, draft__isnull=False, published=None, trash=None ).order_by('category__lt', 'id')

	elif post_type=="trash":
		posts = Post.objects.filter( author=request.user, trash__isnull=False, published=None, draft=None, hidden=None ).order_by('category__lt', 'id')

	elif post_type=="pending":
		if request.user.is_superuser:
			posts = Post.objects.filter( published=None, draft=None, trash=None ).order_by('category__lt', 'id')
		else:
			posts = Post.objects.filter( author=request.user, published=None, draft=None, trash=None ).order_by('category__lt', 'id')

	else:
		raise Http404
	
	return render_to_response( 'content_management/dashboard_posts.html', {'posts':posts, 'warnings':warnings, 'type':post_type}, RequestContext(request) )


