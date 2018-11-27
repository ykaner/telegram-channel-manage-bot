from functools import wraps

from telegram import ChatAction
from telegram.ext import BaseFilter

import resourses


class FilterCancel(BaseFilter):
	def filter(self, message):
		return message.text == resourses.cancel


filter_cancel = FilterCancel()


def send_action(action):
	"""Sends `action` while processing func command."""
	
	def decorator(func):
		@wraps(func)
		def command_func(*args, **kwargs):
			bot, update = args
			bot.send_chat_action(chat_id=update.message.chat_id, action=action)
			return func(bot, update, **kwargs)
		
		return command_func
	
	return decorator


send_typing_action = send_action(ChatAction.TYPING)


def log(bot, message, to_send=None):
	if to_send is None:
		to_send = '@ilshoppingbotlog'
	bot.send_message(to_send, message)

