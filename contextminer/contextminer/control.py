#!/usr/bin/env python

import gevent
import os
import pkg_resources
import re
import signal
import subprocess
import sys
from subprocess import call
from contextminer.app import main as app
from contextminer.runner import main as runner

def get_conf():
    """
    Returns the full path to the conf file for supervisord
    """
    return pkg_resources.resource_filename(
	    'contextminer', 
	    'supervisor/supervisor.conf'
    ) 

def print_out(f):
    for i in f:
	print(i)

def exists(f):
    return os.path.exists(f)

def touch(path):
    with open(path, 'w') as f:
	f.write('')

def mkdir(path):
    os.mkdir(path)

def is_running(process):
    s = subprocess.Popen(["ps", "axw"],stdout=subprocess.PIPE)
    for x in s.stdout:
	if re.search(process, x):
	    return True
    return False

def init():
    files = (
	('/var/log/supervisor', 'd'),
	('/var/log/supervisor/supervisor.log', 'f'),
	('/var/run/supervisord.pid', 'f'),
	('/var/log/contextminer', 'd'),
	('/var/log/contextminer/web.log', 'f'),
	('/var/log/contextminer/miner.log', 'f'),
	('/data', 'd'),
	('/data/log', 'f')
    )

    for f in files:
	if not exists(f[0]):
	    if f[1] == 'f':
		print('creating %s' % f[0])
		touch(f[0])
	    elif f[1] == 'd':
		print('creating %s' % f[0])
		mkdir(f[0])

def start():
    started = False
    conf = get_conf()
    if not is_running('mongod'):
	print('starting mongodb...')
	rc = call(['mongod', '--rest', '--dbpath', '/data', '--logpath', '/data/log', '--fork'])
	if rc != 0:
	    print("failed to start mongodb")
	    sys.exit(1)

    if not is_running('supervisord'):
	print('starting supervisord...')
	rc = call(['supervisord', '-c', conf])
	if rc != 0:
	    print("failed to start supervisord")
	    sys.exit(1)
	started = True

    if not started: 
	print('starting web interface...')
	web = subprocess.Popen(['supervisorctl', '-c', conf, 'start', 'cm_web'], stdout=subprocess.PIPE)
	print_out(web.stdout)
	web.communicate()

	print('starting miners...')
	miner = subprocess.Popen(['supervisorctl', '-c', conf, 'start', 'cm_miner'], stdout=subprocess.PIPE)
	print_out(miner.stdout)
	miner.communicate()

    print('contextminer has started')
    return

def stop():
    conf = get_conf()
    web = subprocess.Popen(['supervisorctl', '-c', conf, 'stop', 'cm_web'])
    web.communicate()
    miner = subprocess.Popen(['supervisorctl', '-c', conf, 'stop', 'cm_miner'])
    miner.communicate()

def main():
    start()

if __name__ == '__main__':
    main()
