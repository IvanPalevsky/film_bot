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
    user_id = message.from_user.id
    movies = m.get_movie_by_settings(user_id, n=1)
    if movies:
        movie_info = m.movie_discription(movies[0][0])
        bot.reply_to(message, movie_info)
    else:
        bot.reply_to(message, "Фильмы не найдены")

@bot.message_handler(commands=["settings"])
def set_settings(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, "Используйте: /settings [год_начала-год_конца] [оценка] [популярность]\nПример: /settings 2010-2020 7.5 100")
    else:
        params = message.text.split()
        date_range = params[1].split('-')
        date_start = date_range[0]
        date_end = date_range[1]
        rating = float(params[2])
        popularity = int(params[3])
            
        user_id = message.from_user.id
        m.save_settings(user_id, date_start, date_end, rating, popularity)
        bot.reply_to(message, "Настройки сохранены!")

@bot.message_handler(commands=["set_genres"])
def set_genres(message, page=1):
    genres = m.get_genres()
    markup = InlineKeyboardMarkup()
    for i in range(5):
        genre = genres[((page - 1)*5)%len(genres) + i]
        markup.add(InlineKeyboardButton(genre[1], callback_data=f"genre_{genre[0]}"))
    markup.add(InlineKeyboardButton('🔙', callback_data=f'scroll_left_{page}'), InlineKeyboardButton(f'{page}/{round(len(genres)/5)}', callback_data='-'), InlineKeyboardButton('🔜', callback_data=f'scroll_right_{page}'))
    markup.add(InlineKeyboardButton('Закончить выбор', callback_data='end_genres'))
    bot.send_message(message.chat.id, 'Выберите жанр', reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith('scroll'))
def callback_scroll(call):
    l = call.data.split('_')
    page = int(l[2])
    if l[1] == 'left':
        page -= 1
    else:
        page += 1
    bot.delete_message(call.message.chat.id, call.message.message_id)
    set_genres(call.message, page)

@bot.message_handler(commands=["reset"])
def reset_settings(message):
    user_id = message.from_user.id
    m.reset_settings(user_id)
    bot.reply_to(message, "Настройки сброшены. Теперь перезапустите бота командой /start")


if __name__ == '__main__':
    m = DB_Manager(DATABASE)
    bot.infinity_polling()
