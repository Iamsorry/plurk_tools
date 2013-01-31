#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys
import plurklib

target_count = 5

obj = plurklib.login(sys.argv[1])
user_info = obj['user_info']
print 'Login as %s (%s, id=%d, karma=%d)' % (user_info['nick_name'], user_info['display_name'], user_info['id'], user_info['karma'])

offset = ''
owners = {}
plurks = []

while len(plurks) < target_count:
	obj = plurklib.getPlurks(offset)
	part_owners = obj['plurk_users']
	part_plurks = obj['plurks']
	if len(part_plurks) == 0:
		break

	for plurk in part_plurks:
		if plurk['limited_to'] is not None:
			plurks.append(plurk)
			if len(plurks) == target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	offset = plurklib.ctime2iso(offset)

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
				obj = plurklib.getPublicProfile(guest_id)
				owners[guest_id] = obj['user_info']
			guest = owners[guest_id]
			display_name = guest.get('display_name', guest['nick_name'])
			if display_name == '':
				display_name = guest['nick_name']
			print '\t' + display_name
