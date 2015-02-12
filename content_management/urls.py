from django.conf.urls import patterns, url
from content_management import views
from content_management import forms
urlpatterns = patterns('',
	url(r'^search',views.search),
	url(r'^create/post/$', views.create_post, name='create_post'),
    url(r'^edit/post/(?P<post_id>\d+)/$', views.edit_post, name='edit_post'),
    url(r'^create/category/$', views.create_category, name='create_category'),
    url(r'^postlist/$',views.postHtml),
    url(r'^reorder/$',views.reorder),
    url(r'^updateleafcategory/', views.leafCategoriesHtml),
   url(r'^updatesubcategories/', views.subCategoriesHtml),
    url(r'^generateuploadurl/', views.generateUploadUrl),
    url(r'^dashboard/posts/(?P<post_type>\w+)/$', views.dashboard_posts),
	url(r'^dashboard/categories/$', views.dashboard_categories),
	url(r'^categories/$', views.dashboard_categories),
    url(r'^subjects/(?P<url>.+)/author/(?P<author_username>\w+)', views.retrieve_post),
    url(r'^subjects(?P<url>.+)', views.retrieve_category),
)
