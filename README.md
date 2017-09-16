# Tiddy-Tides
Small Alexa skill to get the tides of a specific river.  Could be adapted to get the tide of another location or even extended to give the user the option to choose a location.

You can activate the skill (once set up in Amazon developer portal) by saying:

Alexa ask the river when is the next high/low tide  or  Alexa ask the river what its doing

Of simply say Alexa open the river and she will tell you the commands you can use to invoke the skill.

Refer to the scheme for the list of Alexa intents - note some are unused at present.

Dependenices:
Python 3
Beautifulsoup4
flask
flask-ask
datetime
unidecode
requests

Suggest you run this in a virtual env, i.e if the project lives in /var/www/tides then:

cd /var/www/tides
virtualenv tides tidesenv
source tidesenv/bin/activate  (to enter the virtual environment)

Then install the dependencies and check your code runs before deactivating the environment with:

deactivate

If you do not want to run this as a Lambda function on AWS then a good tutorial to follow for setting up your own flask server using nginx is here:

https://www.digitalocean.com/community/tutorials/how-to-serve-flask-applications-with-uwsgi-and-nginx-on-ubuntu-16-04

And here to set up lets encrypt as Amazon expect all end points to have a valid SSL cert  - alternatively use ngrok:

https://gist.github.com/cecilemuller/a26737699a7e70a7093d4dc115915de8

End.

