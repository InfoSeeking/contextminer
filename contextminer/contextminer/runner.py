import sys
import datetime
from gevent import Greenlet
import gevent
try:
    import simplejson as json
except ImportError:
    import json 
import db
import miners

db_host = 'localhost'
db_port = 27017

def fix_keys(obj):
    """
    Full traversal of dict obj that removes '$' from keys for insertion into 
    mongodb.
    """
    if isinstance(obj, dict):
	keys = obj.keys()
	for key in keys:
	    if isinstance(obj[key], dict):
		fix_keys(obj[key])
	    elif isinstance(obj[key], list):
		obj[key] = map(fix_keys, obj[key])
	    if key.find('$') != -1:
		obj[key.replace('$', '')] = obj.pop(key)
    return obj 

class Runner(Greenlet):
    
    def __init__(self, host, port):
	Greenlet.__init__(self)
	self.db = db.Database(db_host, db_port)

    def _run(self):
	"""
	Main loop for Runner
	"""
	running = []
	while True:
	    job = self.get_job()
	    running.append(gevent.spawn(self.run_job, job['value']))
	    # remove finished tasks
	    for task in running:
		if task.successful:
		    running.remove(task)

    def run_job(self, job):
	"""
	Runs job and inserts result in database
	"""
	task = self.db.get_task(job['task'])	
	exec_time = datetime.datetime.now()
	res = miners.mine(task['source'], task['query'], 
			     attrs=task['attributes'], since=task['last_run'])

	if isinstance(res, list): 
	    res = map(fix_keys, res)
	    for data in res:
		self.db.insert_data(datetime.datetime.now(), task['source'], 
			    task['query'], data)
	else:
	    self.db.insert_data(datetime.datetime.now(), task['source'],
				task['query'], res)
	# update last run time for task
	self.db.conn.contextminer.tasks.update({'_id': task['_id']},
		{'$set': {'last_run': exec_time}})
	return

    def get_job(self, interval=10):
	"""
	Returns a job from contextminer.jobs collection. If there are not jobs
	blocks until one becomes available. interval specifies the interval of
	polling the job queue in seconds.
	"""
	job = {}
	while True:
	    print "polling to get a job"
	    job = self.db.conn.contextminer.command('findAndModify', 
						    'jobs', remove=True)
	    if job.get('value') is not None:
		print "got a job!"
		break
	    gevent.sleep(interval)

	return job

class Scheduler(Greenlet):

    poll_interval = 60 # one minute

    def __init__(self, host, port):
	Greenlet.__init__(self)
	self.db = db.Database(host, port)

    def _run(self):
	while True:
	    print "scheduling!!"
	    cur = self.db.conn.contextminer.tasks.find()	    
	    now = datetime.datetime.now()
	    for task in cur: # assuming all tasks run daily
		if (now - task['last_run']) > datetime.timedelta(days=1):
		    print "found a task!!"
		    self.db.add_job(task['_id'], datetime.datetime.now())
	    gevent.sleep(self.poll_interval)

def main():
    runner = Runner(db_host, db_port)
    runner.start()
    scheduler = Scheduler(db_host, db_port)
    scheduler.start()
    gevent.joinall([runner, scheduler])

if __name__ == "__main__":
    main()
