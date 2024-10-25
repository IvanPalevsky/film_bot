from logic import *
import telebot
from config import *
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=["start"])
def start(message):
    user_name = message.from_user.first_name
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("Случайный фильм", callback_data="random_movie"))
    bot.send_message(message.chat.id, f"Привет, {user_name}! Нажми на кнопку, чтобы получить случайный фильм.", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data == "random_movie")
def callback_random_movie(call):
    movie_id = m.get_random_movie()
    movie_info = m.movie_discription(movie_id)
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, movie_info)

@bot.message_handler(commands=["search"])
def search_movie(message):
    # movie_id = m.get_random_movie()
    # movie_info = m.movie_discription(movie_id)
    # bot.answer_callback_query(call.id)
    # bot.send_message(call.message.chat.id, movie_info)
    pass

@bot.message_handler(commands=["settigs"])
def set_settings(message):
    pass

@bot.message_handler(commands=["reset"])
def reset_settings(message):
    pass


if __name__ == '__main__':
    m = DB_Manager(DATABASE)
    bot.infinity_polling()