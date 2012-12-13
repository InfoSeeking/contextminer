#!/usr/bin/env python

import gevent
import subprocess
from subprocess import call
from contextminer.app import main as app
from contextminer.runner import main as runner

def init():
    print('creating /data directory')
    call(['mkdir', '/data/'])
    print('creating /data/log file')
    call(['touch', '/data/log'])

def start():
    processes = []
    print('starting mongodb')
    print(subprocess.check_output(['pwd']))
    call(['mongod', '--rest', '--dbpath', './data', '--logpath', './data/log', '--fork'])
    print('starting web interface')
    processes.append(gevent.spawn(app))
    print('starting miners')
    processes.append(gevent.spawn(runner))
    gevent.joinall(processes)

def main():
    start()

if __name__ == '__main__':
    main()
