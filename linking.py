import os
import urllib.parse as urlparse
import urllib.request as request

from telegraph.upload import upload_file


def is_valid_url(link):
	return is_ebay(link) or is_aliexpress(link) or is_zipy(link)


def is_ebay(link):
	return 'ebay.com' in link


def is_aliexpress(link):
	return 'aliexpress.com' in link


def is_zipy(link):
	return 'zipy.co.il' in link


def expand_link(link):
	return request.urlopen(link).url


def telegraph_link_media(media):
	return 'https://telegra.ph/{}'.format(upload_file(media)[0])


# get the product id from ebay
def prod_id_from_ebay(link):
	return os.path.splitext(os.path.basename(urlparse.urlparse(link).path))[0]


def prod_id_from_ali(link):
	plink = os.path.splitext(os.path.basename(urlparse.urlparse(link).path))[0]
	idx = plink.find('_')
	return plink[idx + 1:]


def zipy_prod_by_id(source, pid):
	return 'www.zipy.co.il/p/' + source + '/-/' + str(pid)


def zipy_link_tokenize(link, token):
	
	qdx = link.find('?')
	if qdx != -1:
		link = link[:qdx]
	hdx = link.find('#')
	if hdx != -1:
		link = link[:hdx]
	
	link += '/#' + token
	return link


def tokenize_link(link, token):
	if is_ebay(link):
		pid = prod_id_from_ebay(link)
		link = zipy_prod_by_id('ebay', pid)
	elif is_aliexpress(link):
		pid = prod_id_from_ali(link)
		link = zipy_prod_by_id('aliexpress', pid)
	
	link = zipy_link_tokenize(link, token)
	return link
