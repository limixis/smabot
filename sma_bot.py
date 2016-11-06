from telegram import ReplyKeyboardMarkup
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from validator import Validator

from collections import Counter
import argparse


TOKEN = 'xxxxxxxxxxxxxxxxxxx'
KEYS_FILE = 'C:\Users\limixis\Desktop\keys.tsv'
LOG_FILE = 'C:\Users\limixis\Desktop\log.tsv'

BANDS = ['AC/DC', 'KINO', '4DB', 'The Beatles', 'Zhuki', 'Band 21', 'Band 31', 'Band 51', 'Banda']

reply_keyboard = [BANDS[i:i + 2] for i in range(0, len(BANDS), 2)]

markup = ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True, resize_keyboard=True)

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
                    text="I'm a SMA bot, give me your token and vote for a favourite band!")


def stats(bot, update):
    telegram_user = update.message.from_user
    if telegram_user.username in ADMIN_NAMES:
        bot.sendMessage(chat_id=update.message.chat_id,
                        text=band_stats.items())


class Chatter(object):
    def __init__(self):
        self.modes = {'AUTHENTICATION': self.process_token, 'VOTING': self.vote, 'FEEDBACK': self.send_feedback}
        self.mode = 'AUTHENTICATION'
        self.key_val = Validator(KEYS_FILE)

    def handle_text(self, bot, update):
        func = self.modes[self.mode]
        func(bot, update)

    def process_token(self, bot, update):
        is_correct = self.key_val.validate_keys(update.message.text.strip())
        if is_correct:
            message = 'Yep, your token is fine, now you can vote!'
            bot.sendMessage(chat_id=update.message.chat_id, text=message, reply_markup=markup)
            self.mode = 'VOTING'
        else:
            message = 'Sorry, I don\'t recognize your token, try again?'
            bot.sendMessage(chat_id=update.message.chat_id, text=message)

    def vote(self, bot, update):
        band = update.message.text
        if band in BANDS:
            band_stats[band] += 1
            with open(LOG_FILE, 'a') as f:
                print >> f, band
        bot.sendMessage(chat_id=update.message.chat_id,
                        text='Good choice, thanks!')
        self.mode = 'AUTHENTICATION'

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
    text_handler = MessageHandler(Filters.text, chatter.handle_text)
    dp.add_handler(text_handler)

    updater.start_polling()

    updater.idle()
