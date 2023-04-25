from PIL import Image
from sys import platform
import os, json, re, requests

# Очистка консоли
def clear():
	if platform == "linux" or platform == "linux2":
		os.system("clear")
	elif platform == "win32":
		os.system("cls")

# Проверка ссылки
def is_youtube_link(text):
    pattern = r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+(&\S*)?'
    pattern2 = r'(https?://)?(www\.)?(youtu\.be/|youtube\.com/watch\?v=)[\w-]+(&\S*)?'
    return bool(re.match(pattern, text)) or bool(re.match(pattern2, text))

# Работа с json
def json_read(file):
	with open(file, encoding="utf-8") as f:
		return json.load(f)
json_r = json_read

def json_write(file, new_dict):
	with open(file, 'w', encoding="utf-8") as f:
		json.dump(new_dict, f, sort_keys=True, indent=2)
json_w = json_write

def file_resize(size):
	if size/(2**20) > 1000:
		if size/(2**30) > 1000:
			size = size/(2**40)
			size = "{:.1f}".format(size)+" ТБ"
		else:
			size = size/(2**30)
			size = "{:.1f}".format(size)+" ГБ"
	else:
		size = size/(2**20)
		size = "{:.1f}".format(size)+" МБ"
	return size

def convert_image(image):
	im = Image.open(image)
	crop_width = im.size[1]
	crop_height = im.size[1]
	img_width, img_height = im.size
	im = im.crop(((img_width - crop_width) // 2,
                         (img_height - crop_height) // 2,
                         (img_width + crop_width) // 2,
                         (img_height + crop_height) // 2))
	im = im.resize((320, 320))
	im.save(image)

def convert_image_2(image_path):
	with Image.open(image_path) as img:
		# Получаем размеры изображения
		width, height = img.size

		# Если изображение уже меньше 320 пикселей по длине и ширине, то ничего не делаем
		if width <= 320 and height <= 320:
			return

		# Вычисляем коэффициент масштабирования
		scale = min(320/width, 320/height)

		# Вычисляем новые размеры изображения
		new_width = int(width * scale)
		new_height = int(height * scale)

		# Масштабируем изображение
		img.thumbnail((new_width, new_height))

		# Сохраняем измененное изображение
		img.save(image_path)

	#im = Image.open(image)
	#im = im.resize((320, 320))
	#im.save(image)

def download_image(video_id, name):
	if ".jpg" not in name: name += ".jpg"
	result = requests.get(f"https://img.youtube.com/vi/{video_id}/maxresdefault.jpg").content
	with open(name, "wb") as f:
		f.write(result)
	return name

class progress_bar:
    def __init__(self, max_per=100):
        self.data = {"white": 10, "black": 0}
        self.max = 10
        self.per = max_per

    def get(self):
        obj = "■"*self.data["black"]+"□"*self.data["white"]
        return obj

    def add(self, per=1):
        if self.data["white"] != 0:
            col = per//self.max
            self.data["white"] -= col
            self.data["black"] += col

    def set(self, per=1):
        if self.data["white"] != 0:
            col = per//self.max
            self.data["white"] = 10-col
            self.data["black"] = col