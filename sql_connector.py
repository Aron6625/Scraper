import mysql.connector

mydb = mysql.connector.connect(
  host="127.0.1.1",
  user="root",
  password="34353435",
  database="xcelence"
)

table='binary_dictionary'

cursor = mydb.cursor()
cursor.execute(f'SELECT id, primary_ES FROM {table} LIMIT 2')

myresult = cursor.fetchall()

for x in myresult:
  translation = translator.translate(x[1])
  translation = translation.replace('&#39;', "'") 
  cursor.execute(
    f'UPDATE {table} SET primary_CA = %s WHERE id = %s',
    (translation, x[0])
  )

  print(f"{table}:  {x[0]}  {translation}  ✓")

mydb.commit()
