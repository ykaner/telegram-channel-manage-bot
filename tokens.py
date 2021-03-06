import utils
import numpy as np
import os
import json

developer_fee = [0.12, 'yk12953']


senders = {
	'ykaner': [0.54, 'yk12953'],
	'noamh': [1 - developer_fee[0], '2'],
	'rotemsd': [1 - developer_fee[0], '10'],
	# 'ohad1': [0.26, 'yk12953'],
	'duperyuyu': [0.7, 'duper'],
	'Israel_Ben_Ari': [0.5, 'buying']
}


owners = {
	'noamh': [0.5, '2'],
	'rotemsd': [0.5, '10']
}


token_data_f = 'token_data'
senders_f = 'senders.json'
owners_f = 'owners.json'
utils.create_folder_if_not_exists(token_data_f)
if not os.path.exists(os.path.join(token_data_f, senders_f)):
	with open(os.path.join(token_data_f, senders_f), 'w') as f:
		json.dump(senders, f, indent='\t')
else:
	with open(os.path.join(token_data_f, senders_f), 'r') as f:
		senders = json.load(f)
if not os.path.exists(os.path.join(token_data_f, owners_f)):
	with open(os.path.join(token_data_f, owners_f), 'w') as f:
		json.dump(senders, f, indent='\t')
else:
	with open(os.path.join(token_data_f, owners_f), 'r') as f:
		senders = json.load(f)


def choose_token(sender):
	sender = sender.lower()
	areas = [developer_fee[0],
	         senders[sender][0]]
	area_tokens = ['yk12953', senders[sender][1]]
	free_area = 1 - sum(areas)
	for k in owners:
		areas.append(owners[k][0] * free_area)
		area_tokens.append(owners[k][1])
	assert sum(areas) == 1
	token = np.random.choice(area_tokens, 1, p=areas)[0]
	return token
	

	# the old - tree - way of tokenizing
	# if utils.in_chance(developer_fee[0]):
	# 	token = developer_fee[1]
	# elif utils.in_chance(senders[sender][0]):
	# 	token = senders[sender][1]
	# elif utils.in_chance(owners['noamh'][0]):
	# 	token = owners['noamh'][1]
	# else:
	# 	token = owners['rotemsd'][1]
	# return token


if __name__ == '__main__':
	# test the statistics
	cnt = {}
	for i in range(10000):
		tok = choose_token('duperyuyu')
		if tok not in cnt:
			cnt[tok] = 1
		else:
			cnt[tok] += 1
	print(cnt)
