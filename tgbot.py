#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Example script for initialize EVE-NG
#
# alexeykr@gmail.com
# coding=utf-8
# import codecs
# https://
import logging
import requests
import re
import os
import sys
from netmiko import ConnectHandler

# from telegram import get_chat_member
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackQueryHandler
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

from scrapli import Scrapli


def check_group(check_id, tgbot):
    check = False
    if check_id == int(NUM_CHAT):
        logger.info("Check: {}".format(check_id))
        return True
    user_status = tgbot.getChatMember(NUM_CHAT, check_id)
    if user_status.status != 'left':
        check = True
    logger.info("Check: {} = {}".format(check_id, user_status.status))
    return check


def chat_id(bot, update):
    text = 'The chat_id for this is %d. Take note that chat_id for group is negative number' % update.message.chat_id
    bot.sendMessage(update.message.chat_id, text)


def get_url():
    contents = requests.get('https://random.dog/woof.json').json()
    url = contents['url']
    return url


def get_image_url():
    allowed_extension = ['jpg', 'jpeg', 'png']
    file_extension = ''
    while file_extension not in allowed_extension:
        url = get_url()
        file_extension = re.search("([^.]*)$", url).group(1).lower()
    return url


def btn_handler(update, context):
    if not (check_group(update.effective_chat.id, context.bot)):
        return
    keyboard = [
        [InlineKeyboardButton("Option 1", callback_data='1'), InlineKeyboardButton("Option 2", callback_data='2')],
        [InlineKeyboardButton("Option 3", callback_data='3')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Please choose:', reply_markup=reply_markup)


def button(update, context):
    query = update.callback_query
    query.edit_message_text(text="Selected option: {}".format(query.data))


def bop_handler(update, context):
    if not (check_group(update.effective_chat.id, context.bot)):
        return
    url = get_image_url()
    chat_id = update.message.chat_id
    context.bot.send_photo(chat_id=chat_id, photo=url)
    # context.bot.send_photo(chat_id=NUM_CHAT, photo=url)


def getint_handler(update, context):
    if not (check_group(update.effective_chat.id, context.bot)):
        return
    device = {
        "host": "192.168.30.225",
        "auth_username": "alex",
        "auth_password": "Cisco123",
        "auth_strict_key": False,
        "platform": "cisco_iosxr",
        "transport": "paramiko",
    }

    conn = Scrapli(**device)
    conn.open()
    # print(conn.get_prompt())
    output = conn.send_command("sh version  | utility egrep expr 'IOS|uptime'")
    conn.close()
    logger.info(f'Output: {output.result}')
    # context.bot.send_message(chat_id=NUM_CHAT, text=f'{output}')
    update.effective_message.reply_text(f'{output.result}')


# def getint_handler(update, context):
#     if not (check_group(update.effective_chat.id, context.bot)):
#         return
#     cisco = {
#         'device_type': 'cisco_ios',
#         'host': '192.168.30.225',
#         'port': '22',
#         'username': 'alex',
#         'password': 'Cisco123',
#     }
#     logger.info("Get query ... from chat_id: {}".format(update.effective_chat.id))
#     # logger.info(f'{cisco}')
#     net_connect = ConnectHandler(**cisco)
#     net_connect.find_prompt()
#     output = net_connect.send_command("sh version  | utility egrep expr 'IOS|uptime'")
#     logger.info(f'Output: {output}')
#     # context.bot.send_message(chat_id=NUM_CHAT, text=f'{output}')
#     update.effective_message.reply_text(f'{output}')


def start_handler(update, context):
    # update.effective_message.reply_text(f'Привет {update.message.from_user.first_name}! Это приватный чат!')
    # res = context.bot.getChatMember(NUM_CHAT, '1008829533')
    # res = context.bot.getChatMember(NUM_CHAT, update.effective_chat.id)
    # context.bot.send_message(chat_id=NUM_CHAT, text=f'Привет {update.message.from_user.first_name}!')
    # logger.info("Start: {} ==== {} ====".format(update.effective_chat, res.status))
    logger.info("Start: {} ".format(update.effective_chat))
    if check_group(update.effective_chat.id, context.bot):
        update.effective_message.reply_text(f'Привет {update.message.from_user.first_name}!')
    else:
        update.effective_message.reply_text(f'Привет {update.message.from_user.first_name}! Это приватный чат, ты должен быть членом группы.')


def unknown(update, context):
    if not (check_group(update.effective_chat.id, context.bot)):
        return
    context.bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")


def echo_handler(update, context):
    if not (check_group(update.effective_chat.id, context.bot)):
        return
    # if check_group(update.effective_chat.id) return
    logger.info("Receive message: {}".format(update.effective_message.text))
    update.effective_message.reply_text(update.effective_message.text)


def random_handler(update, context):
    if not (check_group(update.effective_chat.id, context.bot)):
        return
    number = 8
    logger.info("User {} randomed number {}".format(update.effective_user["id"], number))
    update.message.reply_text("Random number: {}".format(number))


def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"', update, error)


def run(updater):
    if MODE == "dev":
        logger.info(f'Run in Developer mode: {MODE}')
        updater.start_polling(poll_interval=0.5, timeout=20)
        updater.idle()

    elif MODE == "prod":
        logger.info(f'Run in Prodaction mode: {MODE}')
        PORT = int(os.environ.get("PORT", "8443"))
        HEROKU_APP_NAME = os.environ.get("HEROKU_APP_NAME")
        updater.start_webhook(listen="0.0.0.0", port=int(PORT), url_path=TOKEN)
        updater.bot.set_webhook("https://{}.herokuapp.com/{}".format(HEROKU_APP_NAME, TOKEN))
        updater.idle()
    else:
        logger.error("No MODE specified!")
        sys.exit(1)


if __name__ == "__main__":
    NUM_CHAT = os.getenv("NUM_CHAT")
    MODE = os.getenv("MODE")
    TOKEN = os.getenv("TOKEN")
    USERSSH = os.getenv("USERSSH")
    PASS = os.getenv("PASS")
    # Enable logging
    logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
    logger = logging.getLogger(__name__)

    # Set up the Updater
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher
    # Add handlers
    dp.add_handler(CommandHandler('start', start_handler))
    dp.add_handler(CommandHandler('btn', btn_handler))
    dp.add_handler(CallbackQueryHandler(button))
    dp.add_handler(CommandHandler('random', random_handler))
    dp.add_handler(CommandHandler('bop', bop_handler))
    dp.add_handler(CommandHandler('getint', getint_handler))
    dp.add_handler(MessageHandler(Filters.text, echo_handler))
    # dp.add_handler(MessageHandler(Filters.command, unknown))
    dp.add_error_handler(error)

    run(updater)
