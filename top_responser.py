#!/usr/bin/python

# -*- coding: utf-8 -*-

import plurklib

target_count = 5

obj = plurklib.login('account1')
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
		if plurk['owner_id'] == user_info['id']:
			plurks.append(plurk)
			if len(plurks) == target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	offset = plurklib.ctime2iso(offset)

aggregate = {}
response_count = 0

# aggregate
for plurk in plurks:
	obj = plurklib.getResponse(plurk['plurk_id'])
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
		obj = plurklib.getPublicProfile(user_id)
		owners.update(obj['user_info'])
	responser = owners[user_id_str]
	display_name = responser.get('display_name', responser['nick_name'])
	if display_name == '':
			display_name = responser['nick_name']
	print ('%d times from %s (%d)' % (resp_count, display_name, user_id)).encode('utf-8')

print 'Total:', response_count, 'responses'
