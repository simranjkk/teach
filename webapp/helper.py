def create_url(parent_url, current_url):
	'''
	It creates url by appending current_url to the parent_url.
	'''

	url = slugify_url(parent_url + current_url)
	return url

def slugify_url( url ):
	'''
	convert all characters to lowercase, prepend and append '/', replace <space> with '-'(hyphen)
	'''

	url = url.replace(' ', "-").replace('_','-')
	url = url.lower()
	if not url.startswith('/'):
		url = '/'+url
	if not url.endswith('/'):
		url = url + '/'
	return url

