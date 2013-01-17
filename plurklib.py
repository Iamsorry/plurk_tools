#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import os.path
import urllib, urllib2, cookielib
import json
import MultipartPostHandler

cookie_jar = None
session_opener = None
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode
api_key = ''
accounts = {
	'account1': 'password1',
	'account2': 'password2',
	'account3': 'password3',
}

def json2obj(jsonstr):
	return json.loads(jsonstr
		.replace('\\u', '#UNI_ESC#')
		.replace('\\', '\\\\')
		.replace('#UNI_ESC#', '\\u')
		.decode('unicode-escape')
		.replace(r'\/', '/').replace('\n', ''))

def getPlurks(time_offset):
	fp = session_opener.open(get_api_url('/Timeline/getPlurks'),
		encode({'api_key': api_key,
		'limit': '100',
		'offset': time_offset,
		}))
	return json2obj(fp.read())

def getUserPlurks(time_offset, target_user):
	fp = session_opener.open(get_api_url('/Timeline/getPlurks'),
		encode({'api_key': api_key,
		'user_id': target_user,
		'limit': '100',
		'offset': time_offset,
		}))
	return json2obj(fp.read())

def getResponse(plurk_id):
	fp = session_opener.open(get_api_url('/Responses/get'),
		encode({'api_key': api_key,
		'plurk_id': plurk_id,
		}))
	return json2obj(fp.read())

def getPublicProfile(user_id):
	fp = session_opener.open(get_api_url('/Profile/getPublicProfile'),
		encode({'api_key': api_key,
		'user_id': user_id,
		}))
	return json2obj(fp.read())

def getOwnProfile():
	args = {'api_key': api_key}
	fp = session_opener.open(get_api_url('/Profile/getOwnProfile'),
		encode(args))
	return json2obj(fp.read())

def plurkAdd(qualifier, content):
	args = {'qualifier': qualifier,
		'content': content,
		'lang': 'tr_ch',
		'api_key': api_key}
	fp = session_opener.open(get_api_url('/Timeline/plurkAdd'),
		encode(args))
	return json2obj(fp.read())

def responseAdd(plurk_id, qualifier, content):
	args = {'plurk_id': plurk_id,
		'qualifier': qualifier,
		'content': content,
		'api_key': api_key}
	fp = session_opener.open(get_api_url('/Responses/responseAdd'),
		encode(args))
	return json2obj(fp.read())

def uploadPicture(imgp):
	uploader = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar), MultipartPostHandler.MultipartPostHandler)
	args = {'api_key': api_key,
		'image': imgp}
	try:
		fp = uploader.open(get_api_url("/Timeline/uploadPicture"), args)
		obj = json2obj(fp.read())
	except urllib2.HTTPError, error:
		print 'Upload failed: %d - %s' % (error.code, error.read())
		exit()
	return obj

def login(username):
	if not accounts.has_key(username):
		print 'User not defined in plurklib'
		return None

	global cookie_jar
	global session_opener

	cookie_jar = cookielib.LWPCookieJar()
	cookie_file = 'plurk_session.' + username + '.txt'
	if os.path.isfile(cookie_file):
		cookie_jar.load(cookie_file)

	session_opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cookie_jar))
	#urllib2.install_opener(session_opener)

	obj = None
	try:
		obj = getOwnProfile()
	except urllib2.HTTPError, error:
		print 'Cookie auth failed: %d - %s' % (error.code, error.read())
		try:
			fp = session_opener.open(get_api_url('/Users/login'),
				encode({'api_key': api_key,
				'username': username,
				'password': accounts[username],
				#'no_data': '1',
				}))
			obj = json2obj(fp.read())
		except urllib2.HTTPError, error:
			print 'Password auth failed: %d - %s' % (error.code, error.read())
			exit()
		else:
			cookie_jar.save(cookie_file)

	return obj
