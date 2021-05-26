"""
WSGI config for fyp_k00232104 project. It exposes the WSGI callable as a module-level variable named ``application``.
For more information on this file, see https://docs.djangoproject.com/en/3.1/howto/deployment/wsgi/

WSGI stands for “Web Server Gateway Interface”. It is used to forward requests from a web server 
(such as Apache or NGINX) to a backend Python web application or framework. 
From there, responses are then passed back to the web server to reply to the requester.
Requests are sent from the client’s browser to the server. WSGI forwards the request to the web server python buyFormController,
which then returns the completed request back to the web server and on to the browser.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'fyp_k00232104.settings')

application = get_wsgi_application()
