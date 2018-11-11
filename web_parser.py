import urllib.request
from html.parser import HTMLParser
import utils
import os
import linking


class ZipyParser(HTMLParser):
	def __init__(self):
		self.image_link = None
		HTMLParser.__init__(self)
	
	def handle_starttag(self, tag, attrs):
		if tag == 'img':
			src = ''
			alt = False
			for attr in attrs:
				if attr[0] == 'src':
					src = attr[1]
				if attr[0] == 'alt' and attr[1] == 'gallery image':
					alt = True
					break
			if alt:
				self.image_link = src


chunck_size = 32 * 1024


def telegraph_link_from_zipy_site(link):
	parser = ZipyParser()
	resp = urllib.request.urlopen(link)
	parser.feed(resp.read().decode('utf-8'))
	# while not parser.image_link:
	# 	chunck = resp.read(chunck_size)
	# 	parser.feed(chunck.decode('utf-8'))
	
	image_link = parser.image_link
	if image_link is None:
		print('image not found')
	img_resp = urllib.request.urlopen(image_link)
	tmp_media_path = '/tmp/il_shopping_bot'
	utils.create_folder_if_not_exists(tmp_media_path)
	tmp_path = os.path.join(tmp_media_path, 'anyf.jpg')
	
	image_down = img_resp.read()
	with open(tmp_path, 'wb') as f:
		f.write(image_down)
	photo_link = linking.telegraph_link_media(tmp_path)
	os.remove(tmp_path)
	return photo_link

