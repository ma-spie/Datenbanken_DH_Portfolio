#Ziel des Skriptes: Die Liedlänge über die Jahre hinweg im Streudiagramm darstellen
import sqlite3
import matplotlib.pyplot as plt

musicdb_connect = sqlite3.connect("musicdb.db")
musicdb_cur = musicdb_connect.cursor()

# SQL Anfrage: hier werden alle Jahrwerte mit "0" ignoriert, sowohl alle Liedlängen unter 60 Sekunden
musicdb_cur.execute("SELECT song_year, duration FROM song WHERE song_year > 1 AND duration >= 60")
data = musicdb_cur.fetchall()
# Die Tupel aus der SQL Anfrage mit zip in zwei Listen entpacken, die x Wert Liste mit den Daten aus song_year  und die y Wert Liste mit den Daten aus duration
x_year, y_duration = zip(*data)

#Berechnung der Durschnittslänge der Lieder pro Jahr
musicdb_cur.execute("SELECT song_year, AVG(duration) FROM song WHERE song_year > 1 AND duration >= 60 GROUP BY song_year")
avg_duration = musicdb_cur.fetchall()
xavg_year, yavg_duration = zip(*avg_duration)

#Streudiagramm erstellen und Durchschnitslänge aller Lieder darüberziehen
plt.scatter(x_year, y_duration, color = "purple", label = "Lieder")
plt.scatter(xavg_year, yavg_duration, color="yellow", label= "Durchschnittslänge aller Lieder eines Jahres")
plt.xticks(range(1920, 2015, 5), rotation=45)
plt.yticks(range(0, 3200, 120))
plt.title("Liedlänge im Verlauf der Zeit", fontweight = "bold")
plt.xlabel("Jahr")
plt.ylabel("Länge des Liedes in Sekunden")
plt.legend()
plt.grid()
#plt.savefig("scatterplot_Länge_Jahr.png")
plt.show()

musicdb_connect.close()