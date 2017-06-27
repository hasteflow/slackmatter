Slackmatter - mattermost to slack messages
==========================================

What is this?
-------------

This is a small python script that pushes messages from configured Mattermost channels to Slack.


How does it work?
-----------------

The script checks for new Mattermost messages and send them to Slack. It uses a file named 'timestamps.txt' where it stores timestamps for last messages. 


Installing and running the script
---------------------------------

Install requirements from 'requirements.txt' with 'pip innstall -r requirements.txt'.

After dependencies are installed, update the settings dict with your credentials and run it with 'python slackmatter.py'.

Issues
------

If you are using this script and found a bug, pull requests are welcomed and much appreciated!

