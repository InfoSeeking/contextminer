import imp
import os
import logging
import pkg_resources

class MinerError(Exception): pass
class MinerNotFound(MinerError): pass

sourcedir = './sources/'

logging.basicConfig(level=logging.DEBUG)

def get_source_dir():
    """
    Returns the real sources directory
    """
    return pkg_resources.resource_filename(
	    'contextminer',
	    'sources'
    )

def _load_miner(source):
    """
    Given the filename of the source, loads and returns the miner 
    """
    package = 'contextminer.sources'
    try: 
	return getattr(__import__(package, fromlist=[str(source)]), source)
    except ValueError as e:
	logging.debug(e)
	raise MinerNotFound("A miner could not be found for %s" % source)

#    try:
#	return imp.load_source(source, sourcedir+source+".py")
#    except IOError:
#	raise MinerNotFound("A miner could not be found for %s" % source)
#

def miner_exists(source):
    """
    Returns true if a miner exists for a given source, else returns False
    """
    try:
	_load_miner(source)
	return True
    except MinerNotFound:
	return False

def list_miners():
    """
    Returns a list of all miners
    """
    miners = []
    logging.debug(get_source_dir())
    for f in os.listdir(get_source_dir()):
	name = f.split('.')
	if name[0] != '__init__' and name[-1] == 'py':
	    miners.append(name[0])
    return miners

def get_attrs(source):
    """
    Returns a list of attributes that is possible to gather for given source
    """
    miner = _load_miner(source)
    return miner.list_attrs()

def get_name(source):
    """
    Returns the human readable name of a given source
    """
    miner =  _load_miner(source)
    return miner.name()

def all_miner_info(human_readable=False):
    """
    Convenience function to list all miners and their attributes
    if human_readable == True, then keys are human readable names of miners,
    else, keys are machine readable names of miners.
    """
    miners = list_miners()
    logging.debug(miners)
    res = {}
    for m in miners:
	miner = _load_miner(m)
	attrs = miner.list_attrs()
	if human_readable:
	    name = miner.name()
	else:
	    name = m
	res[name] = attrs
    return res

def mine(source, query, since=None, attrs=[]):
    """
    Mines source for given query and returns results
    """
    miner = _load_miner(source)
    return miner.run(query, attrs=attrs, since=since)
