def create_url(parent_url, current_url):
	url = slugify_url(parent_url + current_url)
	return url

def slugify_url( url ):
	url = url.replace(' ', "-").replace('_','-')
	url = url.lower()
	if not url.startswith('/'):
		url = '/'+url
	if not url.endswith('/'):
		url = url + '/'
	return url

