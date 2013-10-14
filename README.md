ContextMiner - Personal Version
===============================

Compatibility: Mac OS X, Linux

Installing ContextMiner
-----------------------
1. Unzip the downloaded file.
2. Make sure you're connected to the Internet.
2. Open a terminal (on a Mac, it's Applications->Utilities->Terminal).
3. Go to the location where you unzipped ContextMiner. Type the following command and hit enter.  
sudo bash install_cm

It will ask for your administrative/root password.  
This may take a few minutes since it's downloading a bunch of dependencies.


Running ContextMiner
--------------------
1. Open a terminal (on a Mac, it's Applications->Utilities->Terminal).  
2. Type the following command at the terminal and hit enter.  
sudo cmstart
3. Open a Web browser and go to localhost:5000.
4. To stop ContextMiner running, type the following command at the terminal and hit enter.  
sudo cmstop  

You will not loose any data if you stop ContextMiner. It simply disables the access to it through the Web browser.


Using ContextMiner
------------------
1. At 'localhost:5000' location in your Web browser, you will see the front-end of ContextMiner. If this is the first time you are using it, you will have to create an account.
2. Once you have created an account, login.
3. Now you can create a new campiagn/project. Within each campaign, you can enter queries to run automatically on YouTube or Facebook. You will also find options to monitor the data being collected and export it in CSV format.


Updating ContextMiner
---------------------
1. Open a terminal (on a Mac, it's Applications->Utilities->Terminal).
2. Make sure you stop ContextMiner if it is running by issuing 'sudo cmstop' on the command-line/terminal.
3. Type the following command and hit enter.  
sudo bash update_cm  

If there are any updates, they will be downloaded automatically and installed at appropriate locations.


Uninstalling ContextMiner
-------------------------
1. Open a terminal (on a Mac, it's Applications->Utilities->Terminal).  
2. Type the following command and hit enter.  
sudo bash uninstall_cm  


ContextMiner Team  
March 20, 2013  
http://www.contextminer.org/
