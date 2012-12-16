import csv
import io
import urllib2
import urllib
import urlparse
try:
    import simplejson as json
except ImportError:
    import json
import urllib

base_url = "https://gdata.youtube.com/"

def _make_url(endpoint, **kwargs):
    url = '%s?%s' % (
	urlparse.urljoin(base_url, endpoint),
	urllib.urlencode(_fix_kwargs(kwargs))
    )
    return url

def _fix_kwargs(kwargs):
    """
    Remove kwargs that are None
    """
    return dict([(k, v) for k, v in kwargs.items() if v != None])

def _request(url, data=None):
    """
    If data is None, makes a GET request, else makes a POST request
    """
    res = urllib2.urlopen(url, data)
    return json.loads(res.read())

def name():
    """
    Returns the human-readable name of this source
    """
    return "YouTube Search"

def list_attrs():
    """
    Returns a list of attributes that this miner can mine
    """
    return []

def to_csv(data):
    result = io.BytesIO()
    writer = csv.writer(result)
    writer.writerow(['Title', 'Author', 'Published', 'Category', 
		     'Description', 'Video'])
    for d in data:
	if 'mediagroup' in d['data']:
	    description = d['data'].get('mediagroup').get('mediadescription').get('t').encode('ascii', 'backslashreplace')
	else:
	    description = ''

	writer.writerow([d['data']['title']['t'].encode('ascii', 'backslashreplace'), 
			', '.join([a['name']['t'] for a in d['data']['author']]), 
			d['data']['published']['t'],
			', '.join([c['label'] for c in d['data']['category'] if 'label' in c]),
			description,
			d['data']['content']['src'].encode('ascii', 'backslashreplace')])

    return [('youtube_search', result.getvalue())]

def search(**kwargs):
    """
    Queries the search endpoint with given params. Query to search for is found
    in the q param. 
    """
    result = []
    url = _make_url('/feeds/api/videos', **kwargs)
    for i in range(10):
	print "url: " + url
	res = _request(url)
	if not res:
	    break
	result.extend(res['feed']['entry'])
	# find the next url
	nurl = ''
	for link in res['feed']['link']:
	    if link['rel'] == 'next':
		nurl = link['href']
	if not nurl:
	    break
	else: 
	    url = nurl
    return result

def run(query, attrs=[], since=None):
    """ 
    Searches public facebook posts for objects that contain the query. If since
    is specified, returns objects until a certain date, else returns as many 
    objects as it can. since can be any date accepted by PHP's strtotime. 
    """
    objs = search(q=query, orderby="published", alt="json", v=2, time="today")
    return objs

if __name__ == "__name__":
    run("hello")
