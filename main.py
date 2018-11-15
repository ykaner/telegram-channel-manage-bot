# -*- coding: utf-8 -*-
import logging
import os

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters
import argparse
import web_parser

import linking
import tokens
import utils

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

with open('bot_api_token.secret', 'r') as f:
	bot_api_token = f.read()
	bot_api_token = bot_api_token.replace('\n', '')

original_channel_name = '@IsraelShopping'
test_channel_name = '@ilshoppingt'
to_send_channel = test_channel_name


def start_handler(bot, update):
	user = update.message.from_user
	if user.username not in tokens.senders:
		update.message.reply_text('Sorry, but you have no permission to use this bot')
		return
	
	welcome_message = 'שלום וברוכים הבאים לבוט הניהול של ערוץ המכירות הטוב בעולם!!(או בישראל)!'
	update.message.reply_text(welcome_message)
	update.message.reply_text('מחכה להודעה חדשה בשביל הערוץ')


def build_menu(link_labels, shape=None):
	if shape is None:
		shape = []
	
	button_list = []
	for link, label in link_labels:
		button_list.append(InlineKeyboardButton(label, url=link))
	
	if len(button_list) < sum(shape):
		s = 0
		last = len(shape)
		for i, cur_len in enumerate(shape):
			s += cur_len
			if s > len(button_list):
				dif = s - len(button_list)
				shape[i] -= dif
				last = i + 1
				break
		shape = shape[:last]
	elif len(button_list) > sum(shape):
		dif = len(button_list) - sum(shape)
		for i in range(dif):
			shape.append(1)
	
	the_menu = []
	button_it = iter(button_list)
	for cur_len in shape:
		the_menu.append([])
		for i in range(cur_len):
			the_menu[-1].append(next(button_it))
	
	reply_markup = InlineKeyboardMarkup(the_menu)
	return reply_markup


def send(bot, link, user_data, receiver=to_send_channel, add_buttons=True):
	print('sending')
	item_link = link
	item_share = 'https://telegram.me/share/url?url=היי!🤠%0aמצאתי%20מוצר%20שאני%20חושב%20שיעניין%20אותך👇%0a' + item_link
	default_shape = [1, 2]
	default_labels = ['🔥✅ ⬅️  להזמנה- לחצו כאן!! ➡️ ✅🔥',
	                  '🌐לשיתוף הערוץ🌐',
	                  '🔗לשיתוף המוצר🔗']
	links = [item_link,
	         'https://telegram.me/share/url?url=%D7%94%D7%99%D7%99!%F0%9F%A4%A0%0A%20%0A%D7%A8%D7%A6%D7%99%D7%AA%D7%99%20%D7%9C%D7%A9%D7%AA%D7%A3%20%D7%90%D7%95%D7%AA%D7%9A%20%D7%91%D7%A2%D7%A8%D7%95%D7%A5%20%D7%9E%D7%92%D7%A0%D7%99%D7%91%20%D7%A2%D7%9D%20%D7%9E%D7%95%D7%A6%D7%A8%D7%99%D7%9D%20%D7%96%D7%95%D7%9C%D7%99%D7%9D%20%D7%95%D7%90%D7%99%D7%9B%D7%95%D7%AA%D7%99%D7%99%D7%9D%20%D7%9E%D7%97%D7%95%22%D7%9C%F0%9F%94%A5%F0%9F%98%8D%0A%20%0A%D7%9C%D7%94%D7%A6%D7%98%D7%A8%D7%A4%D7%95%D7%AA%20%D7%9C%D7%A2%D7%A8%D7%95%D7%A5%20%D7%98%D7%9C%D7%92%D7%A8%D7%9D%F0%9F%91%87%0Ahttps://t.me/IsraelShopping%0A%20%0A%D7%9C%D7%94%D7%A6%D7%98%D7%A8%D7%A4%D7%95%D7%AA%20%D7%9C%D7%A7%D7%91%D7%95%D7%A6%D7%AA%20%D7%95%D7%95%D7%90%D7%A6%D7%90%D7%A4%F0%9F%91%87%0AHttp://rebrand.ly/WhatsApp-IsraelShopping',
	         item_share]
	if 'photo_link' in user_data:
		text_to_send = '<a href="' + user_data['photo_link'] + '">&#8205;</a>' + user_data['desc']
	else:
		text_to_send = user_data['desc']
	if add_buttons:
		menu_markup = build_menu(zip(links, default_labels), default_shape)
	else:
		menu_markup = None
	mes = bot.send_message(receiver,
	                       text_to_send,
	                       reply_markup=menu_markup,
	                       parse_mode='HTML')


def send_start(bot, update):
	user = update.message.from_user
	
	if user.username not in tokens.senders:
		update.message.reply_text('Sorry, but you have no permission to use this bot')
		return ConversationHandler.END
	
	update.message.reply_text(
			'שלום {}, שלח את המוצר'.format(user.username)
	)
	return DESCRIPTION


def confirmation(bot, update, user_data):
	send(bot, user_data['link'], user_data, receiver=update.message.from_user.id, add_buttons=False)
	custom_keyboard = [['אישור', 'ביטול']]
	reply_keyboard = telegram.ReplyKeyboardMarkup(custom_keyboard)
	return reply_keyboard


def media_handle(bot, update, user_data, media_id):
	photo_stream = bot.get_file(media_id)
	tmp_media_path = '/tmp/il_shopping_bot'
	utils.create_folder_if_not_exists(tmp_media_path)
	
	tmp_path = os.path.join(tmp_media_path, 'anyf.jpg')
	
	photo_stream.download(tmp_path)
	user_data['photo_link'] = linking.telegraph_link_media(tmp_path)
	os.remove(tmp_path)


def photo_handle(bot, update, user_data):
	if len(update.message.photo) > 0:
		media_id = update.message.photo[-1].file_id
	elif update.message.animation is not None:
		media_id = update.message.animation.file_id
	else:
		media_id = update.message.video.file_id
	media_handle(bot, update, user_data, media_id)
	res = description_logic(update.message.caption, update.message.from_user.username, user_data)
	if res[0] == CONFIRM:
		reply_keyboard = confirmation(bot, update, user_data)
	if res[1] is not None and res[1] != '':
		update.message.reply_text(res[1], reply_markup=reply_keyboard)
	return res[0]


def description_logic(text, username, user_data):
	link_idx = utils.where_is_link(text)
	if not link_idx:
		user_data['desc'] = text
		response = 'אוקי, עכשיו שלח את הקישור למוצר'
		return LINK, response
	if link_idx and -1 not in link_idx:
		link_start = link_idx[0]
		link_end = link_idx[1]
		the_link = text[link_start: link_end]
		user_data['desc'] = text[:link_start] + ' ' + text[link_end:]
		res = link_logic(the_link, username, user_data)
		return res


def description_handle(bot, update, user_data):
	res = description_logic(update.message.text, update.message.from_user.username, user_data)
	if res[0] == CONFIRM:
		reply_keyboard = confirmation(bot, update, user_data)
	if res[1] is not None and res[1] != '':
		update.message.reply_text(res[1], reply_markup=reply_keyboard)
	return res[0]


def link_logic(link, username, user_data):
	link = linking.expand_link(link)

	if not linking.is_valid_url(link):
		response = 'הקישור לא חוקי, הזן קישור עוד פעם. (רק את הקישור החדש)'
		return LINK, response

	token = tokens.choose_token(username)
	link = linking.tokenize_link(link, token)
	user_data['link'] = link
	if 'photo_link' not in user_data:  # photo was not passed so need to get from zipy site
		user_data['photo_link'] = web_parser.telegraph_link_from_zipy_site(link)
	return CONFIRM, 'יפה, עכשיו נשאר לך רק לאמת ולשלוח!'


def link_handle(bot, update, user_data):
	link = update.message.text
	username = update.message.from_user.username
	
	res = link_logic(link, username, user_data)
	reply_keyboard = None
	if res[0] == CONFIRM:
		reply_keyboard = confirmation(bot, update, user_data)
	if res[1] is not None and res[1] != '':
		update.message.reply_text(res[1], reply_markup=reply_keyboard)

	return res[0]


def not_link_handle(bot, update, user_data):
	update.message.reply_text('הקישור לא חוקי, הזן קישור עוד פעם. ')
	return LINK


def confirmed(bot, update, user_data):
	link = user_data['link']
	send(bot, link, user_data)
	update.message.reply_text('ההודעה נשלחה בהצלחה!', reply_markup=telegram.ReplyKeyboardRemove())
	user_data.clear()
	return ConversationHandler.END


def photo_skip_handle(bot, update, user_data):
	link = user_data['link']
	if 'photo_link' in user_data:
		del user_data['photo_link']
	send(bot, link, user_data)
	
	update.message.reply_text('ההודעה נשלחה בהצלחה!')
	
	user_data.clear()
	return ConversationHandler.END


def cancel(bot, update, user_data):
	update.message.reply_text('בוטל!', reply_markup=telegram.ReplyKeyboardRemove())
	user_data.clear()
	return ConversationHandler.END


def final_choice(bot, update, user_data):
	choice = update.message.text
	if choice == 'אישור':
		confirmed(bot, update, user_data)
	elif choice == 'ביטול':
		cancel(bot, update, user_data)
	return ConversationHandler.END


# states of the conversation
DESCRIPTION, LINK, CONFIRM = range(3)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--original', dest='original', action='store_const',
	                    const=True, default=False,
	                    help='is send on the test channel')
	args = parser.parse_args()
	global to_send_channel
	if not args.original:
		to_send_channel = test_channel_name
	else:
		to_send_channel = original_channel_name
	
	updater = Updater(token=bot_api_token)
	
	dp = updater.dispatcher
	
	# Add conversation handler with the states ...
	conv_handler = ConversationHandler(
			entry_points=[CommandHandler('send', send_start, pass_user_data=False)],
			
			states={
				DESCRIPTION: [MessageHandler(Filters.text, description_handle, pass_user_data=True),
				              MessageHandler(Filters.photo | Filters.animation | Filters.video,
				                             photo_handle, pass_user_data=True)],
				
				LINK: [MessageHandler(Filters.text & (Filters.entity(MessageEntity.URL) |
				                                      Filters.entity(MessageEntity.TEXT_LINK)),
				                      link_handle, pass_user_data=True),
				       MessageHandler(Filters.all, callback=not_link_handle, pass_user_data=True)],
				CONFIRM: [MessageHandler(Filters.text, final_choice, pass_user_data=True)]
			},
			
			fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True)]
	)
	
	dp.add_handler(conv_handler)
	dp.add_handler(CommandHandler('start', start_handler))
	
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()
