from django.conf.urls import patterns, url
from content_management import views
urlpatterns = patterns('',
	url(r'^create/post/$', views.create_post, name='create_post'),
    url(r'^edit/post/(?P<post_id>\d+)/$', views.edit_post, name='edit_post'),
    url(r'^create/category/$', views.create_category, name='create_category'),
    url(r'^postlist/$',views.postHtml),
    url(r'^reorder/posts/$',views.reorder),
    url(r'^updateleafcategory/', views.leafCategoriesHtml),
    url(r'^generateuploadurl/', views.generateUploadUrl),
    url(r'^posts/(?P<post_type>\w+)/$', views.dashboard_posts),
	url(r'^categories/$', views.dashboard_categories),
)
