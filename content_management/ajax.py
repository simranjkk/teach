import json
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from content_management.views import subcategories
from content_management.models import Category
from dajaxice.utils import deserialize_form
from datetime import datetime
from django.db.models import Max, F
import pyrax,os

@dajaxice_register
def update_subcategories(request, category_id):
	dajax = Dajax()
	
	out = []
	
	sub_categories = subcategories(category_id)
	
	for category in sub_categories:
		url = "/subjects" + category.url
		temp = "<option value=\"" + url + "\">" + category.name + "</option>" 
		out.append(temp)
	
	dajax.assign('#combo2','innerHTML',''.join(out))

	return dajax.json()

@dajaxice_register
def update_parent_categories(request, category_id):
    dajax = Dajax()
    
    out = []
    category = Category.objects.get( id = category_id )
    parent_categories = Category.objects.filter( lt__gt = category.lt, rt__lt = category.rt, rt = F('lt')+1 )
    
    for category in parent_categories:
        value = category.id
        temp = "<option value=\"" + str(value) + "\">" + category.url.split("/",2)[2] + "</option>" 
        out.append(temp)
    
    dajax.assign('#id_category','innerHTML',''.join(out))

    return dajax.json()

@dajaxice_register
def return_upload_url(request, filename):
	dajax = Dajax()
	pyrax.set_setting("identity_type", "rackspace")
	pyrax.set_default_region('HKG')
	pyrax.set_credentials(os.environ["RACKSPACE_USERNAME"],os.environ["RACKSPACE_API_KEY"])
	upload_container = pyrax.cloudfiles.get_container("post_images")
	upload_container.set_metadata({'Access-Control-Allow-Origin': 'http://localhost:8000'})

	upload_url = pyrax.cloudfiles.get_temp_url(upload_container, filename, 60*60, method='PUT')
	#dajax.add_data(upload_url, "upload_file")
	dajax.assign('#url_upload', 'innerHTML',''.join(upload_url))
	return dajax.json()

