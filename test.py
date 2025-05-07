from telebot import TeleBot

bot = TeleBot('8160303615:AAG4CBszOXVbNj3T8PttKOCwfTTS6CjTtF8')

@bot.business_message_handler(regexp='someregexp')
def command_help(message):
    bot.send_message(message.chat.id, 'Did someone call for help?')

@bot.business_message_handler(func=lambda message: message.document.mime_type == 'text/plain',
    content_types=['document'])
def command_handle_document(message):
    bot.send_message(message.chat.id, 'Document received, sir!')

@bot.business_message_handler(func=lambda message: True, content_types=['audio', 'photo', 'voice', 'video', 'document',
    'text', 'location', 'contact', 'sticker'])
def default_command(message):
    bot.send_message(message.chat.id, "This is the default command handler.")

bot.polling(non_stop=True)