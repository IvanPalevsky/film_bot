import sqlite3
from config import *

class DB_Manager:
    def __init__(self, database):
        self.database = database

    def create_user_settings_table(self):
        conn = sqlite3.connect(self.database)
        with conn:
            conn.execute('''CREATE TABLE IF NOT EXISTS settings(
                         user_id INTEGER,
                         release_date_strat TEXT,
                         release_date_end TEXT,
                         vote_average REAL,
                         popularity INTEGER,
                         director_id INTEGER   
                         )''')
            conn.execute('''CREATE TABLE IF NOT EXISTS genre_settings(
                        user_id INTEGER, 
                        genre_id INTEGER,
                        neg_or_pos INTEGER,
                        FOREIGN KEY(genre_id) REFERENCES genres(genre_id)  
                         )''')
           
    def get_movie_by_settings(self, user_id, n=5):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM settings WHERE user_id = ?', (user_id,))
            s = cur.fetchone()
            if s:
                query = '''
                    SELECT DISTINCT m.id FROM movies m
                    JOIN movies_genres mg ON m.id = mg.movie_id
                    WHERE release_date BETWEEN ? AND ?
                    AND vote_average >= ?
                    AND popularity >= ?
                    AND mg.genre_id IN (
                        SELECT genre_id 
                        FROM genre_settings 
                        WHERE user_id = ?
                    )
                '''
                params = [s[1], s[2], s[3], s[4], user_id]
                
                if s[5]:
                    query += ' AND m.director_id = ?'
                    params.append(s[5])
                    
                query += ' ORDER BY RANDOM()'
                cur.execute(query, tuple(params))
            else:
                cur.execute('SELECT id FROM movies ORDER BY RANDOM()')           
            return cur.fetchmany(n)

    def get_random_movie(self):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT id FROM movies ORDER BY random()')
            return cur.fetchone()[0]
        
    def movie_discription(self, movie_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM movies WHERE id = ?', (movie_id, ))
            r = cur.fetchone()
        return f'''
title: {r[1]}
release_date : {r[4]}
vote_average : {r[5]}
'''
    def save_settings(self, user_id, date_start, date_end, rating, popularity, director_id=None):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM settings WHERE user_id = ?", (user_id,))
            cur.execute('''INSERT OR REPLACE INTO settings 
                    (user_id, release_date_strat, release_date_end, vote_average, popularity, director_id)
                    VALUES (?, ?, ?, ?, ?, ?)''', 
                    (user_id, date_start, date_end, rating, popularity, director_id))
            conn.commit()
                
    def reset_settings(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('DELETE FROM settings WHERE user_id = ?', (user_id,))
            cur.execute('DELETE FROM genre_settings WHERE user_id = ?', (user_id,))
            conn.commit()

    def get_genres(self):
        con = sqlite3.connect(self.database)
        with con:
            cur = con.cursor()
            cur.execute('SELECT * FROM genres')
            return cur.fetchall()
        
    def add_genre_setting(self, user_id, genre_id, neg_or_pos):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT * FROM genre_settings WHERE user_id = ? AND genre_id = ? AND neg_or_pos = ?', (user_id, genre_id, neg_or_pos))
            if not cur.fetchone():
                cur.execute('INSERT INTO genre_settings (user_id, genre_id, neg_or_pos) VALUES (?, ?, 1)', 
                        (user_id, genre_id))
                conn.commit()

    def get_genres_by_user_id(self, user_id):
        con = sqlite3.connect(self.database)
        with con:
            cur = con.cursor()
            cur.execute('''SELECT genre FROM genre_settings 
                        LEFT JOIN genres ON genres.genre_id = genre_settings.genre_id
                        WHERE user_id = ?''', (user_id,))
            return '\n'.join([x[0] for x in cur.fetchall()])
        
    def find_director(self, name):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('SELECT id, name FROM directors WHERE name LIKE ?', (f'%{name}%',))
            return cur.fetchall()
        
    def add_to_favorites(self, user_id, movie_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('INSERT OR IGNORE INTO favorites (user_id, movie_id) VALUES (?, ?)', 
                    (user_id, movie_id))
            conn.commit()

    def get_favorites(self, user_id):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute('''
                SELECT m.title, m.release_date, m.vote_average 
                FROM favorites f 
                JOIN movies m ON f.movie_id = m.id 
                WHERE f.user_id = ?
            ''', (user_id,))
            return cur.fetchall()
   
if __name__ == '__main__':
    m = DB_Manager(DATABASE)
    print(m.get_movie_by_settings(1))
