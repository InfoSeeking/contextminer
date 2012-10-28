# A collection of custom filters for Jinja2 templating

import miners

def humanize(name):
    """
    Returns the human readable form of a miner 
    """
    return miners.get_name(name) 
