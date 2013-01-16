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
		if plurk['limited_to'] is not None:
			plurks.append(plurk)
			if len(plurks) == target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	offset = ctime2iso(offset)

# dump
for plurk in plurks:
	owner_id_str = str(plurk['owner_id'])
	owner = owners[owner_id_str]
	display_name = owner.get('display_name', owner['nick_name'])
	print ('%s [%s] %s' % (
		display_name,
		plurk['qualifier'],
		plurk['content_raw'])
		).encode('utf-8')
	limited_to = plurk['limited_to']
	if limited_to == '|0|':
		print '\t(all_friends)'
	else:
		guest_list = limited_to.replace('||', '|').split('|')
		for guest_id in guest_list[1:-1]:
			if not owners.has_key(guest_id):
				obj = getPublicProfile(guest_id)
				owners[guest_id] = obj['user_info']
			guest = owners[guest_id]
			display_name = guest.get('display_name', guest['nick_name'])
			if display_name == '':
				display_name = guest['nick_name']
			print '\t' + display_name
