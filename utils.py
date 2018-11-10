import os
import random
import re


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
