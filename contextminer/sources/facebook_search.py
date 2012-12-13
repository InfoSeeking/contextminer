import csv
import io
import urllib2
import urllib
import urlparse
try:
    import simplejson as json
except ImportError:
    import json

token = "179777262045118|ea5f31c138bbcfbe88147210-100001922464631|-1CbD-hpIzdQwaut3zonK8e38aw"
base_url = "https://graph.facebook.com/"

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
    return "Facebook Search"

def list_attrs():
    """
    Returns a list of attributes that this miner can mine
    """
    return []

def to_csv(data):
    """
    Given a list of JSON facebook search data from mongodb's data collection, 
    returns a CVS representation of the data.
    """
    result = io.BytesIO()
    writer = csv.writer(result)
    writer.writerow(['from_name', 'from_id', 'type', 'likes', 
		     'created_time', 'message', 'link', 'object_id', 
		     'query'])
    for d in data:
	writer.writerow([d['data']['from']['name'].encode('ascii', 'backslashreplace'),
			 d['data']['from']['id'],
			 d['data']['type'],
			 d['data'].get('likes', {}).get('count', 0),
			 d['data']['created_time'],
			 d['data'].get('message', '').encode('ascii', 'backslashreplace'),
			 d['data'].get('link', ''),
			 d['data']['id'],
			 d['query'].encode('ascii', 'ignore')])
    return [('facebook_search.csv', result.getvalue())]

def search(**kwargs):
    """
    Queries the search endpoint with given params. Query to search for is found
    in the q param. 
    """
    result = []
    url = _make_url('/search', **kwargs)
    for i in range(10):
	print "url: " + url
	res = _request(url)
	if not res or not res.get('data'):
	    break
	result.extend(res['data'])
	url = res['paging']['next']
    return result

def run(query, attrs=[], since=None):
    """ 
    Searches public facebook posts for objects that contain the query. If since
    is specified, returns objects until a certain date, else returns as many 
    objects as it can. since can be any date accepted by PHP's strtotime. 
    """
    objs = search(q=query, since=since)
    return objs
