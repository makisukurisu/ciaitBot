import datetime
import telebot #pyTelegramBotAPI
import logging
from classes import Day, Group, Pair

logging.basicConfig(filename="colBot.log", filemode="w+", format='%(asctime)s - %(levelname)s - %(message)s', level=logging.INFO)

bot = telebot.TeleBot("1238495590:AAEVXKiybdfvt5gcXiXGNheIyNRgGH3T6us", "HTML")

days = []

def getAllTeacher(teacher, dayOrdinal, interval = 0):
    retArray = {}
    for day in days:
        if day.DayOrdinal == dayOrdinal or day.DayOrdinal in range(dayOrdinal, dayOrdinal+interval+1):
            for group in day.Groups:
                for pair in group.Pairs:
                    if pair.Teacher == teacher:
                        try:
                            retArray[day.DayOrdinal].append({"Group": str(group), "Pair": group.Pairs.index(pair)+1})
                        except KeyError:
                            retArray[day.DayOrdinal] = [{"Group": str(group), "Pair": group.Pairs.index(pair)+1}]
    return retArray

@bot.message_handler(commands=["getnext"])
def getNext(message, call = None):
    if message:
        bot.send_message(message.chat.id, "Wait for upd")
    elif call:
        bot.send_message(call.message.chat.id, "Wait for upd (callack)")

@bot.message_handler(commands=["main"])
def mainMenuF(message):

    i = telebot.types.InlineKeyboardButton
    markup = telebot.types.InlineKeyboardMarkup()
    markup.add(i("Следующий день", callback_data="get;Next"))
    markup.add(i("Текущий день", callback_data="get;Today"))
    markup.add(i("Информация", callback_data="get;Info"))
    markup.add(i("Сайт", "https://promavt.od.ua"))
    bot.send_message(message.chat.id, "Главное меню:", reply_markup=markup)

@bot.callback_query_handler(func = lambda call: True)
def answerCallback(call):
    chatId = call.message.chat.id
    data = call.data
    dataSplit = data.split(";")
    
    if dataSplit[0] == "get":
        if dataSplit[1] == "Next":
            bot.answer_callback_query(call.id, "Working")
            getNext(None, call)
        elif dataSplit[1] == "Today":
            bot.answer_callback_query(call.id, "WIP")
        elif dataSplit[1] == "Info":
            bot.answer_callback_query(call.id, "WIP")


bot.polling(True)