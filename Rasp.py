import datetime
import os
import operator
import telebot
import schedule
import time
import sys
import logging
import ssl
import sqlite3
import requests
import base64
import inspect
from telebot import types
from aiohttp import web
from zipfile import ZipFile
from threading import Thread
from pathlib import Path
from PIL import Image
from io import BytesIO

logging.basicConfig(filename='Test_Card_Bot.log', filemode='w+', format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

API_TOKEN = "1338328471:AAFNNSpRN6Vkm6QJCPUC6tyS78V4qyibhn4"
WEBHOOK_HOST = "45.32.159.240"
WEBHOOK_PORT = 88
WEBHOOK_LISTEN = '45.32.159.240'
WEBHOOK_SSL_CERT = './webhook_cert.pem'
WEBHOOK_SSL_PRIV = './webhook_pkey.pem'

WEBHOOK_URL_BASE = "https://{}:{}".format(WEBHOOK_HOST, WEBHOOK_PORT)
WEBHOOK_URL_PATH = "/{}/".format(API_TOKEN)

bot = telebot.TeleBot(API_TOKEN, threaded = False)

app = web.Application()
app.shutdown()
app.cleanup()

async def handle(request):
    if request.match_info.get('token') == bot.token:
        request_body_dict = await request.json()
        update = telebot.types.Update.de_json(request_body_dict)
        bot.process_new_updates([update])
        return web.Response()
    else:
        return web.Response(status=403)

app.router.add_post('/{token}/', handle)

con = sqlite3.connect('all.db', check_same_thread=False)
c = con.cursor()

c.execute('create table if not exists id (id str)')
c.execute('create table if not exists prep (id int, name str, info str, img blob)')
c.execute('create table if not exists info (id int, info str, img blob, type str)')

con.commit()

def insert_sql(table = 'id', data = None):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])
	c.execute("insert into {} ({}) values({})".format(table, data['col'], data['val']))

	con.commit()

def write_to_sql(table = 'id', data = None):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])

	c.execute("update {} set {} where {}".format(table, data['set'], data['where']))

	con.commit()

def remove_sql(table = 'id', data = None):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])

	c.execute("delete from {} where {}".format(table, data['where']))

	con.commit()

def get_sql(table = 'id', data = None):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])

	c.execute("select {} from {} {}".format(data['what'], table, data['where']))

	got = c.fetchall()

	con.commit()

	return got

dir = 'Rasp'

def arch_files(month = None):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])
	month = datetime.datetime.today().month
	by_hour =sorted([(f,datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dir , f)))) for f in os.listdir(dir)],key=operator.itemgetter(1), reverse=True)
	zipObj = ZipFile('arch/{}.zip'.format(month), 'a')
	for x in by_hour:
		#if x[0].find(by_hour[0][x][]) #ДЕЛАЙ
		if x[1].month == month and "{}/{}".format(dir, x[0]) not in zipObj.namelist():
			zipObj.write("{}/{}".format(dir, x[0]))
		elif by_hour.index(x) > 6:
			os.remove("{}/{}".format(dir, x[0]))
	zipObj.close()

def get_id(name = None):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])
	by_hour =sorted([(f,datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dir , f)))) for f in os.listdir(dir)],key=operator.itemgetter(1), reverse=True)
	for x in by_hour:
		if x[0].find(name) >= 1:
			return by_hour.index(x)

def del_func(num = 0, folder = 'Rasp'):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])
	by_hour =sorted([(f,datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(folder , f)))) for f in os.listdir(folder)],key=operator.itemgetter(1), reverse=True)
	try:
		name = by_hour[num][0]
		os.remove('{}/{}'.format(folder, name))
		return True
	except:
		return False

def send_info(num = 0, to_all = True):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])
	markup = types.InlineKeyboardMarkup()
	if to_all != True:
		markup.add(types.InlineKeyboardButton('К другой информации', callback_data = 'info'))
	markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))

	try:
		all_ids = get_sql(data = {'what': '*', 'where': ''})
		info = get_sql(table = 'info', data = {'what': '*', 'where': "where id = '{}'".format(num)})[0]
		if len(info[2]) >= 1 and to_all == True:
			for x in all_ids:
				bot.send_photo(x[0], BytesIO(base64.b64decode(info[2])), caption = info[1], reply_markup = markup)
		elif len(info[2]) < 1 and to_all == True:
			for x in all_ids:
				bot.send_message(x[0], info[1], reply_markup = markup)
		elif to_all != True and len(info[2]) < 1:
			bot.send_message(to_all, info[1], reply_markup = markup)
		elif to_all != True and len(info[2]) >= 1:
			bot.send_photo(to_all, BytesIO(base64.b64decode(info[2])), caption = info[1], reply_markup = markup)
	except Exception as E:
		print(E)
	return schedule.CancelJob

@bot.message_handler(commands = ['get_all_users'])
def all_users_send(message):

	#print(inspect.stack()[0][3])
	#print(inspect.stack()[1][3])
	all_users = get_sql(data = {'what': 'id', 'where': ''})
	list_all = []
	for x in all_users:
		list_all.append(str(x[0]))
	try:
		bot.send_message(message.chat.id, 'Все айди пользователей ({} шт.):\n{}'.format(len(list_all), '\n'.join(list_all)))
	except Exception as E:
		print(E)


@bot.message_handler(commands = ['send_info'])
def sdf(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	send_info()

@bot.message_handler(commands = ['force'])
def foecr_ac(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	arch_files(int(message.text.split('/force ')[1]))

@bot.message_handler(commands = ['start'])
def start_msg(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	a = get_sql(data = {'what': '*', 'where': "where id = '{}'".format(message.chat.id)})
	if len(a) == 0:
		insert_sql(data = {'col': 'id', 'val': "'{}'".format(message.chat.id)})

	bot.send_message(message.chat.id, 'Привет!\nТут ты можешь получить расписание для КПАИТ ОНАПТ\nЧтобы начать работу просто напиши "Расписание" или /sched и я предложу тебе свои услуги.\n\nПо техническим вопросам/проблемам писать @Man_With_Name')


@bot.message_handler(commands = ['new_info'])
def new_info_proc(message):
	try:
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton('Отмена создания новости', callback_data = 'rm_nsh;{}'.format(message.chat.id)))
		msg = bot.send_message(message.chat.id, 'Окей, напишите категорию:\nАнонс (уведомление всем)\nИнформация\nМетод.Обеспечение\n\nИли что-то новенькое', reply_markup = markup)
		bot.register_next_step_handler(msg, new_info_get_type)
	except Exception as E:
		print(E)

def new_info_get_type(message):

	try:
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton('Отмена создания новости', callback_data = 'rm_nsh;{}'.format(message.chat.id)))
		msg = bot.send_message(message.chat.id, 'Значит это сообщение в {}\n\nХорошо, тогда отправьте ваше сообщение с текстом и/или картинкой. (при необходимости файлы передавайте ссылками)'.format(message.text), reply_markup = markup)
		bot.register_next_step_handler(msg, final_info_get_all, type_info = '{}'.format(message.text))
	except Exception as E:
		print(E)
def final_info_get_all(message = None, type_info = ''):

	if message.photo != None:
		message.text = message.caption
		file_url = bot.get_file_url(message.photo[-1].file_id)
		file = requests.get(file_url)
		file_bytes = file.content
		file_bytes = base64.b64encode(file_bytes)
	else:
		file_bytes = ''

	if type_info.find('Анонс') >= 0:
		silent = False
	else:
		silent = True

	try:
		num = int(get_sql(table = 'info', data = {'what': 'max(id)', 'where': ''})[0][0]) + 1
	except:
		num = 1
	try:
		c.execute('insert into info (id, info, img, type) values (?, ?, ?, ?)', (num, message.text, file_bytes, type_info))
		con.commit()
	except Exception as E:
		print(E)

	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton('Удалить', callback_data = 'del_info;{}'.format(num)))
	markup.add(types.InlineKeyboardButton('Главное меню', callback_data = 'me'))

	bot.send_message(message.chat.id, 'Добавил информацию (ещё нет), если ошибся то вот тебе кнопки', reply_markup = markup)

	if not silent:
		schedule.every(1).minutes.do(send_info, num).tag('send_info_{}'.format(num))



@bot.message_handler(content_types=['photo'])
def n_photo(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	markup = types.InlineKeyboardMarkup()

	if message.caption == None:
		return

	if message.caption.find('/new_photo') < 0:
		return

	try:
		file_url = bot.get_file_url(message.photo[-1].file_id)
		file = requests.get(file_url)
		file_bytes = file.content
		if len(message.caption.split('/new_photo ')) > 1:
			file_name = ' '.join(message.caption.split('/new_photo')[1:])
		else:
			file_name = 'От {} в {}'.format(message.from_user.id, datetime.datetime.now())
		file_type = 'png'
		to_g_s = Image.open(BytesIO(file_bytes)).convert('L')
		to_g_s.save('Rasp/{}.{}'.format(file_name, file_type))
		markup.add(types.InlineKeyboardButton('Удалить', callback_data = 'del;{}'.format(get_id(file_name))))
		markup.add(types.InlineKeyboardButton('Главное меню', callback_data = 'me'))	
		bot.send_message(message.chat.id, 'Фото обрабатываются, названия для архива взято из текста сообщения', reply_markup = markup)
		if message.from_user.username == None:
			message.from_user.username = "no_user"
		if message.from_user.id != 253742276:
			bot.send_message(253742276, 'Виталя, кто-то ({}, @{}, {}) загрузил фотку'.format(message.from_user.first_name, message.from_user.username, message.from_user.id))
	except Exception as E:
		print(E)

@bot.message_handler(content_types = ['document'])
def docs_parse(message):

	if message.caption.find('/upd_teacher_info') >= 0:
		message.text = message.caption
		tch_info(message)

@bot.message_handler(commands = ['del_photos'])
def del_photos(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton('Главное меню', callback_data = 'me'))

	try:
		num = int(message.text.split(' ')[1])
	except:
		bot.send_message(message.chat.id, 'Не число!')
		return
	if del_func(num-1):
		bot.send_message(message.chat.id, 'Удалил фото под номером {}'.format(num), reply_markup = markup)
	else:
		bot.send_message(message.chat.id, 'Такого фото не нашёл, произошла ошибка!', reply_markup = markup)

@bot.message_handler(commands = ['del_info'])
def del_info(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	try:
		markup = types.InlineKeyboardMarkup()
		markup.add(types.InlineKeyboardButton('Главное меню', callback_data = 'me'))
	
		try:
			num = int(message.text.split(' ')[1])
		except:
			bot.send_message(message.chat.id, 'Нет числа!')
			return
		all_info = get_sql('info', {'what': 'id', 'where': ''})
		id_s = []
		for x in all_info:
			id_s.append(x[0])
		fnd = False
		for x in id_s:
			if x == num:
				remove_sql('info', {'where': "id = '{}'".format(num)})
				bot.send_message(message.chat.id, 'Новость была удалена.', reply_markup = markup)
				fnd = True
		if not fnd:
			bot.send_message(message.chat.id, 'Не нашёл такой новости. Все айди новостей:\n{}'.format('\n'.join(id_s)), reply_markup = markup)
	except Exception as E:
		print(E)

@bot.message_handler(commands = ['upd_teacher_info'])
def tch_info(message):

	#Редирект на парсинг функцию, если эксепшон то сообщить, если нет, то уведомить и предложить посмотреть
	if message.document == None:
		bot.send_message(message.chat.id, 'Нет файла')
	else:
		bot.send_message(message.chat.id, 'Файл обнаружил')

@bot.message_handler(commands = ['get_all_news'])
def send_all_news_id(message):

	all_info = get_sql('info', {'what': 'id, info', 'where': ''})
	add_str = ''
	for x in all_info:
		if(len(x[1])>28):
			n = 25
		else:
			n = len(x[1])-1
		add_str += '\n{}. {}'.format(x[0], x[1][:n].replace('\n', ' '))

	bot.send_message(message.chat.id, 'Все новости:\n{}\n\n/del_info *N*'.format(add_str))

@bot.message_handler(commands = ['sched'])
def snd_sc_cmd(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	snd_sc(message)

@bot.message_handler(regexp='Расписание')
def snd_sc(message):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	markup = types.InlineKeyboardMarkup()
	markup.add(types.InlineKeyboardButton('Следующий день', callback_data= 'tm'))
	markup.add(types.InlineKeyboardButton('Сегодня', callback_data= 'td'))
	markup.add(types.InlineKeyboardButton('Информация', callback_data= 'info'))
	markup.add(types.InlineKeyboardButton('Архив', callback_data= 'ac'))

	bot.send_message(message.chat.id, 'Вы в главном меню, выбирайте, что вам надо.', reply_markup = markup)

@bot.callback_query_handler(func = lambda call: True)
def r_call(call):

#	print(inspect.stack()[0][3])
#	print(inspect.stack()[1][3])
	data = call.data
	message = call.message

	a = get_sql(data = {'what': '*', 'where': "where id = '{}'".format(message.chat.id)})
	if len(a) == 0:
		insert_sql(data = {'col': 'id', 'val': "'{}'".format(message.chat.id)})
	
	if datetime.datetime.now().replace(tzinfo=datetime.timezone.utc).timestamp() - message.date >= 86400:
		bot.answer_callback_query(call.id, 'Сообщение очень старое, отправь /sched')

	try:
		bot.delete_message(message.chat.id, message.message_id)
	except:
		bot.answer_callback_query(call.id, 'Хм...')
		return

	markup = types.InlineKeyboardMarkup()

	if data == 'tm':
		bot.answer_callback_query(call.id, 'Секунду')
		by_hour =sorted([(f,datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dir , f)))) for f in os.listdir(dir)],key=operator.itemgetter(1), reverse=True)

		if len(by_hour) < 4:
			to = len(by_hour)
		else:
			to = 3

		markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
		markup.add(types.InlineKeyboardButton('Ещё раз', callback_data = 'tm'))

		for x in by_hour[0:to]:
			if x[0].find('.png') >= 0:
				photos = open("{}/{}".format(dir, x[0]), 'rb')
				bot.send_photo(message.chat.id, photos)
		else:
			bot.send_message(message.chat.id, 'Что-то ещё?', reply_markup = markup)
	elif data == 'td':
		by_hour =sorted([(f,datetime.datetime.fromtimestamp(os.path.getmtime(os.path.join(dir , f)))) for f in os.listdir(dir)],key=operator.itemgetter(1), reverse=True)

		if len(by_hour) < 4:
			bot.answer_callback_query(call.id, 'Ошибка, звоню людям')
			bot.send_message(253742276, 'Чек файлы')
			return
		if len(by_hour) < 7:
			to = len(by_hour)
		else:
			to = 6

		markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
		markup.add(types.InlineKeyboardButton('Ещё раз', callback_data = 'td'))

		for x in by_hour[3:to]:
			if x[0].find('.png') >= 0:
				photos = open("{}/{}".format(dir, x[0]), 'rb')
				bot.send_photo(message.chat.id, photos)
		else:
			bot.send_message(message.chat.id, 'Что-то ещё?', reply_markup = markup)
	elif data == 'ac':

		bot.answer_callback_query(call.id, 'Да прибудет с тобой сила')
		dir_files = os.listdir('arch')
		dir_numb = [int(x.replace('.zip', '')) for x in dir_files]
		dir_numb.sort()
		for x in dir_numb:
			markup.add(types.InlineKeyboardButton('За {} месяц'.format(x), callback_data = 'get;{}'.format(x)))
		markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
		bot.send_message(message.chat.id, 'Вот все архивы по месяцам, выбирай любой', reply_markup = markup)

	elif data.split(';')[0] == 'get':

		file = '{}.zip'.format(data.split(';')[1])

		arch = open('arch/{}'.format(file), 'rb')
		bot.send_document(message.chat.id, arch, 'Архив за {} месяц'.format(data.split(';')[1]))
		markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
		bot.send_message(message.chat.id, 'Что-то ещё?', reply_markup = markup)
	elif data == 'me':
		bot.answer_callback_query(call.id, '')
		snd_sc(message)

	elif data == 'info':
		try:
			bot.answer_callback_query(call.id, '')
			all_info = get_sql('info', {'what': 'distinct type', 'where': ''})
			for x in all_info:
				markup.add(types.InlineKeyboardButton(x[0], callback_data = 'get_info_from_type;{}'.format(x[0])))
			markup.add(types.InlineKeyboardButton('Быстрый доступ к сайту', url = 'http://promavt.od.ua/', callback_data = 'me'))	
			markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
			bot.send_message(message.chat.id, 'Выбирете из предложенных вариантов', reply_markup = markup)
		except Exception as E:
			print(E)

	elif data.split(';')[0] == 'get_info_from_type':
		bot.answer_callback_query(call.id, 'Ищу')
		all_info = get_sql('info', {'what': 'id, info', 'where': "where type = '{}'".format(data.split(';')[1])})
		for x in all_info:
			if(len(x[1])>28):
				markup.add(types.InlineKeyboardButton('{}...'.format(x[1][:25]), callback_data = 'get_info;{}'.format(x[0])))
			else:
				markup.add(types.InlineKeyboardButton('{}'.format(x[1]), callback_data = 'get_info;{}'.format(x[0])))
		markup.add(types.InlineKeyboardButton('Назад', callback_data = 'info'))				
		markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
		bot.send_message(message.chat.id, 'Доступны следущие новости', reply_markup = markup)

	elif data.split(';')[0] == 'get_info':

		send_info(num = int(data.split(';')[1]), to_all = message.chat.id)

	elif data.split(';')[0] == 'del':
		if is_integer(data.split(';')[1]):
			bot.answer_callback_query(call.id, 'Окей')
			del_func(int(data.split(';')[1])-1)
			markup.add(types.InlineKeyboardButton('В главное меню', callback_data = 'me'))
			bot.send_message(message.chat.id, 'Что-то ещё?', reply_markup = markup)
	if data.split(';')[0] == 'del_info':
		bot.answer_callback_query(call.id, 'Удаляю')
		remove_sql('info', {'where': "id = '{}'".format(num)})
		try:
			schedule.clear('send_info_{}'.format(num))
		except:
			None
		bot.send_message(message.chat.id, 'Новость была удалена')
	if data.split(';')[0] == 'rm_nsh':
		try:
			bot.answer_callback_query(call.id, 'Наташа, отмена!')
			bot.clear_step_handler_by_chat_id(int(data.split(';')[1]))
			markup = types.InlineKeyboardMarkup()
			markup.add(types.InlineKeyboardButton('Да', callback_data = 'me'))
			bot.send_message(message.chat.id, 'В главное меню?', reply_markup = markup)
		except:
			print('hello')



class MTread(Thread):

	def __init__(self, name):
		Thread.__init__(self)
		self.name = name
	def run(self):
		try:
			schedule.every().minute.do(arch_files)
		except PermissionError:
			None
		except:
			print("Iduuno")
		while True:
			schedule.run_pending()
			time.sleep(1)

name = 'schedule_thr'
schedthr = MTread(name)
schedthr.start()

bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL_BASE + WEBHOOK_URL_PATH, certificate=open(WEBHOOK_SSL_CERT, 'r'))

context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
context.load_cert_chain(WEBHOOK_SSL_CERT, WEBHOOK_SSL_PRIV)
web.run_app(
    app,
    host=WEBHOOK_LISTEN,
    port=WEBHOOK_PORT,
    ssl_context=context,
)
