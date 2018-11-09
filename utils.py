import random
import os


def in_chance(prob):
	return (random.random() + prob) > 1


def create_folder_if_not_exists(path):
	if os.path.exists(path):
		return
	create_folder_if_not_exists(os.path.dirname(path))
	os.mkdir(path)

