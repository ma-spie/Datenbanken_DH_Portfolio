#Ziel des Skrips: SQL Anfragen formulieren, um interessante Sachverhalte und Beziehungen aus den Daten zu erschließen.

import sqlite3

# Diese Funktion elaubt ein effizientes und platzsparendes Ausführen der SQL Anfragen und beinhaltet alle DB Operationen. 
#Im Falle eines Auslesefehlers/eines leeren Datensatzes ist ein Prüfmechanismus vorgeschaltet.
def execute_sql(query):
    musicdb_connect = sqlite3.connect("musicdb.db")
    musicdb_cur = musicdb_connect.cursor()

    musicdb_cur.execute(query)
    result = musicdb_cur.fetchall()

    if not result:
        print(f"Es wurden keine Daten für die Anfrage gefunden.")
        musicdb_connect.close()
        exit()
    else:
        musicdb_connect.close()
        return result

#SQL Anfragen
'''
    Test: Durchschnittslänge der Rezensionen in Zeichen
	query1: Alle Künstler, deren Alben mit 10.0 Punkten bewertet wurden, nach Jahr sortiert
    query1a: Die top populärsten Künslter mit ihren durschnittlichen Bewertung und Tags
    query2: Autorenportait
    query3: Top 10 Genres mit der höchsten Anzahl der Rezensionen

'''

query_test = execute_sql("SELECT AVG(LENGTH(content_review)) as average_review_length FROM review")
print(f"Die Durchschnittslänge der Rezensionen umfasst {query_test} Zeichen.")


query1 = execute_sql("""SELECT DISTINCT r.score, a.artist_name, r.review_year, al.album_name, al.album_year
FROM review r, artist a, album al
WHERE r.score = 10 AND r.reviewed_artist=a.artist_id AND al.review_id=r.review_id
ORDER BY r.review_year ASC""")
print(f"Alle Künstler, deren Alben mit 10.0 Punkten bewertet wurden, nach Jahr sortiert: ")
for entry in query1:
    print(entry)


query1a = execute_sql("""SELECT DISTINCT a.artist_name, a.artist_popularity, AVG(r.score) AS average_score, t.tag
FROM review r, artist a, has_tags h, artist_tags t
WHERE r.reviewed_artist=a.artist_id AND a.artist_id=h.artist_id AND h.tag_id=t.tag_id
GROUP BY a.artist_name, a.artist_popularity
ORDER BY artist_popularity DESC
LIMIT 71""")
print(f"Top populärsten Künslter mit ihren durschnittlichen Bewertung und Tags: ")
for entry in query1a:
    print(entry)


query2 = execute_sql("""SELECT au.author_name, COUNT(*) AS num_reviews, au.author_type, AVG(r.score) AS average_score, MIN(r.score) as lowest_score, MAX(r.score) as highest_score
FROM review r, author au
WHERE r.review_author = au.author_id
GROUP BY au.author_name
ORDER BY num_reviews DESC
LIMIT 10""")
print("Autorenportrait: Autoren mit den meisten Reviews, Autorentyp, durschnittliche, niedrigste und höhste  Bewertung: ")
for entry in query2:
    print(entry)


query3 = execute_sql("""SELECT DISTINCT a.genre, COUNT(r.review_id) AS number_reviews
FROM album a, review r
WHERE a.review_id=r.review_id
GROUP BY a.genre
ORDER BY number_reviews DESC
LIMIT 10""")
print("Top 10 Genres mit der höchsten Anzahl der Rezensionen:")
for entry in query3:
    print(entry)