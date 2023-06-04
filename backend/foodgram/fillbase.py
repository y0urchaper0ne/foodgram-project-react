import csv
import sqlite3

con = sqlite3.connect(r'/Users/ilya/Dev/foodgram-project-react/backend/foodgram/db.sqlite3')
cur = con.cursor()
with open('/Users/ilya/Dev/foodgram-project-react/backend/foodgram/ingredients.csv', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    to_db = []
    for row in reader:
        print(f'Добавляем строку {row["name"]}, {row["measurement_unit"]}')
        to_db.append((row['name'], row['measurement_unit']))

cur.executemany('INSERT or IGNORE INTO recipe_ingredients (name, measurement_unit) VALUES (?, ?);', to_db)
con.commit()
con.close()
