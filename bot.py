import os
import django
import telebot

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'portal.settings')
django.setup()

from portal.curr_settings import BOT_TOKEN

bot = telebot.TeleBot(BOT_TOKEN)


# '/start 54645454'
# @bot.message_handler(regexp=r'^/start\s+')
# def handle_message(message):
#     chat_id = message.chat.id
#     token = message.text.split(' ')[-1]
#     profile = Profile.objects.get(connect_token=token,
#                                   is_active=True)
#     profile.telegram_id = chat_id
#     profile.save()
#
#     print('chat_id=' + str(chat_id))
#     print('token: ' + str(token))


@bot.message_handler(commands='/myid')
def handle_my_chat_id(message):
    chat_id = message.chat.id
    bot.send_message(chat_id,
                     chat_id)


if __name__ == '__main__':
    bot.polling(none_stop=True)


# bot.send_message(request.user.profile.chat_id, 'Тест')
# 1