from django.conf.urls import patterns, url
from webapp import views

urlpatterns = patterns('',
	url(r'^contact', views.contact),
	url(r'^search', views.search),
    url(r'^updatesubcategories/', views.subCategoriesHtml),
    url(r'^subjects/(?P<url>.+)/author/(?P<author_username>\w+)', views.retrieve_post),
    url(r'^subjects(?P<url>.+)', views.retrieve_category),
)
