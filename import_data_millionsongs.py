#Ziel des Skripts: Importieren der Daten aus den 3 Millionsong Datenbanken in die song, artist_tags, artist, artist_similarity, has_tags Tabellen.

import sqlite3

musicdb_connect = sqlite3.connect("musicdb.db")
musicdb_cur = musicdb_connect.cursor()

#Verbinden mit den Datenbanken aus denen Daten exportiert werden sollen
trackmetadata_connect = sqlite3.connect("track_metadata.db")
trackmetadata_cur = trackmetadata_connect.cursor()

artistterm_connect = sqlite3.connect("artist_term.db")
artistterm_cur = artistterm_connect.cursor()

artistsimilarity_connect = sqlite3.connect("artist_similarity.db")
artistsimilarity_cur = artistsimilarity_connect.cursor()

print("Verbunden mit SQLite")


# ---1. song Tabelle befüllen

trackmetadata_cur.execute("SELECT track_id, title, year, duration, artist_id FROM songs")
track_data = trackmetadata_cur.fetchall()

sqlcmd = "INSERT OR IGNORE INTO song (track_id, title, song_year, duration, artist_id) VALUES (?, ?, ?, ?, ?)"
musicdb_cur.executemany(sqlcmd, track_data)
musicdb_connect.commit()
print(f"Insgesamt wurden {len(track_data)} Zeilen in die song Tabelle erfolgreich eingefügt.")

# --1a. Fremdschlüssel reviewed_in befüllen, dazu Albumnamen aus der trackmetadata DB und aus der Musik DB zusammenführen und deren review_id als reviewed_in benutzen.
musicdb_cur.execute("SELECT review_id, LOWER(album_name) FROM album")
album_data = musicdb_cur.fetchall()

trackmetadata_cur.execute("SELECT track_id, LOWER(release) FROM songs")
track_release = trackmetadata_cur.fetchall()

# Wörterbuch: paart album_name mit review_id
album_dict = {}
for review_id, album_name in album_data:
    album_dict[album_name] = review_id

# von den gleichgeschriebenen Albumnamen wird diejenige review_id in die Spalte reviewed_in integriert, wo die track_id von Musik Db und Trackmetadata Db übereinstimmen.
for track_id, release in track_release:
    reviewed_in = album_dict.get(release)
    musicdb_cur.execute("UPDATE OR IGNORE song SET reviewed_in = ? WHERE track_id = ?", (reviewed_in, track_id))
musicdb_connect.commit()

#die Anzahl der aktualisierten reviewed_in Zeilen berechnen
musicdb_cur.execute("SELECT COUNT(DISTINCT reviewed_in) FROM song WHERE reviewed_in IS NOT NULL")
row_count = musicdb_cur.fetchone()[0]
print(f"Insgesamt wurden {row_count} Zeilen in die Spalte reviewed_in aus der Tabelle song erfolgreich hinzugefügt.")


# ---2. artist_tags Tabelle befüllen---

artistterm_cur.execute("SELECT DISTINCT mbtag FROM mbtags")
mbtags_data = artistterm_cur.fetchall()

# manuelle tag_id erstellen und zusammen mit den mbtag Werten (angefangen bei dem ersten Element) in eine Liste bringen
insert_data = []
for i, mbtag in enumerate(mbtags_data):
    mbtag = mbtag[0]
    tag_id = str(i + 1)      
    insert_data.append((tag_id, mbtag))

sqlcmd = "INSERT OR IGNORE INTO artist_tags (tag_id, tag) VALUES (?, ?)"
musicdb_cur.executemany(sqlcmd, insert_data)
musicdb_connect.commit()
print(f"Insgesamt wurden {len(insert_data)} Zeilen in die Tabelle artist_tags erfolgreich eingefügt.")


# ---3. artist Tabelle befüllen---

trackmetadata_cur.execute("SELECT artist_id, artist_name, artist_hotttnesss, artist_familiarity FROM songs")
artist_data = trackmetadata_cur.fetchall()

sqlcmd = "INSERT OR IGNORE INTO artist (artist_id, artist_name, artist_popularity, artist_familiarity) VALUES (?, ?, ?, ?)"
musicdb_cur.executemany(sqlcmd, artist_data)
musicdb_connect.commit()

print(f"Insgesamt wurden {len(artist_data)} Zeilen in die Tabelle artist erfolgreich eingefügt.")


# ---4. artist_similarity Tabelle befüllen---

artistsimilarity_cur.execute("SELECT target, similar FROM similarity")
similarity_data = artistsimilarity_cur.fetchall()

sqlcmd = "INSERT OR IGNORE INTO similarity (target_artist, similar_artist) VALUES (?, ?)"
musicdb_cur.executemany(sqlcmd, similarity_data)
musicdb_connect.commit()
print(f"Insgesamt wurden {len(similarity_data)} Zeilen in die Tabelle similarity erfolgreich eingefügt.")


# ---5. has_tags Tabelle befüllen---

artistterm_cur.execute("SELECT artist_id, mbtag FROM artist_mbtag")
artistterm_data =artistterm_cur.fetchall()

musicdb_cur.execute("SELECT tag_id, tag FROM artist_tags")
musicdb_tagdata = musicdb_cur.fetchall()

#Wörterbuch, wo tag mit tag_id gepaart wird
tag_dict ={}
for tag_id, tag in musicdb_tagdata:
    tag_dict[tag] = tag_id

# mbtag durch tag_id ersetzen: wenn ein tag sowohl in der artistterm Db als auch in der music DB vorkommt, wird die entsprechende tag_id aus dem Wöterbuch genommen und in die has_tags Tabelle eingesetzt.
has_tags_data = []                   
for artist_id, mbtag in artistterm_data:       
    if mbtag in tag_dict:           
        has_tags_data.append((artist_id, tag_dict[mbtag]))       

sqlcmd = "INSERT OR IGNORE INTO has_tags (artist_id, tag_id) VALUES (?, ?)"
musicdb_cur.executemany(sqlcmd, has_tags_data)
musicdb_connect.commit()
print(f"Insgesamt wurden {len(has_tags_data)} Zeilen in die Tabelle has_tags erfolgreich eingefügt.")


musicdb_connect.close()
trackmetadata_connect.close()
artistterm_connect.close()
artistsimilarity_connect.close()