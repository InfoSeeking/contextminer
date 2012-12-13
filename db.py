import datetime
from pymongo import Connection

class DatabaseError(Exception):
    pass

class Database(object):
    """
    Connection abstraction to mongoDB. Assumes contextminer database is created
    """
    def __init__(self, host, port):
	self.host = host
	self.port = port
	self.conn = Connection(host, port)

    def create_user(self, username, password, email, first_name, last_name):
	"""
	Creates a user with given username and first and last names. If the 
	username is already taken returns 1; if the email is taken, returns 2;
	if the email and username is taken, returns 3; else returns 0.
	"""
	u_cursor = self.conn.contextminer.users.find({'username': username}).limit(1)
	e_cursor = self.conn.contextminer.users.find({'email': email}).limit(1)
	if u_cursor.count() > 0 and e_cursor.count() > 0:
	    return 3
	elif e_cursor.count() > 0:
	    return 2
	elif u_cursor.count() > 0:
	    return 1
	else:
	    self.conn.contextminer.users.insert({'username': username, 
		'name': {'first': first_name, 'last': last_name},
		'password': password,
		'email': email,
		'created': datetime.datetime.now(),
		'num_campaigns': 0
		})
	    return 0 

    def get_user(self, query):
	"""
	Finds and returns one user based on the query
	"""
	cur = self.conn.contextminer.users.find(query)
	if cur.count() <= 0:
	    return None
	else:
	    return cur.next()

    def get_campaign_task(self, source, _id):
	"""
	Given a source name and the _id of a campaign, returns a task embedded
	document from the appropiate campaign or None if no task found
	"""
	campaign = self.conn.contextminer.campaigns.find_one({'_id': _id})
	for task in campaign['tasks']:
	    if task['name'] == source:
		return task
	return None

    def get_task(self, _id):
	"""
	Given the objectid of a task object, returns matching document from 
	tasks collection
	"""
	return self.conn.contextminer.tasks.find_one({'_id': _id})

    def get_tasks(self, _id):
	"""
	Given the object id of a campaign, returns all it's tasks
	"""
	campaign = self.conn.contextminer.campaigns.find_one({'_id': _id})
	return campaign['tasks']

    def create_campaign(self, owner, title, tasks, description=''):
	"""
	Format of tasks: 
	[
	    {
		name: facebook,
		query: swine flue,
		attributes: ['likes', 'shares', 'post']
	    },
	    ...
	]
	"""
	cid = self.conn.contextminer.command('findandmodify', 'users', 
		query={'username': owner}, 
		update={'$inc': {'num_campaigns': 1}}, 
		upsert=True)['value']['num_campaigns']

	_id = self.conn.contextminer.campaigns.insert({
		'cid': cid, 
		'owner': owner, 
		'title': title, 
		'description': description, 
		'created': datetime.datetime.now(), 
		'active': True, 
		'tasks': tasks
		})

	# create a new task for each task; should try to minimize task 
	# creation instead
	for task in tasks:
	    self._add_task(_id, task['query'], task['name'], task['attributes'])

    def _add_task(self, campaign, query, source, attributes):
	task = self.conn.contextminer.tasks.find_one({'query': query, 
					 'source': source})
	if task: #if task already exists, just update with union of attributes
	    self.conn.contextminer.tasks.update({'query': query, 
	     'source': source }, 
	     {'attributes': list(set(task['attributes']) | set(attributes)),
	      '$push': {'campaign': campaign}})
	else: # create task
	    self.conn.contextminer.tasks.insert({'campaign': [campaign], 
			     'query': query,
			     'source': source,
			     'attributes': attributes,
			     'last_run': datetime.datetime(1970, 1, 1, 0, 0)})

    def list_campaigns(self, owner):
	"""
	Returns a list of campaigns for owner without tasks
	"""
	cur = self.conn.contextminer.campaigns.find({'owner': owner}, {'tasks': 0})
	return [entry for entry in cur]
    
    def get_campaign(self, owner, cid):
	"""
	Searches and returns one campaign. If campaign not found returns None
	"""
	cur = self.conn.contextminer.campaigns.find_one({'owner': owner, 'cid': cid})
	return cur

    def get_data(self, tasks):
	"""
	Returns all the data gathered for the given tasks sorted by date
	"""
	result = []
	for task in tasks:
	    cur = self.conn.contextminer.data.find({
		'query': task['query'], 
		'source': task['name']}
		).sort('data', 1)

	    for e in cur:
		result.append(e) 
	return result

    def get_sources(self, _id):
	"""
	Returns a list of all the sources this campaign is mining
	"""
	campaign = self.conn.contextminer.campaigns.find_one({'_id': _id})
	sources = []
	for task in campaign['tasks']:
	    sources.append(task['name'])
	return sources

    def add_job(self, task, time):
	self.conn.contextminer.jobs.insert({'task': task, 'time': time})
	
    def insert_data(self, date, source, query, data):
	"""
	Creates a new entry in the data collection. date must be a datetime 
	object. data is free-form JSON data inside a string. If source is not a
	valid source returns False, else inserts data and returns True.
	"""
	self.conn.contextminer.data.insert({'date': date, 
					    'source': source, 
					    'query': query,
					    'data': data})
	return True

    def find_users(query):
	"""
	Finds a user based on query. query is a dictionary whose key/value pair
	matches an attribute of the user. Attributes can be _id for username, 
	created for datetime created, or name which is a dictionary that can 
	look like {name: {first: 'name'}}, {name: {last: 'name'}} or 
	{name: {first: 'name', last: 'name'}}. Returns all valid users else 
	returns None.
	"""
	pass
    
    def deactivate_campaign(id):
	pass

    def delete_campaign(self, cid):
	"""
	Deletes campaign and all related tasks and jobs
	"""
	campaign = self.conn.contextminer.command('findandmodify', 'campaigns', 
		    query={'cid': cid}, remove=True)['value']

	tasks = self.conn.contextminer.command('findandmodify', 'tasks', 
		    query={'campaign': campaign['_id']}, 
		    update={'$pull': {'campaign': campaign['_id']} })['value']

	# remove task if campaigns array is empty
	self.conn.contextminer.command('findandmodify', 'tasks',
		    query={'campaign': {'$size': 0}},
		    remove=True)

	# may need to remove jobs later. 
	return
    
    def create_source():
	pass

    def delete_source():
	pass

    def find(query):
	"""
	Executes the valid mongoDB query. query is a dictionary
	"""
	pass

