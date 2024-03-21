#Ziel des Skriptes: Der Music-Matcher empfliehlt Benutzern ähnliche Künstler anhand einer Suchanfrage.

import sqlite3

musicdb_connect = sqlite3.connect("musicdb.db")
musicdb_cur = musicdb_connect.cursor()

print("Willkommen beim Music-Matcher! Entdecke, welche Künstler ähnlich zueinander sind.\nDeine Künstlerempfehlungem warten schon auf dich!")


#SQL Anfrage bezieht sich auf die rekursive Beziehung zwischen den Tabellen artist und similarity
while True:
    search_user = input("Gib einen Künslter ein, den du magst (z.B. Muse, Depeche Mode, Nirvana):\nUm das Programm zu beenden gib ENDE ein.\n")
    if search_user == "ENDE":
        print("Wir hoffen du hattest Spaß mit dem Music-Matcher. Komm bald wieder! ")
        break
    elif search_user:
        sqlcmd = f"""SELECT a2.artist_name
                    FROM artist a1, artist a2, similarity s
                    WHERE a1.artist_id=s.target_artist AND a2.artist_id = s.similar_artist AND a1.artist_name = ?
                    """
        musicdb_cur.execute(sqlcmd, (search_user,))
        result = musicdb_cur.fetchall()
        if result: 
            print(f"Hier ist eine Liste von Künstlern, die ähnlich sind wie {search_user}: ")
            for row in result:
                print(row[0])
            print("Höre gerne rein! Oder versuche es noch einmal")
        else:
            print(f"Leider haben wir keine ähnlichen Künstler wie {search_user} gefunden.")
       
musicdb_connect.close()