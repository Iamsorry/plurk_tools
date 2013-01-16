#!/usr/local/bin/python

# -*- coding: utf-8 -*-

import sys
import urllib, urllib2, cookielib
import json
import time

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode
timezone_offset = 60 * 60 * 8	# CST = GMT +8 hours
api_key = ''
username = ''
password = ''
target_count = 5

def json2obj(jsonstr):
	return json.loads(jsonstr
		.replace('\\u', '#UNI_ESC#')
		.replace('\\', '\\\\')
		.replace('#UNI_ESC#', '\\u')
		.decode('unicode-escape').encode('utf-8')
		.replace(r'\/', '/').replace('\n', ''))

def login(username, password):
	fp = opener.open(get_api_url('/Users/login'),
		encode({'api_key': api_key,
		'username': username,
		'password': password,
		}))
	return json2obj(fp.read())

def getPlurks(time_offset):
	fp = opener.open(get_api_url('/Timeline/getPlurks'),
		encode({'api_key': api_key,
		'limit': '100',
		'offset': time_offset,
		}))
	return json2obj(fp.read())

def getResponse(plurk_id):
	fp = opener.open(get_api_url('/Responses/get'),
		encode({'api_key': api_key,
		'plurk_id': plurk_id,
		}))
	return json2obj(fp.read())

def getPublicProfile(user_id):
	fp = opener.open(get_api_url('/Profile/getPublicProfile'),
		encode({'api_key': api_key,
		'user_id': user_id,
		}))
	return json2obj(fp.read())

def ctime2iso(ctime):
	tm = time.strptime(ctime, '%a, %d %b %Y %H:%M:%S %Z')
	return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(time.mktime(tm)) + timezone_offset))

obj = login(username, password)
user_info = obj['user_info']
print 'Login as %s (%s, id=%d, karma=%d)' % (user_info['nick_name'], user_info['display_name'], user_info['id'], user_info['karma'])

offset = ''
owners = {}
plurks = []

while len(plurks) < target_count:
	obj = getPlurks(offset)
	part_owners = obj['plurk_users']
	part_plurks = obj['plurks']

	for plurk in part_plurks:
		if plurk['owner_id'] == user_info['id']:
			plurks.append(plurk)
			if len(plurks) == target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	offset = ctime2iso(offset)

aggregate = {}
response_count = 0

# aggregate
for plurk in plurks:
	obj = getResponse(plurk['plurk_id'])
	owners.update(obj['friends'])
	responses = obj['responses']
	response_count += len(responses)
	for response in responses:
		user_id = response['user_id']
		if aggregate.has_key(user_id):
			aggregate[user_id] += 1
		else:
			aggregate[user_id] = 1

# sort
summary = aggregate.items()
summary = sorted(((resp_count, user_id) for (user_id, resp_count) in summary), reverse = True)

# output
for (resp_count, user_id) in summary:
	user_id_str = str(user_id)
	if not owners.has_key(user_id_str):
		obj = getPublicProfile(user_id)
		owners.update(obj['user_info'])
	responser = owners[user_id_str]
	display_name = responser.get('display_name', responser['nick_name'])
	if display_name == '':
			display_name = responser['nick_name']
	print ('%d times from %s (%d)' % (resp_count, display_name, user_id)).encode('utf-8')

print 'Total:', response_count, 'responses'
