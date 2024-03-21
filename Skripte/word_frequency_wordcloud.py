#Ziel des Skriptes: die zehn häufigsten benutzen Wörter aus den Rezensionen auslesen, deren Häufigkeit bestimmen und eine Wordcloud der Rezensionen erstellen

import sqlite3
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from nltk.probability import FreqDist 
from wordcloud import WordCloud
import matplotlib.pyplot as plt  

print(f"Die Ausführung des Skripts dauert eine Weile...")


# aus der DB die Textinhalte der Rezensionen auswählen
musicdb_connect = sqlite3.connect("musicdb.db")
musicdb_cur = musicdb_connect.cursor()
musicdb_cur.execute("SELECT content_review FROM review")
reviews = musicdb_cur.fetchall()

#Stopwords downloaden und englische Stopwords auswählen
nltk.download('stopwords')
stop_words = set(stopwords.words("english"))

# Liste mit Wörtern, die weder Stopwords noch alphanumerische Zeichen sind, also Wörter, die wir für die Anfrage suchen
relevant_words = []

# Preprocessing: die Wörer der Rezensionen kleinschreiben und tokenisieren. Dann alle alphanumerischen Wörter außer stopwords in die Liste aufnehmen 
for review in reviews:
    words = word_tokenize(review[0].lower())  
    for word in words:
        if word.isalnum() and word not in stop_words: 
            relevant_words.append(word) 


#berechenen wie oft die zehn häufigsten Wörter vorkommen
word_frequency = FreqDist(relevant_words).most_common(10)
print(f"Die Zehn häufigsten Wörter mit Anzahl ihres Vorkommens: {word_frequency}")

# word cloud anlegen mit der Bibliothek von Mueller: https://github.com/amueller/word_cloud
wordcloud = WordCloud(width=800, height=400, background_color="white").generate(' '.join(relevant_words))

# word cloud anzeigen
plt.figure(figsize=(10, 5))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
#plt.savefig("word_cloud_album_reviews.png")
plt.show()