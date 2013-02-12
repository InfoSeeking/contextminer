import datetime
import hashlib
import flask
import functools
import gevent
from gevent.pywsgi import WSGIServer
import logging
import math
import time
import zipfile
import io
from flask.views import View, MethodView
from db import Database, DatabaseError
try:
    import simplejson as json
except ImportError:
    import json

import miners
import jinja_filters

app = flask.Flask(__name__)
app.secret_key = 'pineapple'

db_host = 'localhost'
db_port = 27017

logging.basicConfig(level=logging.DEBUG)

# setup custom filters
app.jinja_env.filters['humanize'] = jinja_filters.humanize
app.jinja_env.filters['format_insights'] = jinja_filters.format_insights

# decorators {{
def csv(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
	logging.debug("I'm returning csv!")
	response = flask.make_response(method(*args, **kwargs))
	response.headers['Content-Type'] = 'text/csv; charset=utf-8'
	return response
    return wrapper

def zip(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
	logging.debug("I'm returning a zip!")
	response = flask.make_response(method(*args, **kwargs))
	response.headers['Content-Type'] = 'application/zip' 
	return response
    return wrapper

def with_db(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
	logging.debug("I'm with the db!")
	if not hasattr(flask.g, 'db'):
	    flask.g.db = Database(db_host, db_port)
	result = method(*args, **kwargs)
	return result
    return wrapper

def session(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
	if 'user' in flask.session:
	    logging.debug("I'm logged in!")
	    return method(*args, **kwargs)
	logging.debug("I'm not logged in!")
	return flask.redirect(flask.url_for('login'))
    return wrapper

def admin(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
	user = flask.g.db.get_user({'username': flask.session.get('user')})
	if user.get('admin', 0):
	    logging.debug("I'm an admin!")
	    return method(*args, **kwargs)
	logging.debug("I'm not an admin!")
	return flask.abort(404)
    return wrapper

def json(method):
    @functools.wraps(method)
    def wrapper(*args, **kwargs):
	logging.debug("I'm returning json!")
	result = method(*args, **kwargs)
	return json.dumps(result)
    return wrapper
# }}

def milli_to_dt(mt):
    """
    Converts UTC in milliseconds (JavaScript time) to a datetime object
    """
    ut = time.gmtime(mt / 1000.0)
    dec = mt / 1000.0
    us = round((dec - math.floor(dec)) * 1000000) # microsecond
    t = ut[:6]
    t += (int(us),)
    return datetime.datetime(*t)

def is_number(i):
    try:
	float(i)
	return True
    except ValueError:
	return False

def hash(password):
    return hashlib.md5(password).hexdigest()

class Register(MethodView):
    def get(self):
	if 'user' in flask.session:
	    return flask.redirect(flask.url_for('index'))
	else: 
	    return flask.render_template('register.html')

    @with_db
    def post(self):
	"""
	Create an account
	"""
	req = ['first_name', 'last_name', 'email', 'username', 'passwd',
	       'passwd2']
	params = {}
	errs = {}
	for r in req:
	    value = flask.request.form.get(r)
	    if not value:
		errs[r] = 'Required'
	    else:
		params[r] = value

	if errs:
	    logging.debug('Missing some registration fields. errs: %s' % errs)
	    return flask.render_template('register.html', errs=errs)

	if params['passwd'] != params['passwd2']:
	    errs['passwd'] = 'Passwords do not match'
	    errs['passwd2'] = ''
	    logging.debug('Passwords do not match')
	    return flask.render_template('register.html', errs=errs)

	rc = flask.g.db.create_user(params['username'], hash(params['passwd']),
		params['email'], params['first_name'], params['last_name'])

	if rc == 3:
	    errs['username'] = 'Username is taken'
	    errs['email'] = 'Email is taken'
	elif rc == 2:
	    errs['email'] = 'Email is taken'
	elif rc == 1:
	    errs['username'] = 'Username is taken'

	if errs:
	    return flask.render_template('register.html', errs=errs)

	flask.session['user'] = params['username']
	return flask.redirect(flask.url_for('index'))

class Login(MethodView):
    def get(self):
	if 'user' in flask.session:
	    return flask.redirect(flask.url_for('index'))
	else:
	    return flask.render_template('login.html')

    @with_db
    def post(self):
	username = flask.request.form.get('username')
	passwd = flask.request.form.get('passwd')
	user = flask.g.db.get_user({'username': username})
	if not user:
	    return flask.render_template('login.html')
	if user['password'] != hash(passwd):
	    return flask.render_template('login.html')
	flask.session['user'] = username
	return flask.redirect(flask.url_for('index'))

class Logout(MethodView):
    decorators = [session]

    def post(self):
	flask.session.pop('user', None)
	return flask.redirect(flask.url_for('index'))

class Index(MethodView):
    def get(self):
	if 'user' not in flask.session:
	    return flask.redirect(flask.url_for('login'))
	else:
	    return flask.render_template('index.html')

class Collector(MethodView):
    decorators = [with_db, json]

    def get(self, point):
	print(point)
	if not point:
	    return 'not point'
	else:
	     return point

    def post(self):
	"""
	date - unix time in milliseconds
	data - free form JSON data
	source - string 
	if source is not registered with contextminer, date is improperly
	formed, or data, date, or source not found in reqeust, returns false, 
	else inserts data and returns true
	"""
	required = set(['data', 'date', 'source'])
	for i in required:
	    if not flask.request.form.get(i):
		return False
	params = flask.request.form
	if not is_number(params['date']):
	    return json.dumps(False)
	rc = flask.g.db.insert_data(milli_to_dt(float(params['date'])),
				    params['source'], params['data'])
	return rc

class Campaigns(MethodView):
    decorators = [with_db, session]

    def get(self, action=None, cid=-1, source=None):
	if action == 'create':
	    return flask.render_template("create_campaign.html", 
			 sources=miners.all_miner_info())
	elif cid != -1 and not source: # a campaign view is requested
	    campaign = flask.g.db.get_campaign(flask.session.get('user'), cid)
	    if not campaign:
		flask.abort(404)
	    tasks = flask.g.db.get_tasks(campaign['_id'])
	    data = flask.g.db.get_data(tasks)
	    return flask.render_template("campaign.html", campaign=campaign, 
					 data=data)
	elif cid != -1 and source: # data from source of campaign is requested
	    campaign = flask.g.db.get_campaign(flask.session.get('user'), cid)
	    if not campaign:
		flask.abort(404)
	    task = flask.g.db.get_campaign_task(source, campaign['_id'])
	    if not task:
		flask.abort(404)
	    data = flask.g.db.get_data([task])
	    # hack to return csv data
	    if flask.request.args.get('fmt') is not None:
		return self.fmt(source, data)
	    else:
		return flask.render_template(source+".html", campaign=campaign, 
					     data=data)
	else:
	    campaigns = flask.g.db.list_campaigns(flask.session.get('user'))
	    return flask.render_template("campaigns.html", campaigns=campaigns)
    
    def fmt(self, source, data):
	fmt = flask.request.args.get('fmt')
	if fmt == 'csv':
	    miner = miners._load_miner(source)
	    result = miner.to_csv(data)
	    if len(result) > 1:
		return self.zip_response(result)
	    else:
		return self.csv_response(result)
	elif fmt == 'json':
	    return self.json_response(data)
	else:
	    return data

    @csv
    def csv_response(self, data):
	return data[0][1]

    @json
    def json_response(self, data):
	return data

    @zip
    def zip_response(self, files):
	"""
	Expects a list of tuples with the first element as the filename and 
	the second element as the string that represent the file. Zips up all
	the files and returns a zip file response
	"""
	zipstream = io.BytesIO()
	zfile = zipfile.ZipFile(file=zipstream, mode='w')
	for f in files:
	    zfile.writestr(f[0], f[1])
	zfile.close()
	zipstream.seek(0)
	return zipstream.getvalue()

    def post(self, action):
	print flask.request.form
	if action == 'create':
	    return self.create()
	elif action == 'delete':
	    return self.delete()
	else:
	    return flask.abort(404)

    def delete(self):
	"""
	Deletes a campaign
	"""
	cid = int(float(flask.request.form.get('cid')))
	if not isinstance(cid, (int, long)):
	    return flask.abort(503)
	flask.g.db.delete_campaign(cid)
	return flask.redirect(flask.url_for('campaigns'))

    def create(self):
	"""
	Creates a new campaign. Expects sources to be a JSON string. 
	Title and query are strings.
	"""
	sources = miners.all_miner_info()
	print sources
	campaign_req = set(['title'])
	missing = {}
	params = {}
	for r in campaign_req:
	    value = flask.request.form.get(r)
	    if not value:
		missing[r] = 'Required'
	    params[r] = value
#	if missing:	
#	    return flask.render_template("create_campaigns.html", errs=missing)

	# find out if source in request. if so, check if required fields are included
	# and save as a task for this campaign
	tasks = []
	source_req = set(['query', 'frequency'])
	for source in sources:
	    fields = [x.split('_', 1)[1] for x in flask.request.form if x.split('_')[0] == source] 
	    print fields
	    for r in source_req:
		if not r in fields:
		    missing[source+'_'+r] = 'Required'

	    # attributes are not required, but if they're present must
	    # check if source supports the attribute
	    attrs = [x for x in fields if x not in source_req]
	    for attr in attrs:
		if attr not in sources[source]:
		    attrs.remove(attr)

	    if flask.request.form.get(source+'_query') != '': # only create task if query not null
		tasks.append({'name': source, 'query': flask.request.form.get(source+'_query'),
		    'frequency': flask.request.form.get(source+'_frequency'),
		    'attributes': attrs})

	desc = flask.request.form.get('description', '')
	flask.g.db.create_campaign(flask.session.get('user'), params['title'], tasks, description=desc)
	return flask.redirect(flask.url_for('index'))
	
class Users(MethodView):
    decorators = [admin, session, with_db]

    def get(self):
	return flask.render_template("users.html", active="users")

    def post(self):
	pass

class Sources(MethodView):
    decorators = [admin, session, with_db]
    
    def get(self):
	return flask.render_template("sources.html", active="sources")

    def post(self):
	pass

collector_view = Collector.as_view('collector')

app.add_url_rule('/', view_func=Index.as_view('index'), 
		methods=['GET', 'POST'])

app.add_url_rule('/register/', view_func=Register.as_view('register'), 
		methods=['GET', 'POST'])

app.add_url_rule('/login/', view_func=Login.as_view('login'),
		methods=['GET', 'POST'])

app.add_url_rule('/logout/', view_func=Logout.as_view('logout'), 
		methods=['POST'])

app.add_url_rule('/campaigns/', view_func=Campaigns.as_view('campaigns'),
		methods=['GET', 'POST'])

app.add_url_rule('/campaigns/<string:action>/',
	    	view_func=Campaigns.as_view('campaigns'),
		methods=['GET', 'POST'])

app.add_url_rule('/campaigns/<string:action>/<float:cid>/',
	    	view_func=Campaigns.as_view('campaigns'),
		methods=['POST'])

app.add_url_rule('/campaigns/<int:cid>/',
	    	view_func=Campaigns.as_view('campaigns'),
		methods=['GET',])

app.add_url_rule('/campaigns/<int:cid>/<string:source>',
	    	view_func=Campaigns.as_view('campaigns'),
		methods=['GET',])

app.add_url_rule('/users/', view_func=Users.as_view('users'),
		methods=['GET', 'POST'])

app.add_url_rule('/sources/', view_func=Sources.as_view('sources'),
		methods=['GET', 'POST'])

app.add_url_rule('/collector/', defaults={'point' : None},
		view_func=collector_view, methods=['GET',])

app.add_url_rule('/collector/', view_func=collector_view, 
		methods=['POST',])

app.add_url_rule('/collector/<path:point>', view_func=collector_view,
		methods=['GET',])

def main():
    server = WSGIServer(('0.0.0.0', 5000), app)
    try:
	server.serve_forever()
    except KeyboardInterrupt:
	gevent.shutdown()

if __name__=='__main__':
    main()
