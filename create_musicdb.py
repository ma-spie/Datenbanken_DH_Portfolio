#Ziel des Skripts: Erstellen der notwendigen Tabellen und Attributen basierend auf dem relationalen Modell.

import sqlite3

#Datenbank initialisieren
musicdb_connect = sqlite3.connect("musicdb.db")
musicdb_cur = musicdb_connect.cursor()
print("Verbunden mit SQLite")                #Zwischentest

#wenn bestehende Tabellen existieren, diese löschen, damit man auf Wunsch die DB von neu aufbauen kann.
musicdb_cur.execute("DROP TABLE IF EXISTS artist")
musicdb_cur.execute("DROP TABLE IF EXISTS artist_tags")
musicdb_cur.execute("DROP TABLE IF EXISTS has_tags")
musicdb_cur.execute("DROP TABLE IF EXISTS similarity")
musicdb_cur.execute("DROP TABLE IF EXISTS song")
musicdb_cur.execute("DROP TABLE IF EXISTS album")
musicdb_cur.execute("DROP TABLE IF EXISTS review")
musicdb_cur.execute("DROP TABLE IF EXISTS author")

#Tabellen anlegen

musicdb_cur.execute('''CREATE TABLE artist (
            artist_id VARCHAR(25) PRIMARY KEY,
            artist_name VARCHAR(40),
            artist_popularity FLOAT, 
            artist_familiarity FLOAT
            )''') 

musicdb_cur.execute('''CREATE TABLE artist_tags (
            tag_id INT PRIMARY KEY,
            tag TEXT
            )''')

#Die Verknüpfungstabelle has_tags hat zwei Fremdschlüssel wegen der m:n Beziehung.
#zusätzlich muss ein zusammengesetzter Schlüssel (artist_id, tag_id) erstellt werden, damit jede Kombination dieser zwei Attribute nur einmal vorkommt
musicdb_cur.execute('''CREATE TABLE has_tags (
            artist_id VARCHAR(25),
            tag_id INT,
            FOREIGN KEY(artist_id) REFERENCES artist(artist_id),
            FOREIGN KEY(tag_id) REFERENCES tags(tag_id),
            PRIMARY KEY (artist_id, tag_id)
            )''')

musicdb_cur.execute('''CREATE TABLE similarity (
            target_artist VARCHAR(25), 
            similar_artist VARCHAR(25),
            FOREIGN KEY (target_artist) REFERENCES artist(artist_id),
            FOREIGN KEY (similar_artist) REFERENCES artist(artist_id),
            PRIMARY KEY (target_artist, similar_artist)
            )''')

#FOREIGN KEY REFERENCES stellt sicher, dass eine Verbindung zur artist und album Tabelle erstellt wird, auf die sich die Fremdschlüssel reviewed_in und artist_id beziehen.
musicdb_cur.execute('''CREATE TABLE song (
            track_id VARCHAR(25) PRIMARY KEY, 
            title TEXT, 
            song_year INT, 
            duration FLOAT, 
            artist_id VARCHAR,
            reviewed_in INT,
            FOREIGN KEY (artist_id) REFERENCES artist(artist_id),
            FOREIGN KEY (reviewed_in) REFERENCES album(review_id)
            )''')

musicdb_cur.execute('''CREATE TABLE album (
            review_id INT PRIMARY KEY,
            album_name TEXT,
            genre TEXT,
            album_year INT,
            label TEXT 
            )''')

musicdb_cur.execute('''CREATE TABLE review (
            review_id INT PRIMARY KEY, 
            content_review MEDIUMTEXT, 
            score FLOAT, 
            review_year INT, 
            url TEXT, 
            reviewed_artist VARCHAR(25),
            review_author VARCHAR(25),
            FOREIGN KEY (reviewed_artist) REFERENCES artist(artist_id),
            FOREIGN KEY (review_author) REFERENCES author(author_id)
            )''')

musicdb_cur.execute('''CREATE TABLE author (
            author_id VARCHAR(25) PRIMARY KEY, 
            author_name TEXT, 
            author_type TEXT
            )''')
print("Alle Tabellen wurden angelegt.")
musicdb_connect.commit()
musicdb_connect.close()