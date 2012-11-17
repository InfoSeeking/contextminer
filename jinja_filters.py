# A collection of custom filters for Jinja2 templating

import miners

def humanize(name):
    """
    Returns the human readable form of a miner 
    """
    return miners.get_name(name) 

def format_insights(data):
    """
    Takes raw youtube insights data and returns a dict of the parsed insight
    data
    """
    miner = miners._load_miner('youtube_insights')
    return miner.parse(data)
