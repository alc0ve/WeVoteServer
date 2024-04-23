# README for API Installation: 4. Set up Environment

[Back to Install Table of Contents](README_API_INSTALL.md)

[BACK: 3a. Install Python/Django on Mac](README_API_INSTALL_PYTHON_MAC.md)

[BACK: 3b. Install Python/Django on Linux](README_API_INSTALL_PYTHON_LINUX.md)


## Setup - Environment Variables Configuration - WeVoteServer/config/environment_variables.json

NOTE: IMPORTANT STEP

Copy "WeVoteServer/config/environment_variables-template.json" to "WeVoteServer/config/environment_variables.json". 
You will configure many variables for your local environment in this file. 

New variables needed by WeVoteServer will be added to
"environment_variables-template.json" from time to time, so please check for updates by comparing your local version
with the template file.

To start with, enter DATABASE_USER as "postgres" and DATABASE_PASSWORD as whatever you set previously in [step 1b](README_API_INSTALL_POSTGRES_LINUX.md).  
You will also need to set DATABASE_USER_READONLY and DATABASE_PASSWORD_READONLY with the same values.

### LOG_FILE
Create a file on your computer to match the one expected in the environment_variables.json file:

    sudo mkdir /var/log/wevote/
    sudo touch /var/log/wevote/wevoteserver.log
    sudo chmod -R 0777 /var/log/wevote/

As configured in github, only errors get written to the log.
Logging has five levels: CRITICAL, ERROR, INFO, WARN, DEBUG.
It works as a hierarchy (i.e. INFO picks up all messages logged as INFO, ERROR and CRITICAL), and when logging we
specify the level assigned to each message. You can change this to info items by changing the LOG_FILE_LEVEL variable 
in the WeVoteServer/config/environment_variables.json file to "INFO".

## Setup - WeVote Settings - WeVoteServer/wevote_settings/migrations/

Add an empty file named "\_\_init\_\_.py" to "WeVoteServer/wevote_settings/migrations/". You may need to create this directory if it does not exist. 
   
    $ cd ~/PythonProjects/WeVoteServer/
    $ mkdir wevote_settings/migrations/
    $ touch wevote_settings/migrations/__init__.py

You will need to makemigrations and migrate again.

    $ source ~/WeVoteServer3.5/WeVoteServer/bin/activate
    (WeVoteServer) $ python manage.py makemigrations
    (WeVoteServer) $ python manage.py migrate

[NEXT: 5. Set up Database](README_API_INSTALL_SETUP_DATABASE.md)
    
[Working with WeVoteServer day-to-day](README_WORKING_WITH_WE_VOTE_SERVER.md)

[Back to Install Table of Contents](README_API_INSTALL.md)
