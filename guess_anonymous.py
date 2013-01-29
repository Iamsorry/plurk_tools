#!/usr/bin/python

# -*- coding: utf-8 -*-

import plurklib
import time

timezone_offset = 60 * 60 * 8	# CST = GMT +8 hours
target_count = 5
max_output = 5

def ctime2iso(ctime):
	tm = time.strptime(ctime, '%a, %d %b %Y %H:%M:%S %Z')
	return time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime(int(time.mktime(tm)) + timezone_offset))

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
		if plurk['owner_id'] == 99999:
			plurks.append(plurk)
			if len(plurks) == target_count:
				break

	owners.update(part_owners)

	offset = part_plurks[len(part_plurks)-1]['posted']
	offset = ctime2iso(offset)

# aggregate
for plurk in plurks:
	suspects = {}
	obj = plurklib.getResponse(plurk['plurk_id'])
	owners.update(obj['friends'])
	responses = obj['responses']
	print '%s (%d)' % (plurk['content_raw'].encode('utf-8'), len(responses))
	if len(responses) == 0:
		print '\t' + '(no reponse)'
		continue
	for response in responses:
		user_id = response['user_id']
		if suspects.has_key(user_id):
			suspects[user_id] += 1
		else:
			suspects[user_id] = 1

	ordered = sorted(((v, k) for (k, v) in suspects.items()), reverse = True)
	output = 0
	for (appearance, suspect) in ordered:
		if output > max_output:
			break
		suspect_info = owners[str(suspect)]
		display_name = suspect_info.get('display_name', suspect_info['nick_name'])
		if display_name is None or display_name == '':
			display_name = suspect_info['nick_name']
		#print ('\t%s (%d:%s)' % (display_name, suspect, suspect_info['nick_name'])).encode('utf-8')
		print ('\t%s (%d)' % (display_name, appearance)).encode('utf-8')
		output += 1;
