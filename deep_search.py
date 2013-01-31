#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import plurklib

target_user = 1165290	#jerryjcw
target_count = 389

obj = plurklib.login(sys.argv[1])
user_info = obj['user_info']
print 'Login as %s (%s, id=%d, karma=%d)' % (user_info['nick_name'], user_info['display_name'], user_info['id'], user_info['karma'])

offset = ''
offset = plurklib.ctime2iso('Sat, 17 Oct 2009 09:41:19 GMT')
owners = {}
plurks = []

while len(plurks) < target_count:
	obj = plurklib.getUserPlurks(offset, target_user)
	part_owners = obj['plurk_users']
	part_plurks = obj['plurks']
	if len(part_plurks) == 0:
		break

	print 'Read',  len(part_plurks), 'plurks'

	for plurk in part_plurks:
		if plurk['owner_id'] == target_user:
			plurks.append(plurk)
			if len(plurks) >= target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	print 'Last plurk was posted at', offset
	offset = plurklib.ctime2iso(offset)

#search
for plurk in plurks:
	print plurk['plurk_id'], plurk['content_raw'].encode('utf-8')
	obj = plurklib.getResponse(plurk['plurk_id'])
	owners.update(obj['friends'])
	responses = obj['responses']
	for response in responses:
		user_id = response['user_id']
		user_id_str = str(user_id)
		if not owners.has_key(user_id_str):
			obj = plurklib.getPublicProfile(user_id)
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
