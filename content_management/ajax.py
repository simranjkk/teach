import json
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from content_management.views import subcategories
from content_management.models import Category
from dajaxice.utils import deserialize_form
from datetime import datetime
from django.db.models import Max, F

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

