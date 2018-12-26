import os
import random
import re
import datetime
import teleutils


def in_chance(prob):
	return (random.random() + prob) > 1


def where_is_link(text):
	match = re.search('(http:\/\/www\.|https:\/\/www\.|http:\/\/|https:\/\/)?'
	          '[a-z0-9]+([\-\.]{1}[a-z0-9]+)*\.[a-z]{2,5}(:[0-9]{1,5})?(\/.*)?', text)
	if match is None:
		return None
	return match.span(0)


def create_folder_if_not_exists(path):
	if os.path.exists(path):
		return
	create_folder_if_not_exists(os.path.dirname(path))
	os.mkdir(path)


def spell_time(time_str):
	match = re.search('\d\s+\d{1,2}\s*[\s:]\s*\d{1,2}', time_str)
	if match is None:
		return None
	time_str = time_str[match.span(0)[0]: match.span(0)[1]]
	day_idx = re.search('\d', time_str).span(0)
	days = time_str[day_idx[0]: day_idx[1]]
	days = int(days)
	
	time_str = time_str[day_idx[1]:]
	h_idx = re.search('\d{1,2}', time_str).span(0)
	hours = time_str[h_idx[0]: h_idx[1]]
	hours = int(hours)
	
	time_str = time_str[h_idx[1]:]
	m_idx = re.search('\d{1,2}', time_str).span(0)
	minutes = time_str[m_idx[0]: m_idx[1]]
	minutes = int(minutes)
	
	return ((days * 24 + hours) * 60 + minutes) * 60


def log(bot, message, to_send=None):
	if to_send is None:
		to_send = '@ilshoppingbotlog'
	
	message = str(datetime.datetime.now()) + ': ' + message
	with open('log.txt', 'a') as f:
		f.write(message + '\n')
	
	teleutils.log(bot, message, to_send)


# if __name__ == '__main__':
# 	log('helo')

