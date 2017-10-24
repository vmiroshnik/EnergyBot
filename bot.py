__name__ = '__EnergyBot__'

import os
import logging
import datetime as dt
from io import BytesIO

from flask import Flask, request
import telebot

import settings
import utils


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(name)-12s %(levelname)-8s %(message)s',
                    datefmt='%m-%d %H:%M',
                    filename='bot.log',
                    filemode='w')


logger = telebot.logger
logger.setLevel(logging.DEBUG)

# telebot.apihelper.proxy = settings.proxy

bot = telebot.TeleBot(settings.token)

server = Flask(__name__)


@bot.message_handler(commands=['start', 'help'])
def hello(message):
    bot.reply_to(message, 'Ну привіт, енергомасони')
    with open(r'static\Tesla.webp', 'rb') as sti:
        bot.send_sticker(message.chat.id, sti)


@bot.message_handler(regexp='some')
def show_keyboard(message):
    markup = telebot.types.ReplyKeyboardMarkup(row_width=2, one_time_keyboard=True)
    itb1 = telebot.types.KeyboardButton('a')
    itb2 = telebot.types.KeyboardButton('b')
    itb3 = telebot.types.KeyboardButton('b')
    markup.add(itb1, itb2, itb3)
    bot.reply_to(message, 'Choose one letter:', reply_markup=markup)


@bot.message_handler(commands=['plot'])
def send_plot(message):
    date = dt.datetime.today()
    keyboard = telebot.types.InlineKeyboardMarkup(row_width=2)
    button1 = telebot.types.InlineKeyboardButton(text='Поточний графік',
                                                 callback_data=date.strftime('%d.%m.%Y') + ' 1')
    button2 = telebot.types.InlineKeyboardButton(text='За попередню добу',
                                                 callback_data=(date - dt.timedelta(1)).strftime('%d.%m.%Y') + ' ')
    keyboard.add(button1, button2)
    bot.send_message(message.chat.id, 'Поточний графік чи за попередню добу?', reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    date_str, today = call.data.split(' ')
    # proxies = settings.proxy
    data_tb = utils.get_data_tb(today)  #, proxies=proxies)
    plt = utils.make_graph(data_tb, date_str, save=False)
    plot_buffer = BytesIO()
    with plot_buffer as plot:
        plt.savefig(plot, format='png')
        plot.seek(0)
        bot.send_photo(call.message.chat.id, plot.getvalue())


@bot.message_handler(content_types='text')
def echo(message):
    bot.reply_to(message, message.text)


@server.route("/bot", methods=['POST'])
def get_message():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url="https://energybot.herokuapp.com/bot")

# if __name__ == '__EnergyBot__':
#     bot.polling(none_stop=True)
server.run(host='0.0.0.0', port=os.environ.get('PORT', 5000))
server =Flask(__name__)

















