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
                         popularity INTEGER   
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
                cur.execute('''SELECT id FROM movies 
                            WHERE
                            (release_date BETWEEN ? AND ?) and
                            (vote_average >= ?) and
                            (popularity >= ?)
                            ORDER BY random()''', (s[1], s[2], s[3], s[4]))
            else:
                cur.execute('SELECT id FROM movies ORDER BY random()')
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
    def save_settings(self, user_id, date_start, date_end, rating, popularity):
        conn = sqlite3.connect(self.database)
        with conn:
            cur = conn.cursor()
            cur.execute("DELETE FROM settings WHERE user_id = ?", (user_id,))
            cur.execute('''INSERT OR REPLACE INTO settings 
                    (user_id, release_date_strat, release_date_end, vote_average, popularity)
                    VALUES (?, ?, ?, ?, ?)''', 
                    (user_id, date_start, date_end, rating, popularity))
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
    
if __name__ == '__main__':
    m = DB_Manager(DATABASE)
    print(m.get_movie_by_settings(1))
