import utils
import numpy as np

developer_fee = [0.1, 'yk12953']


senders = {
	'ykaner': [0.4, 'yk12953'],
	'NoamH': [0.9, '2'],
	'rotemsd': [0.9, '10'],
	'ohad1': [0.24, 'yk12953'],
	'duperyuyu': [0.7, 'duper'],
	'@IBA10': [0.5, 'buying']
}


owners = {
	'NoamH': [0.5, '2'],
	'rotemsd': [0.5, '10']
}


def choose_token(sender):
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
	# elif utils.in_chance(owners['NoamH'][0]):
	# 	token = owners['NoamH'][1]
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
