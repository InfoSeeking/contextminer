from setuptools import setup

setup(name='contextminer',
      version='0.1.2',
      description='A framework for collecting and analyzing data from social media sources',
      author='Phillip Quiza',
      author_email='pquiza@gmail.com',
      license='MIT',
      packages=['contextminer', 'contextminer.sources'],
      install_requires=[
	  'flask',
	  'pymongo',
	  'beautifulsoup4',
	  'gevent',
	  'supervisor'
      ],
      package_data = {
	'contextminer' : [
	    'supervisor/*', 
	    'templates/*', 
	    'static/css/*',
	    'static/js/*',
	    'static/img/*'
	]
      },
      entry_points={
	'console_scripts' : [
	    'cminit = contextminer.control:init',
	    'cmstart = contextminer.control:start',
	    'cmstop = contextminer.control:stop',
	    'cmweb = contextminer.app:main',
	    'cmminer = contextminer.runner:main',
	]
      },
      zip_safe=False)
