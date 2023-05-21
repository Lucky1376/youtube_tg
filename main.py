from pyrogram.errors import FloodWait, MessageNotModified
from pyrogram import Client, filters
from pyrogram.types import InlineQueryResultArticle, InputTextMessageContent
from pyrogram import types
from youtubesearchpython import VideosSearch
from pytube import YouTube

from utils import *
from keyboard import *

import config, random, requests, os, time, json

search_data = {}
search_result = {}
th_data = []
video_data = {}

audio_info = {}
video_info = {}

app = Client("youtube", api_id=config.API_ID, api_hash=config.API_HASH, bot_token=config.TOKEN)

@app.on_message(filters.command(["start"], prefixes="/") & filters.private)
def start(client, message):
	id = message.from_user.id
	name = message.from_user.first_name

	client.send_message(id, f"**Привет [{name}](tg://user?id={id})!**\n\n__**Отправь мне ссылку на видео или напиши текст для поиска видео и я выдам тебе результаты!**__", reply_markup=url_kb(text="https://github.com/Lucky1376/youtube_tg", title="Исходный код Бота"))

@app.on_message(filters.text & filters.private)
def txt(client, message):
	global search_data
	global th_data
	global video_data

	id = message.from_user.id
	text = message.text

	if is_youtube_link(text):
		if id in th_data:
			client.send_message(id, "❌**Извините, поток занят**")
			return

		th_data.append(id)
		file_id = f"{message.id}{id}"

		a = client.send_message(id, "🕒**Создаю объект видео...**")

		try:
			proxy = {'http': 'http://pr0xyShopTG:proxysoxybot@45.81.137.174:5500'}

			yt = YouTube(text)
			streams = yt.streams

			a.edit("✅**Объект создан**\n🕒**Скачиваю обложку**")

			download_image(yt.video_id, f"{file_id}.jpg")

			a.edit("✅**Объект создан**\n✅**Обложка скачена**\n🕒**Собираю информацию**")

			itog = {"title": yt.title,
			        "len": yt.length,
			        "date": yt.publish_date,
			        "views": yt.views,
			        "author": yt.author,
			        "author_url": yt.channel_url,
			        "prew": yt.thumbnail_url,
			        "video": [],
			        "audio": []}

			# Собираем все видео
			for video in streams.filter(mime_type="video/mp4"):
				conf = {}

				conf["itag"] = str(video.itag)
				conf["res"] = int(video.resolution[:-1])
				if int(video.resolution[:-1]) > 1080:
					continue
				conf["size"] = video.filesize

				f = True
				for i in itog["video"]:
					if i["res"] == int(video.resolution[:-1]):
						f = False
						break

				if f:
					itog["video"].append(conf)

			itog["video"] = sorted(itog["video"], key=lambda student: student["res"])

			# Собираю информацию о аудио
			for audio in streams.filter(mime_type="audio/mp4"):
				conf = {}

				conf["itag"] = str(audio.itag)
				conf["size"] = audio.filesize
				conf["abr"] = audio.abr

				itog["audio"].append(conf)

			video_data[file_id] = {"url": text, "data": itog, "class": yt, "streams": streams}

			# Составляем клавиатуру и текст
			itog_text = f"👤**[{yt.author}]({yt.channel_url})**\n📹**{yt.title}**\n\n👁️`"+str('{0:,}'.format(yt.views).replace(',', '.'))+"`\n\n"


			# Собираем информацию о качестве видео и сразу клавитурку
			kb = []
			for i in range(20):
				kb.append([])
			what_kb = 0
			for dp in itog["video"]:
				t = ""

				resize = file_resize(dp["size"])
				tt = "**"+str(dp["res"])+f"p** | `{resize}`"
				if dp["size"] >= 2147483648:
					t += f"⛔️{tt}\n"
				else:
					t += f"✅{tt}\n"

				itog_text += t

				if len(kb[what_kb]) == 3:
					what_kb += 1

				kb[what_kb].append(types.InlineKeyboardButton(text="📹"+str(dp["res"])+f"p", callback_data=f"getvideo {file_id} "+dp["itag"]+" "+itog["audio"][-1]["itag"]))

			resize = file_resize(itog["audio"][-1]["size"])
			itog_text += f"\n🎧**MP3 | ** `{resize}`"

			kb[-1].append(types.InlineKeyboardButton(text="🎧MP3", callback_data=f"getaudio {file_id} "+itog["audio"][-1]["itag"]))
			kb[-1].append(types.InlineKeyboardButton(text="🖼", callback_data=f"getprew {file_id}"))
			kb[-1].append(types.InlineKeyboardButton(text="👤", switch_inline_query_current_chat="channel_"+yt.channel_id))

			kb = types.InlineKeyboardMarkup(kb)

			client.send_photo(id, f"{file_id}.jpg", caption=itog_text, reply_markup=kb)
			a.delete()
			os.remove(f"{file_id}.jpg")
		except Exception as e:
			print(e)
			a.edit("❌**Произошел сбой, попробуйте снова**")

		th_data.remove(id)
		try:
			os.remove(f"{file_id}.jpg")
		except:
			pass
	else:
		spec_id = f"{message.id}{id}"
		search_data[spec_id] = text

		client.send_message(id, f"**Текст опредлен как запрос**\n└__{text}__", reply_markup=no_kb(f"search {spec_id}", "🔎Найти"))
		print(search_data)

@app.on_callback_query()
def callbackk(client, message):
	global audio_info
	global video_info
	global search_data
	global th_data
	global video_data

	id = message.from_user.id
	message_id = message.message.id
	text = message.data

	if text.split()[0] == "getprew":
		file_id = text.split()[1]
		if file_id not in video_data:
			client.answer_callback_query(callback_query_id=message.id, text="❌Объект был утерян", show_alert=True)
		else:
			client.answer_callback_query(callback_query_id=message.id, text="🕒Отправляю")
			yt = video_data[file_id]["class"]
			download_image(yt.video_id, f"{file_id}.jpg")
			client.send_document(id, f"{file_id}.jpg", caption="**@orion_youtube_bot**")
			os.remove(f"{file_id}.jpg")



	elif text.split()[0] == "getaudio":
		file_id = text.split()[1]
		if file_id not in video_data:
			client.answer_callback_query(callback_query_id=message.id, text="❌Объект был утерян", show_alert=True)
			return

		elif id in th_data:
			client.answer_callback_query(callback_query_id=message.id, text="❌Поток занят", show_alert=True)
			return

		a = client.send_message(id, "🕒**Ожидайте**")
		th_data.append(id)

		try:
			itag = int(text.split()[2])

			def yt_progress(stream=None, chunk=None, remaining=0):
				file_downloaded = (audio_info[id]["size"] - remaining)
				per = int((file_downloaded / audio_info[id]["size"]) * 100)
					
				bar = progress_bar()
				bar.set(per)
				bar_text = bar.get()

				try:
					audio_info[id]["m"].edit(f"🕒**Скачиваю**\n{bar_text} ~`{per}`**%**")
				except FloodWait as e:
					time.sleep(e.value)
					audio_info[id]["m"].edit(f"🕒**Скачиваю**\n{bar_text} ~`{per}`**%**")

			yt = YouTube(video_data[file_id]["url"], on_progress_callback=yt_progress)
			stream = yt.streams.get_by_itag(itag)
			audio_info[id] = {"size": stream.filesize,
							   "m": a}


			if audio_info[id]["size"] > 31457280:
				a.edit("❌**Размер Аудио слишком велик, я не могу его отправить**")
				th_data.remove(id)
				return

			a.edit("🕒**Скачиваю**\n□□□□□□□□□□ ~`0`**%**")
			
			audio_path = stream.download()

			a.edit("🕒**Конвертация...**")
			os.system(f'ffmpeg -i "{audio_path}" "'+audio_path[:-1]+'3" -y')
			a.edit("🕒**Меняю обложку...**")
			download_image(yt.video_id, f"{file_id}.jpg")
			convert_image(f"{file_id}.jpg")

			def py_progress(current, total, *args):
				per = int((current * 100 / total))

				bar = progress_bar()
				bar.set(per)
				bar_text = bar.get()

				try:
					args[0].edit(f"🕒**Отправляю**\n{bar_text} ~`{per}`**%**")
				except FloodWait as e:
					time.sleep(e.value)
					args[0].edit(f"🕒**Отправляю**\n{bar_text} ~`{per}`**%**")

			a.edit("🕒**Отправляю**\n□□□□□□□□□□ ~`0`**%**")
			client.send_audio(id, audio_path[:-1]+"3", thumb=f"{file_id}.jpg", performer=yt.author, caption=f"**@orion_youtube_bot**", progress=py_progress, progress_args=(a,))
			a.delete()
		except:
			a.edit("❌**Произошел сбой, попробуйте снова**")

		th_data.remove(id)
		hg = [f"{file_id}.jpg", audio_path, audio_path[:-1]+"3"]
		for i in hg:
			try:
				os.remove(i)
			except:
				pass
		clear()



	elif text.split()[0] == "getvideo":
		file_id = text.split()[1]
		if file_id not in video_data:
			client.answer_callback_query(callback_query_id=message.id, text="❌Объект был утерян", show_alert=True)
			return

		elif id in th_data:
			client.answer_callback_query(callback_query_id=message.id, text="❌Поток занят", show_alert=True)
			return

		a = client.send_message(id, "🕒**Ожидайте**")
		th_data.append(id)

		audio_path = ""
		video_path = ""

		#---------------------------------------------

		try:
			itag_vd = int(text.split()[2])
			itag_au = int(text.split()[3])

			def yt_progress(stream=None, chunk=None, remaining=0):
				obj = video_info[id][video_info[id]["what"]]

				file_downloaded = (obj["size"] - remaining)
				per = int((file_downloaded / obj["size"]) * 100)

				symb = obj["symb"]

				bar = progress_bar()
				bar.set(per)
				bar_text = bar.get()
				
				try:
					video_info[id]["m"].edit(f"🕒**Скачиваю {symb}**\n{bar_text} ~`{per}`**%**")
				except FloodWait as e:
					time.sleep(e.value)

			yt = YouTube(video_data[file_id]["url"], on_progress_callback=yt_progress)
			stream_vd = yt.streams.get_by_itag(itag_vd)
			stream_au = yt.streams.get_by_itag(itag_au)

			video_info[id] = {"au": {"size": stream_au.filesize,
									 "symb": "🎧"},
							  "vd": {"size": stream_vd.filesize,
							  		 "symb": "📹"},
							  "m": a,
							  "what": "au"}

			if video_info[id]["vd"]["size"] >= 2147483648:
				a.edit("❌**Размер Видео слишком велик, я не могу его отправить**")
				th_data.remove(id)
				return

			if video_info[id]["au"]["size"] > 576716800:
				a.edit("❌**Размер Аудио слишком велик, я не могу скачать видео**")
				th_data.remove(id)
				return

			# Скачиваем аудио
			a.edit("🕒**Скачиваю 🎧**\n□□□□□□□□□□ ~`0`**%**")

			audio_path = stream_au.download(filename=f"{a.id}{id}")
			a.edit("🕒**Скачиваю 📹**\n□□□□□□□□□□ ~`0`**%**")
			video_info[id]["what"] = "vd"

			video_path = stream_vd.download(filename=f"{message_id}{id}")

			a.edit("🕒**Слияние...**")

			os.system(f'ffmpeg -i "{video_path}" -i {audio_path} -c:v copy -c:a copy "{a.id}{message_id}{id}.mp4" -y')

			a.edit("🕒**Меняю обложку...**")
			result = requests.get(f"https://img.youtube.com/vi/{yt.video_id}/maxresdefault.jpg").content
			with open(f"{file_id}.jpg", "wb") as f:
				f.write(result)
			convert_image_2(f"{file_id}.jpg")

			def py_progress(current, total, *args):
				global bar

				per = (current * 100 / total)
				#per = '{:.1f}'.format(per)
				per = int(per)
				bar = progress_bar()
				bar.set(per)
				bar_text = bar.get()

				try:
					args[0].edit(f"🕒**Отправляю**\n{bar_text} ~`{per}`**%**")
				except FloodWait as e:
					time.sleep(e.value)
				except MessageNotModified:
					pass

			a.edit("🕒**Отправляю**\n□□□□□□□□□□ ~`0`**%**")
			client.send_video(id, f"{a.id}{message_id}{id}.mp4", thumb=f"{file_id}.jpg", caption=f"📹**{yt.title}**\n\n**@orion_youtube_bot**", progress=py_progress, progress_args=(a,))
			a.delete()
		except:
			try:
				a.edit("❌**Произошел сбой, попробуйте снова**")
			except FloodWait as e:
				time.sleep(e)

		hg = [audio_path, video_path, f"{a.id}{message_id}{id}.mp4", f"{file_id}.jpg"]
		for i in hg:
			try:
				os.remove(i)
			except:
				continue
		th_data.remove(id)
		clear()



	elif text.split()[0] == "search":
		if text.split()[1] not in search_data:
			client.answer_callback_query(callback_query_id=message.id, text="❌Запрос был утерян", show_alert=True)
			client.edit_message_reply_markup(chat_id=id, message_id=message_id, reply_markup=None)
			return

		a = client.edit_message_text(id, message_id, "🕒**Загружаю результаты...**", reply_markup=None)

		s_text = search_data[text.split()[1]]
		result = VideosSearch(s_text, limit=50, region='RU').result()["result"]
		if len(result) == 0:
			client.edit_message_text(id, message_id, "❌**Результатов не найдено**", reply_markup=None)
			return

		s_id = f"{message.id}{id}"
		search_result[s_id] = result

		title = result[0]["title"]
		url = result[0]["link"]
		v_id = result[0]["id"]
		channel = result[0]["channel"]["name"]

		# Скачиваю первую обложку
		image = download_image(v_id, s_id)

		kb = [[types.InlineKeyboardButton(text="📤", switch_inline_query_current_chat=f"sdownload|{s_id}|{v_id}|0")]]

		if len(result) > 1:
			kb[0].append(types.InlineKeyboardButton(text="➡️", callback_data=f"sresult {s_id} 1 right"))

		kb = types.InlineKeyboardMarkup(kb)

		client.send_photo(id, image, caption=f"📹**{title}**\n👤**{channel}**\n\n🔗**[URL]({url})**", reply_markup=kb)

		a.delete()
		os.remove(image)



	elif text.split()[0] == "sresult":
		s_id = text.split()[1]
		n = int(text.split()[2])
		what = text.split()[3]

		if s_id not in search_result:
			client.answer_callback_query(callback_query_id=message.id, text="❌Запрос был утерян", show_alert=True)
			client.edit_message_reply_markup(chat_id=id, message_id=message_id, reply_markup=None)
			return

		title = search_result[s_id][n]["title"]
		url = search_result[s_id][n]["link"]
		v_id = search_result[s_id][n]["id"]
		channel = search_result[s_id][n]["channel"]["name"]

		client.delete_messages(id, message_id)

		image = download_image(v_id, s_id)

		kb = [[]]
		if n == 0:
			kb[0].append(types.InlineKeyboardButton(text="📤", switch_inline_query_current_chat=f"sdownload|{s_id}|{v_id}|0"))
			kb[0].append(types.InlineKeyboardButton(text="➡️", callback_data=f"sresult {s_id} 1 right"))
		elif n == len(search_result[s_id]):
			kb[0].append(types.InlineKeyboardButton(text="⬅️", callback_data=f"sresult {s_id} {n-1} left"))
			kb[0].append(types.InlineKeyboardButton(text="📤", switch_inline_query_current_chat=f"sdownload|{s_id}|{v_id}|{n}"))
		else:
			kb[0].append(types.InlineKeyboardButton(text="⬅️", callback_data=f"sresult {s_id} {n-1} left"))
			kb[0].append(types.InlineKeyboardButton(text="📤", switch_inline_query_current_chat=f"sdownload|{s_id}|{v_id}|{n}"))
			kb[0].append(types.InlineKeyboardButton(text="➡️", callback_data=f"sresult {s_id} {n+1} right"))

		kb = types.InlineKeyboardMarkup(kb)

		client.send_photo(id, image, caption=f"📹**{title}**\n👤**{channel}**\n\n🔗**[URL]({url})**", reply_markup=kb)

		os.remove(image)

@app.on_inline_query()
def not_answer(client, inline_query):
	text = inline_query.query
	id = inline_query.from_user.id

	if "sdownload" in text:
		# sdownload_{s_id}_{v_id}_{n}
		data = text.split("|")

		s_id = data[1]
		v_id = data[2]
		n = int(data[3])

		if s_id in search_result:
			title = "👤"+search_result[s_id][n]["channel"]["name"]
			url = search_result[s_id][n]["link"]
			msg = search_result[s_id][n]["title"]
			image = f"https://img.youtube.com/vi/{v_id}/maxresdefault.jpg"
		else:
			title = "📤Нажмите для загрузки видео"
			url = f"https://www.youtube.com/watch?v={v_id}"
			msg = "Результаты были утеряны и мы не можем показать информацию о видео"
			image = "https://i.ibb.co/LvG31sF/none2.jpg"

		inline_query.answer(
                results=[
                    InlineQueryResultArticle(
                        title=title,
                        input_message_content=InputTextMessageContent(
                            url
                        ),
                        description=msg,
                        thumb_url=image
                    )], cache_time=1)
	elif "channel" in text:
		pass

clear()
app.run()