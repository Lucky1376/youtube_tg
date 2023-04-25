from pyrogram import types

# Клавитура для отмены действий
def no_kb(text="no", title="❌Действие не задано❌"):
	return types.InlineKeyboardMarkup(
									      [
									      	[
									          	types.InlineKeyboardButton(text=title, callback_data=text)
									      	]
									      ]
									  )

def url_kb(text="", title=""):
	return types.InlineKeyboardMarkup(
									      [
									      	[
									          	types.InlineKeyboardButton(text=title, url=text)
									      	]
									      ]
									  )