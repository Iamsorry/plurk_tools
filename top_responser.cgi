#!/usr/local/bin/python
# -*- coding: utf-8 -*-

import cgi
import sys
import urllib, urllib2, cookielib
import json
import time

print 'Content-Type: text/html; charset=utf-8\n\n'
print '<title>Top responsers</title>'

form = cgi.FieldStorage()

opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
get_api_url = lambda x: 'http://www.plurk.com/API%s' % x
encode = urllib.urlencode
timezone_offset = 60 * 60 * 8	# CST = GMT +8 hours
api_key = ''
username = form['username'].value
password = form['password'].value
target_count = 20

now_str = time.strftime('[%Y/%m/%d %H:%M:%S] ', time.localtime())
logfile = open('plurk_topresp.log', 'a')
logfile.write(now_str + username + '\n')
logfile.close()

def json2obj(jsonstr):
	return json.loads(jsonstr
		.replace('\\u', '#UNI_ESC#')
		.replace('\\', '\\\\')
		.replace('#UNI_ESC#', '\\u')
		.decode('unicode-escape').encode('utf-8')
		.replace(r'\/', '/').replace('', ''))

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

def plurkAdd(content, limited_to):
	args = {'content': content,
		'qualifier': 'says',
		'lang': 'tr_ch',
		'api_key': api_key}
	if limited_to == 'me':
		args['limited_to'] = '[' + str(user_info['id']) + ']'
	elif limited_to == 'friends':
		args['limited_to'] = '[0]'
	fp = opener.open(get_api_url('/Timeline/plurkAdd'),
		encode(args))
	return json2obj(fp.read())

def responseAdd(plurk_id, content):
	fp = opener.open(get_api_url('/Responses/responseAdd'),
	encode({'plurk_id': str(plurk_id),
	'content': content,
	'qualifier': 'says',
	'api_key': api_key}))
	return json2obj(fp.read())

def ctime2iso(ctime):
	tm = time.strptime(ctime, '%a, %d %b %Y %H:%M:%S %Z')
	return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(time.mktime(tm)) + timezone_offset))

obj = login(username, password)
user_info = obj['user_info']

print '''
<style type="text/css">
body {
	font-size: 12px;
	font-family: verdana, helvetica, arial, sans-serif;
}
a:link, a:visited {
	color: blue;
	text-decoration: none;
}
a:hover {
	color: blue;
	text-decoration: underline;
}
table#Detail {
	font-size: 12px;
	border-style: solid;
	border-width: 1px;
	border-color: #c3c3c3;
	border-collapse: collapse;
	border-spacing: 1px;
	empty-cells: show;
}
table#Detail th {
	background-color: #cf682f;
	color: white;
}
table#Detail tr:hover {
	background-color: #efefef;
}
</style>
'''

print '<h3>User:', user_info['nick_name'], '</h3>'
print 'Counting within', target_count, 'most recent plurks...<br>'
print '<hr width="50%" align="left">'

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

print '<table border="1" cellpadding="4" cellpadding="3" id="Detail">'
print '<tr><th>User</th><th>Responsed</th><th>Ratio</th></tr>'

# get owner info
for (resp_count, user_id) in summary:
	user_id_str = str(user_id)
	if not owners.has_key(user_id_str):
		obj = getPublicProfile(user_id)
		owners.update(obj['user_info'])

# output chart
charturl = 'http://chart.apis.google.com/chart?'
chart_type = 'p3'
chart_size = '480x160'
chart_data = ''
chart_label = ''
scale_max = 0
other_count = 0

for (resp_count, user_id) in summary:
	user_id_str = str(user_id)
	responser = owners[user_id_str]
	if(resp_count > scale_max):
		scale_max = resp_count
	if(resp_count > 1):
		if(chart_data == ''):
			chart_data = 't:' + str(resp_count)
		else:
			chart_data += ',' + str(resp_count)
		if(chart_label == ''):
			chart_label = responser['nick_name']
		else:
			chart_label += '|' + responser['nick_name']
	else:
		other_count += 1
charturl += 'cht=' + chart_type \
	+ '&chs=' + chart_size \
	+ '&chd=' + chart_data + ',' + str(other_count) \
	+ '&chds=0,' + str(scale_max) \
	+ '&chl=' + chart_label + '|Others'
print '<img src="' + charturl + '"><br><br><br>'

# output table
print 'Detail:<br>'
for (resp_count, user_id) in summary:
	user_id_str = str(user_id)
	responser = owners[user_id_str]
	display_name = responser.get('display_name', responser['nick_name'])
	if display_name == None or display_name == '':
			display_name = responser['nick_name']
	# render avatar
	if responser['has_profile_image'] == 1:
		if  responser['avatar'] == None or responser['avatar'] == 0:
			avatar = 'http://avatars.plurk.com/' + user_id_str + '-small.gif'
		else:
			avatar = 'http://avatars.plurk.com/' + user_id_str + '-small' + str(responser['avatar']) + '.gif'
	else:
		avatar = 'http://www.plurk.com/static/default_small.gif'
	print ('<tr><td><img src="%s"> <a href="http://www.plurk.com/%s">%s</a></td><td align="right">%d</td><td align="right">%.2f%%</td></tr>' %
		(avatar,
		responser['nick_name'],
		display_name,
		resp_count,
		float(100 * resp_count / response_count)
		)).encode('utf-8')

print '</table>'
print 'Total:', response_count, 'responses<br>'
print '<br>'
print 'By <a href="http://www.plurk.com/sorry" target="_blank">@Sorry</a><br>'

# add plurk and response
if 'addplurk' in form and form['addplurk'].value == '1':
	if form['privacy'].value == 'me':
		privacy = 'me'
	elif form['privacy'].value == 'friends':
		privacy = 'friends'
	(resp_count, user_id) = summary[0]
	responser = owners[str(user_id)]
	plurk = plurkAdd('[回噗統計] 第 1 名: @%s (%d 則)' % (responser['nick_name'].encode('utf-8'), resp_count), privacy)

	for i in [1, 2, 3, 4]:
		if i >= len(summary):
			break
		(resp_count, user_id) = summary[i]
		if resp_count < 2:
			break;
		responser = owners[str(user_id)]
		responseAdd(plurk['plurk_id'], '第 %d 名: @%s (%d 則)' % (i + 1,  responser['nick_name'].encode('utf-8'), resp_count))
