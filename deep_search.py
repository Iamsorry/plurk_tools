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
target_user = 1165290	#jerryjcw
target_count = 389

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

def getPlurks(time_offset, target_user):
	try:
		fp = opener.open(get_api_url('/Timeline/getPublicPlurks'),
			encode({'api_key': api_key,
			'limit': '100',
			'offset': time_offset,
			'user_id': target_user,
			}))
	except:
		return None
	else:
		return json2obj(fp.read())

def getResponse(plurk_id):
	fp = opener.open(get_api_url('/Responses/get'),
		encode({'api_key': api_key,
		'plurk_id': plurk_id,
		}))
	return json2obj(fp.read())

def getPublicProfile(user_id):
	try:
		fp = opener.open(get_api_url('/Profile/getPublicProfile'),
			encode({'api_key': api_key,
			'user_id': user_id,
			}))
	except:
		return None
	else:
		return json2obj(fp.read())

def ctime2iso(ctime):
	tm = time.strptime(ctime, '%a, %d %b %Y %H:%M:%S %Z')
	return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(time.mktime(tm)) + timezone_offset))

obj = login(username, password)
user_info = obj['user_info']
print 'Login as %s (%s, id=%d, karma=%d)' % (user_info['nick_name'], user_info['display_name'], user_info['id'], user_info['karma'])

offset = ''
offset = ctime2iso('Sat, 17 Oct 2009 09:41:19 GMT')
owners = {}
plurks = []

while len(plurks) < target_count:
	obj = getPlurks(offset, target_user)
	part_owners = obj['plurk_users']
	part_plurks = obj['plurks']

	print 'Read',  len(part_plurks), 'plurks'

	for plurk in part_plurks:
		if plurk['owner_id'] == target_user:
			plurks.append(plurk)
			if len(plurks) >= target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	print 'Last plurk was posted at', offset
	offset = ctime2iso(offset)

#search
for plurk in plurks:
	print plurk['plurk_id'], plurk['content_raw'].encode('utf-8')
	obj = getResponse(plurk['plurk_id'])
	owners.update(obj['friends'])
	responses = obj['responses']
	for response in responses:
		user_id = response['user_id']
		user_id_str = str(user_id)
		if not owners.has_key(user_id_str):
			obj = getPublicProfile(user_id)
			if obj is not None:
				owners.update(obj['user_info'])
		if owners.has_key(user_id_str):
			responser = owners[user_id_str]
			display_name = responser.get('display_name', responser['nick_name'])
			if display_name is None or display_name == '':
				display_name = responser['nick_name']
		else:
			display_name = user_id_str
		print (('\t%s: %s') % (display_name, response['content_raw'])).encode('utf-8')
		if responser['nick_name'] == 'iKKBOX':
			print '^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^'
