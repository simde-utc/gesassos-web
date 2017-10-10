# -*- coding: utf-8 -*-

from django.conf import settings
import requests

def _urlJoin(*argv):
	return settings.GINGER_SERVER_URL_V2 + "/".join(argv)

def _makeHeaders():
	return {'Authorization': 'Bearer ' + settings.GINGER_KEY_V2}

def getKeys():
	p = {}
	h = _makeHeaders()
	r = requests.get(_urlJoin("keys"), params = p, headers = h)
	# r.status_code
	# TODO: handle errors !
	return r.json()