from django.conf.urls import patterns, include, url
from django.views.generic import TemplateView
# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'teachoo_web_project.views.home', name='home'),
    # url(r'^teachoo_web_project/', include('teachoo_web_project.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^terms-conditions/$', TemplateView.as_view(template_name="webapp/terms_of_service.html")),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/', include('allauth.urls')),
    url(r'^dashboard/', include('content_management.urls')),
	url(r'^$', TemplateView.as_view(template_name="webapp/index.html")),
	url(r'^', include('webapp.urls')),
	
)

try:
	import pyrax, os
	pyrax.set_setting("identity_type", "rackspace")
	pyrax.set_default_region('HKG')
	pyrax.set_credentials(os.environ["RACKSPACE_USERNAME"],os.environ["RACKSPACE_API_KEY"])
	post_images_container = pyrax.cloudfiles.get_container("post-images")
	download_files_container = pyrax.cloudfiles.get_container("download-files")
except:
	print "error pyrax"


