from content_management.models import Category 

def navbar_subjects(request):
	categories = Category.objects.filter(lt__gt=1, level__lt=3).order_by('lt'); 
	return {'categories':categories}
