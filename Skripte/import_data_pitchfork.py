#Ziel des Skripts: Importieren der Daten aus der Pitchforkdatenbank in die Tabellen author, album und review.

import sqlite3

musicdb_connect = sqlite3.connect("musicdb.db")
musicdb_cur = musicdb_connect.cursor()

#Verbinden mit den Datenbanken, aus denen Daten exportiert werden sollen
pitchfork_connect = sqlite3.connect("pitchfork_reviews.sqlite")
pitchfork_cur = pitchfork_connect.cursor()

trackmetadata_connect = sqlite3.connect("track_metadata.db")
trackmetadata_cur = trackmetadata_connect.cursor()
print("Verbunden mit SQLite") 


#--- 1. author Tabelle befüllen ---
#Daten aus der Pitchfork Datenbank nehmen  
pitchfork_cur.execute("SELECT DISTINCT author, author_type FROM reviews")
author_data = pitchfork_cur.fetchall()

# Liste mit den Daten aus der Pitchfork DB, die statt den Placeholdern genutzt werden sollen inkl. einer manuellen author_id angefangen bei 1
insert_data = []
for i, (author, author_type) in enumerate(author_data):
    author_id = str(i + 1)
    insert_data.append((author_id, author, author_type))       

#INSERT Anfrage mit placeholdern 
sqlcmd = "INSERT OR IGNORE INTO author (author_id, author_name, author_type) VALUES (?, ?, ?)" 
musicdb_cur.executemany(sqlcmd, insert_data) 
musicdb_connect.commit()
print(f"Insgesamt wurden {len(insert_data)} Zeilen in die Tabelle author erfolgreich eingefügt.")


#--- 2. album Tabelle befüllen ---
#Entnehmen der benötigten Daten aus der Pitchfork DB. dazu Verknüpfung über alle benötigten Tabellen mit dem Schlüssel reviewid
pitchfork_cur.execute('''SELECT reviews.reviewid, reviews.title, genres.genre, years.year, labels.label
                    FROM reviews, years, genres, labels
                    WHERE reviews.reviewid = years.reviewid
                    AND reviews.reviewid = genres.reviewid
                    AND reviews.reviewid = labels.reviewid 
                    ''')

album_data = pitchfork_cur.fetchall()

#album_data in die album Tabelle einfügen
sqlcmd = "INSERT OR IGNORE INTO ALBUM (review_id, album_name, genre, album_year, label) VALUES (?, ?, ?, ?, ?)"
musicdb_cur.executemany(sqlcmd, album_data)
musicdb_connect.commit()
print(f"Insgesamt wurden {len(album_data)} Zeilen in die Tabelle album erfolgreich eingefügt.")


# ---3. review Tabelle befüllen---
#notwendige Daten aus den Tabellen der Pitchfork Datenbank holen
pitchfork_cur.execute('''SELECT reviews.reviewid, content.content, reviews.score, reviews.pub_year, reviews.url, reviews.author
                FROM reviews, content
                WHERE reviews.reviewid = content.reviewid
                        ''')
review_data = pitchfork_cur.fetchall()

musicdb_cur.execute("SELECT author_name, author_id FROM author")
author_data = musicdb_cur.fetchall()

#--3a: review_author (und danach alle anderen Spalten außer reviewed_artist) befüllen--
# Ein Wörtervuch erstellen, indem author_name und author_id von der author Tabelle zum Wörterbuchpaar werden.
author_dict = {}
for author_name, author_id in author_data:
    author_dict[author_name] = author_id

#aus review_data den Autornamen mit dem Autornamen in der author_dict abgleichen und bei Treffer statt dem Autornamen die author_id in die Liste aufnehmen
review_data_with_author_id = []
for review in review_data:
    review_id, content, score, review_year, url, author = review
    if author in author_dict:
        author_id = author_dict[author] 
        review_data_with_author_id.append((review_id, content, score, review_year, url, author_id))

# review_data in die review Tabelle einfügen
sqlcmd = "INSERT OR IGNORE INTO review (review_id, content_review, score, review_year, url, review_author) VALUES (?, ?, ?, ?, ?, ?)"
musicdb_cur.executemany(sqlcmd, review_data_with_author_id)
musicdb_connect.commit()
print(f"Insgesamt wurden {len(review_data_with_author_id)} Zeilen in die Spalte review_author aus der Tabelle review erfolgreich eingefügt")

#--3b reviewed_artist befüllen--
# aus der Pitchfork DB und der trackmetadata DB die notwendigen Attibute rausholen. 
pitchfork_cur.execute("SELECT reviewid, artist FROM reviews")
pitchfork_artist_data = pitchfork_cur.fetchall()

trackmetadata_cur.execute("SELECT artist_id, artist_name FROM songs")
artist_data = trackmetadata_cur.fetchall()

# Wörterbuch, um artist names mit artist_id zu paaren. Für die Zusammenführung der artist names ist es wichtig sie durch Kleinschreibung zu normalisieren.
artistname_dict = {}                              
for artist_id, artist_name in artist_data:
    lower_artist_nametrack = artist_name.lower()
    artistname_dict[lower_artist_nametrack] = artist_id

# statt artist name die artist id verwenden: wenn in der artist_dict ein artist Name mit einem artist Namen aus der Pitchfork DB übereinstimmt, wird von diesem Artist die artist_id aus dem dict geholt 
for review_id, artist in pitchfork_artist_data:
    lower_artist_namepitchfork = artist.lower()   
    reviewed_artist_id = artistname_dict.get(lower_artist_namepitchfork)  
    musicdb_cur.execute("UPDATE OR IGNORE review SET reviewed_artist = ? WHERE review_id = ?", (reviewed_artist_id, review_id)) 
        
musicdb_connect.commit()

#die Anzahl der aktualisierten reviewed_artist Zeilen berechnen
musicdb_cur.execute("SELECT COUNT(reviewed_artist) FROM review WHERE reviewed_artist IS NOT NULL")
row_count = musicdb_cur.fetchone()[0]
print(f"Insgesamt wurden {row_count} Zeilen in die Spalte reviewed_artist aus der Tabelle review erfolgreich eingefügt.")


musicdb_connect.close()
pitchfork_connect.close()
trackmetadata_connect.close()