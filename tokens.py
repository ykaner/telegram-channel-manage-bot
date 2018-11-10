import utils


developer_fee = [0.1, 'yk12953']


senders = {
	'ykaner': [0.25, 'yk12953'],
	'NoamH': [0.2, '2'],
	'rotemsd': [0.2, '10'],
	'ohad1': [0.2, 'yk12953'],
	'duperyuyu': [0.4, 'duper']
}


owners = {
	'NoamH': [0.5, '2'],
	'rotemsd': [0.5, '10']
}


def choose_token(sender):
	if utils.in_chance(developer_fee[0]):
		token = developer_fee[1]
	elif utils.in_chance(senders[sender][0]):
		token = senders[sender][1]
	elif utils.in_chance(owners['NoamH'][0]):
		token = owners['NoamH'][1]
	else:
		token = owners['rotemsd'][1]
	return token


if __name__ == '__main__':
	# test the statistics
	cnt = {}
	for i in range(10000):
		tok = choose_token('ohad1')
		if tok not in cnt:
			cnt[tok] = 1
		cnt[tok] += 1
	print(cnt)
