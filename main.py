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
    bot.answer_callback_query(call.id)
    send_movie_info(call.message.chat.id, movie_id)

@bot.message_handler(commands=["search"])
def search_movie(message):
    user_id = message.from_user.id
    movies = m.get_movie_by_settings(user_id, n=1)
    if movies:
        send_movie_info(message.chat.id, movies[0][0])
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
    bot.send_message(message.chat.id, f'Ваши жанры:{m.get_genres_by_user_id(message.chat.id)} Выберите жанр', reply_markup=markup)

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

@bot.callback_query_handler(func=lambda call: call.data.startswith('genre_'))
def callback_genre(call):
    genre_id = int(call.data.split('_')[1])
    user_id = call.from_user.id
    m.add_genre_setting(user_id, genre_id, neg_or_pos=1)
    bot.answer_callback_query(call.id, text="Жанр добавлен")

@bot.callback_query_handler(func=lambda call: call.data == 'end_genres')
def callback_end_genres(call):
    bot.delete_message(call.message.chat.id, call.message.message_id)
    movies = m.get_movie_by_settings(call.from_user.id, n=1)
    if movies:
        send_movie_info(call.message.chat.id, movies[0][0])
    else:
        bot.send_message(call.message.chat.id, "Фильмы не найдены")

@bot.message_handler(commands=["set_director"])
def set_director(message):
    if len(message.text.split()) == 1:
        bot.reply_to(message, 
            "Используйте: /set_director Имя Режиссера\n"
            "Например: /set_director James Cameron")
        return
    director_name = ' '.join(message.text.split()[1:])
    directors = m.find_director(director_name)
    
    if not directors:
        bot.reply_to(message, "Режиссер не найден. Проверьте правильность написания имени.")
        return
        
    if len(directors) == 1:
        director_id, director_name = directors[0]
        conn = sqlite3.connect(DATABASE)
        cur = conn.cursor()
        cur.execute('SELECT release_date_strat, release_date_end, vote_average, popularity FROM settings WHERE user_id = ?', 
                   (message.from_user.id,))
        settings = cur.fetchone()
        
        if settings:
            m.save_settings(message.from_user.id, settings[0], settings[1], settings[2], settings[3], director_id)
        else:
            m.save_settings(message.from_user.id, "1900", "2024", 0, 0, director_id)
            
        bot.reply_to(message, f"Режиссер {director_name} добавлен в настройки поиска!")
    else:
        response = "Найдено несколько режиссеров. Уточните запрос:\n"
        for _, name in directors:
            response += f"• {name}\n"
        bot.reply_to(message, response)

@bot.message_handler(commands=["reset_director"])
def reset_director(message):
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()
    cur.execute('UPDATE settings SET director_id = NULL WHERE user_id = ?', (message.from_user.id,))
    conn.commit()
    conn.close()
    bot.reply_to(message, "Фильтр по режиссеру сброшен")

def create_movie_markup(movie_id):
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton("Понравилось", callback_data=f"like_{movie_id}"),
        InlineKeyboardButton("Не смотрел", callback_data=f"not_watched_{movie_id}")
    )
    markup.add(InlineKeyboardButton("Показать лучшие фильмы", callback_data="show_favorites"))
    return markup

def send_movie_info(chat_id, movie_id):
    movie_info = m.movie_discription(movie_id)
    markup = create_movie_markup(movie_id)
    bot.send_message(chat_id, movie_info, reply_markup=markup)

@bot.callback_query_handler(func=lambda call: call.data.startswith(('like_', 'not_watched_', 'show_favorites')))
def callback_movie_action(call):
    if call.data.startswith('like_'):
        movie_id = int(call.data.split('_')[1])
        m.add_to_favorites(call.from_user.id, movie_id)
        bot.answer_callback_query(call.id, text="Фильм добавлен в избранное!")
        
    elif call.data.startswith('not_watched_'):
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, "Обязательно посмотрите и поставьте оценку!")
        
    elif call.data == 'show_favorites':
        favorites = m.get_favorites(call.from_user.id)
        
        if favorites:
            message = "Ваши любимые фильмы:\n\n"
            for title, release_date, rating in favorites:
                message += f"{title} ({release_date}) - {rating}\n"
        else:
            message = "У вас пока нет избранных фильмов!"
            
        bot.answer_callback_query(call.id)
        bot.send_message(call.message.chat.id, message)

if __name__ == '__main__':
    m = DB_Manager(DATABASE)
    bot.infinity_polling()
