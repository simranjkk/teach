import json
from dajaxice.decorators import dajaxice_register
from dajax.core import Dajax
from content_management.views import subcategories
from dajaxice.utils import deserialize_form
from datetime import datetime
from django.db.models import Max

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

