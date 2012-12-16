from bs4 import BeautifulSoup
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

base_url = "http://www.youtube.com/"

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
    return res.read()

def name():
    """
    Returns the human-readable name of this source
    """
    return "YouTube Insights"

def list_attrs():
    """
    Returns a list of attributes that this miner can mine
    """
    return []

def _str_to_num(s):
    """
    Remove commas and converts string to number
    """
    return int(s.replace(',',''))

def parse(data):
    """
    Parses raw insights data and returns a dict of the data it parsed 
    """
    # Currently will fail horribly if format for insights changes. A better 
    # solution would be to have a dict that maps value names (e.g. views count, 
    # likes chart, etc.) to statements that could possibly return None (e.g. 
    # soup.find(class_="stats-views"), etc.) and iterate throught the dict, 
    # checking if each statement is not, and provide a default value if it is. 
    # This would prevent failing horribly. There probably are better solutions. 
    soup = BeautifulSoup(data)

    comments_box = soup.find(class_='stats-box-top stats-box-left')
    favorites_box = soup.find(class_='stats-box-top stats-box-right')
    likes_box = soup.find(class_='stats-box-bottom stats-box-left')
    dislikes_box = soup.find(class_='stats-box-bottom stats-box-right')

    res = {'views': {}, 'comments': {}, 'favorites': {}, 
	   'likes': {}, 'dislikes': {}}
    res['views']['count'] = _str_to_num(soup.find(class_="stats-views").h3.text)
    res['views']['chart'] = soup.find(class_="stats-big-chart-expanded").get('src')
    res['comments']['count'] = _str_to_num(comments_box.h4.text)
    res['comments']['chart'] = comments_box.img.get('src')
    res['favorites']['count'] = _str_to_num(favorites_box.h4.text)
    res['favorites']['chart'] = favorites_box.img.get('src')
    res['likes']['count'] = _str_to_num(likes_box.h4.text)
    res['likes']['chart'] = likes_box.img.get('src')
    res['dislikes']['count'] = _str_to_num(dislikes_box.h4.text)
    res['dislikes']['chart'] = dislikes_box.img.get('src')

    # "securely" scraping top demographics and top locations (because neither
    # are guaranteed to be there). 
    audience = soup.div.find(class_='stats-audience')
    for stat in audience.find_all('h4'): 
	if stat.text.find('demographics') != -1:
	    # next sibling twice because \n counts as a sibling
	    res['demographics'] = [x.text.strip() for x in 
		    stat.next_sibling.next_sibling.find_all('dd')] 

	elif stat.text.find('locations') != -1:
	    res['locations'] = [x.text.strip() for x in 
		    stat.next_sibling.next_sibling.find_all('dd')]

    if res.get('demographics', None) is None:
	res['demographics'] = ''
    if res.get('locations', None) is None:
	res['locations'] = ''

    return res

def to_csv(data):
    d = parse(data[0]['data'])

    stats = io.BytesIO()
    swriter = csv.writer(stats)
    swriter.writerow(['stat', 'count', 'chart'])
    for s in d:
	if s not in ('locations', 'demographics'):
	    swriter.writerow([s, d[s]['count'], d[s]['chart']])

    locations = io.BytesIO()
    lwriter = csv.writer(locations) 
    lwriter.writerow(['popular locations'])
    for location in d['locations']:
	lwriter.writerow([location])

    demographics = io.BytesIO()
    dwriter = csv.writer(demographics) 
    dwriter.writerow(['gender', 'age range'])
    for group in d['demographics']:
	dwriter.writerow([x.strip() for x in group.split(',', 1)])

    return [('stats.csv', stats.getvalue()), 
	    ('locations.csv', locations.getvalue()),
	    ('demographics.csv', demographics.getvalue())]

def _strip_xml(data):
    """
    Strips invalid XML from beginning and end of insights response from youtube
    """
    return '\n'.join(data.split('\n')[1:-1])

def insights(video_id):
    """
    Gets and returns insights for a given video id. 
    """
    url = _make_url('/insight_ajax', action_get_statistics_and_data=1,v=video_id)
    result = _request(url)
    return _strip_xml(result)

def run(video_id, attrs=[], since=None):
    """ 
    Searches public facebook posts for objects that contain the query. If since
    is specified, returns objects until a certain date, else returns as many 
    objects as it can. since can be any date accepted by PHP's strtotime. 
    """
    objs = insights(video_id)
    return objs

if __name__ == "__name__":
    run("hello")
