== Installing ContextMiner ==

Mac OSX
-------

## Installing the Prerequisites:
Open Terminal.app and type in the following commands:
ruby -e "$(curl -fsSkL raw.github.com/mxcl/homebrew/go)"
brew install mongodb
brew install libevent
sudo easy_install pip

## Installing ContextMiner:
sudo pip install contextminer 
You should now have three commands available: cminit, cmstart, cmstop

If you do not have these commands, install the client with easy_install:
sudo easy_install supervisor
sudo easy_install contextminer

And remove the previous installation with:
sudo pip uninstall contextminer

Now you can run cminit once to initialize the database. After that when ever you want to start CM just run cmstart. If you want to stop CM, run cmstop. 


Linux (Ubuntu/Debian)
---------------------

## Installing the Prerequisites:
sudo apt-get install mongodb
sudo apt-get install python-dev
sudo apt-get install python-setuptools
sudo apt-get install libevent
sudo apt-get install libevent-dev
sudo easy_install pip

## Installing ContextMiner:
sudo pip install contextminer 
You should now have three commands available: cminit, cmstart, cmstop

If you do not have these commands, install the client with easy_install:
sudo easy_install supervisor
sudo easy_install contextminer

And remove the previous installation with:
sudo pip uninstall contextminer

Now you can run cminit once to initialize the database. After that when ever you want to start CM just run cmstart. If you want to stop CM, run cmstop. 


== Using ContextMiner == 

After you start CM with cmstart, open up a web browser and navigate to http://localhost:5000. This is the web interface for CM. Here you can create campaigns and view the data each campaign has collected.
