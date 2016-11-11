# -*- coding: UTF-8 -*-

from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from validator import Validator

from collections import Counter
import argparse


TOKEN = 'xxxxxxxxxxxxxxxxxxxxxxxxxxxx'
KEYS_FILE = 'C:\Users\limixis\Documents\GitHub\smabot\keys.tsv'
LOG_FILE = 'C:\Users\limixis\Documents\GitHub\smabot\log.tsv'

BANDS = [u'Авиарежим', u'Полдень на латинском', u'The Last Realism', u'4 Quarters Of A Pizza', u'', u'Всё никак', u'One piece band', u'', 'Banda']

reply_keyboard = [BANDS[i:i + 2] for i in range(0, len(BANDS), 2)]
confirm_keyboard = [[u'Да', u'Нет']]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)
markup_confirm = ReplyKeyboardMarkup(confirm_keyboard, one_time_keyboard=True, resize_keyboard=True)

band_stats = Counter()

ADMIN_NAMES = ['limixis', 'oneunreadmail']


def parse_args():
    parser = argparse.ArgumentParser(description="Generate tokens for authentication")
    parser.add_argument("-f", dest="key_file", default="./keys.tsv", help="Path to file with keys")
    parser.add_argument("--bands", dest="bands", nargs="*", default=None, help="List of bands")
    parser.add_argument("--admins", dest="admins", nargs="*", default=['limixis', 'oneunreadmail'], help="List of admin usernames")

    return parser.parse_args()


def start(bot, update):
    bot.sendMessage(chat_id=update.message.chat_id,
                    text=u'Добрый вечер! Я SMA-бот. Пришлите мне свой пароль и голосуйте за любимую группу!')


def stats(bot, update):
    telegram_user = update.message.from_user
    if telegram_user.username in ADMIN_NAMES:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=band_stats.items())


class Chatter(object):
    def __init__(self):
        self.modes = {'AUTHENTICATION': self.process_token, 'VOTING': self.vote, 'FEEDBACK': self.send_feedback,
                      self.confirm: 'CONFIRMATION'}
        self.key_val = Validator(KEYS_FILE)

    def handle_text(self, bot, update, user_data):
        if not user_data.get('mode'):
            user_data['mode'] = 'AUTHENTICATION'
        mode = user_data['mode']
        func = self.modes[mode]
        func(bot, update, user_data)

    def process_token(self, bot, update, user_data):
        is_correct = self.key_val.validate_keys(update.message.text.strip())
        if is_correct:
            message = u'Спасибо, теперь можно голосовать!'
            bot.sendMessage(chat_id=update.message.chat_id, text=message, reply_markup=markup)
            user_data['mode'] = 'VOTING'
        else:
            message = u'Чтобы проголосовать, нужно ввести свежий пароль'
            bot.sendMessage(chat_id=update.message.chat_id, text=message)

    def vote(self, bot, update, user_data):
        band = update.message.text
        if band in BANDS:
            message = u'Вы точно хотите проголосовать за ' + band + u'?'
            user_data['band'] = band
            user_data['mode'] = 'CONFIRMATION'
        else:
            message = u'Ээ... эта группа сегодня не выступала. Выберите группу из списка.'
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=message)

    def confirm(self, bot, update, user_data):
        _markup=None
        answer = update.message.text.decode('utf-8')
        if answer.lower() == u'да':
            band = user_data['band']
            band_stats[band] += 1
            with open(LOG_FILE, 'a') as f:
                print >> f, band.encode('utf-8')
            message = u'Отличный выбор, спасибо!'
            user_data['mode'] = 'AUTHENTICATION'
        elif answer.lower() == u'нет':
            message = u'Передумали? Тогда проголосуйте заново!'
            user_data['mode'] = 'VOTING'
            _markup = markup
        else:
            message = u'Не понятно. Давайте еще раз. Вы точно хотите проголосовать за ' + user_data['band'] + u'?'
            _markup = markup_confirm
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=message, reply_markup=_markup)

    def send_feedback(self, bot, update):
        pass

if __name__ == "__main__":

    # If you want to pass parameters via command line
    # args = parse_args()

    updater = Updater(token=TOKEN)

    dp = updater.dispatcher

    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    start_handler = CommandHandler('start', start)
    dp.add_handler(start_handler)

    stats_handler = CommandHandler('stats', stats)
    dp.add_handler(stats_handler)

    chatter = Chatter()
    text_handler = MessageHandler(Filters.text, chatter.handle_text, pass_user_data=True)
    dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()
