# -*- coding: utf-8 -*-
import argparse
import logging
import os

import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, MessageEntity
from telegram.error import (TelegramError, Unauthorized, BadRequest,
                            TimedOut, ChatMigrated, NetworkError)
from telegram.ext import Updater, CommandHandler, ConversationHandler, MessageHandler, Filters

import linking
import resourses
import teleutils
import tokens
import utils
import web_parser

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
	if user.username.lower() not in tokens.senders:
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


def send(bot, user_data, receiver=None, add_buttons=True):
	if receiver is None:
		receiver = to_send_channel
	print('sending to ' + str(receiver))
	if 'short_link' in user_data:
		link = user_data['short_link']
	else:
		link = user_data['link']
	item_link = link
	item_share = 'https://telegram.me/share/url?url=היי!🤠%0aמצאתי%20מוצר%20שאני%20חושב%20שיעניין%20אותך👇%0a' + item_link
	default_shape = [1, 2]
	default_labels = ['🔥✅ ⬅️  להזמנה- לחצו כאן!! ➡️ ✅🔥',
	                  '✳️לשיטוף הערוץ✳️',
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
	
	if mes.chat.type == 'channel':
		utils.log(bot, 'send message from {} to {} with the token {}'.format(user_data['username'], receiver,
		                                                                     user_data['token']))


def timer_send(bot, job):
	ud = job.context
	send(bot, ud, receiver=ud['receiver'])


def send_start(bot, update, user_data):
	user = update.message.from_user
	
	if user.username.lower() not in tokens.senders:
		update.message.reply_text('Sorry, but you have no permission to use this bot')
		return ConversationHandler.END
	
	update.message.reply_text(
			'שלום {}, שלח את המוצר'.format(user.username)
	)
	
	user_data['username'] = '@' + user.username
	
	return DESCRIPTION


def confirmation(bot, update, user_data):
	send(bot, user_data, receiver=update.message.from_user.id, add_buttons=False)
	custom_keyboard = [[resourses.confirm, resourses.cancel], [resourses.timer]]
	reply_keyboard = telegram.ReplyKeyboardMarkup(custom_keyboard)
	return reply_keyboard


def timer_confirmed(bot, update, user_data, job_queue):
	if utils.spell_time(update.message.text) is None:
		update.message.reply_text('הזמן לא מובן, בבקשה כתוב עוד פעם בפורמט הנכון:\n'
		                          'ימים שעות דקות')
		return TIMER
	
	delay_time = utils.spell_time(update.message.text)
	context = user_data.copy()
	context['receiver'] = to_send_channel
	job_queue.run_once(timer_send, delay_time, context=context)
	update.message.reply_text('ההודעה תוזמנה ותישלח בעתיד!', reply_markup=telegram.ReplyKeyboardRemove())
	user_data.clear()
	return ConversationHandler.END


def media_handle(bot, update, user_data, media_id):
	photo_stream = bot.get_file(media_id)
	tmp_media_path = '/tmp/il_shopping_bot'
	utils.create_folder_if_not_exists(tmp_media_path)
	
	tmp_path = os.path.join(tmp_media_path, 'anyf.jpg')
	
	photo_stream.download(tmp_path)
	user_data['photo_link'] = linking.telegraph_link_media(tmp_path)
	os.remove(tmp_path)


@teleutils.send_typing_action
def photo_handle(bot, update, user_data):
	if user_data['username'] != '@duperyuyu':  # duper is fully %^&$&^% so is not allowed to send photo
		if len(update.message.photo) > 0:
			media_id = update.message.photo[-1].file_id
		elif update.message.animation is not None:
			media_id = update.message.animation.file_id
		else:
			media_id = update.message.video.file_id
		media_handle(bot, update, user_data, media_id)
	res = description_logic(update.message.caption, update.message.from_user.username, user_data)
	reply_keyboard = None
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


@teleutils.send_typing_action
def description_handle(bot, update, user_data):
	res = description_logic(update.message.text, update.message.from_user.username, user_data)
	reply_keyboard = None
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
	user_data['token'] = token
	link = linking.tokenize_link(link, token)
	user_data['link'] = link
	short_link = linking.shorten_link(link)
	if short_link != link:
		user_data['short_link'] = short_link
	if 'photo_link' not in user_data:  # photo was not passed so need to get from zipy site
		photo_link = web_parser.telegraph_link_from_zipy_site(link)
		if photo_link is not None:
			user_data['photo_link'] = photo_link
	return CONFIRM, 'יפה, עכשיו נשאר לך רק לאמת ולשלוח!'


@teleutils.send_typing_action
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
	send(bot, user_data)
	update.message.reply_text('ההודעה נשלחה בהצלחה!', reply_markup=telegram.ReplyKeyboardRemove())
	user_data.clear()
	return ConversationHandler.END


def photo_skip_handle(bot, update, user_data):
	link = user_data['link']
	if 'photo_link' in user_data:
		del user_data['photo_link']
	send(bot, user_data)
	
	update.message.reply_text('ההודעה נשלחה בהצלחה!')
	
	user_data.clear()
	return ConversationHandler.END


def cancel(bot, update, user_data):
	update.message.reply_text('בוטל!', reply_markup=telegram.ReplyKeyboardRemove())
	user_data.clear()
	return ConversationHandler.END


def final_choice(bot, update, user_data):
	choice = update.message.text
	if choice == resourses.confirm:
		confirmed(bot, update, user_data)
	elif choice == resourses.cancel:
		cancel(bot, update, user_data)
	elif choice == resourses.timer:
		update.message.reply_text('עוד כמה זמן לשלוח\n הכנס את הפרטים: ימים שעות דקות',
		                          reply_markup=telegram.ReplyKeyboardRemove())
		return TIMER
	return ConversationHandler.END


def error_callback(bot, update, error):
	print(update)
	bot.send_message('@ilsbotdebug', 'error occured\n' + error.message)
	try:
		raise error
	except Unauthorized:
		pass
	# remove update.message.chat_id from conversation list
	except BadRequest:
		pass
	# handle malformed requests - read more below!
	except TimedOut:
		pass
	# handle slow connection problems
	except NetworkError:
		pass
	# handle other connection problems
	except ChatMigrated as e:
		pass
	# the chat_id of a group has changed, use e.new_chat_id instead
	except TelegramError:
		pass
	finally:
		pass


# print(update)
# bot.send_message('@ilsbotdebug', 'finally error occured\n' + error.message)


# states of the conversation
DESCRIPTION, LINK, CONFIRM, TIMER = range(4)


def main():
	parser = argparse.ArgumentParser()
	parser.add_argument('--original', dest='original', action='store_const',
	                    const=True, default=False,
	                    help='is send on the test channel')
	parser.add_argument('--testbot', dest='testbot', action='store_const',
	                    const=True, default=False,
	                    help='is run the program on a test bot')
	args = parser.parse_args()
	print(args.original)
	global to_send_channel
	global bot_api_token
	if not args.original:
		to_send_channel = test_channel_name
	else:
		to_send_channel = original_channel_name
	print(to_send_channel)
	if args.testbot:
		print('using the testbot')
		bot_api_token = '622824179:AAFpF-Jv5eQe8_InpgCMxa2txwdYbdA9koE'
	
	updater = Updater(token=bot_api_token)
	
	dp = updater.dispatcher
	
	# Add conversation handler with the states ...
	conv_handler = ConversationHandler(
			entry_points=[CommandHandler('send', send_start, pass_user_data=True)],
			
			states={
				
				DESCRIPTION: [MessageHandler(Filters.text, description_handle, pass_user_data=True),
				              MessageHandler(Filters.photo | Filters.animation | Filters.video,
				                             photo_handle, pass_user_data=True)],
				
				LINK: [MessageHandler((Filters.text & (Filters.entity(MessageEntity.URL) |
				                                       Filters.entity(MessageEntity.TEXT_LINK))) &
				                      (~ Filters.command),
				                      link_handle, pass_user_data=True),
				       MessageHandler(~ (Filters.command | teleutils.filter_cancel), callback=not_link_handle,
				                      pass_user_data=True)],
				CONFIRM: [MessageHandler(Filters.text, final_choice, pass_user_data=True)],
				TIMER: [MessageHandler(Filters.text, timer_confirmed, pass_user_data=True, pass_job_queue=True)]
			},
			
			fallbacks=[CommandHandler('cancel', cancel, pass_user_data=True),
			           MessageHandler(teleutils.filter_cancel, cancel, pass_user_data=True)]
	)
	
	dp.add_handler(conv_handler)
	dp.add_handler(CommandHandler('start', start_handler))
	dp.add_error_handler(error_callback)
	
	updater.start_polling()
	updater.idle()


if __name__ == '__main__':
	main()
