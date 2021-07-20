import psycpg2

con = psycpg2.connect(
    host = "lukeboat",
    database ="bagofparty_local",
    user = "postgres",
    password = "mysecretpassword"
)

cur = con.cursur()

cur.execute(
  INSERT INTO parties (id, party_name, generated_url, user_email, user_password),
  VALUES (%s, %s, %s, %s, %s),
  ()
)

rows = cur.fetchall()

for r in rows:
  print (f"id {r[0]} party_name {r[1]} generated_url {r[2]} user_email {r[3]} user_password {r[4]}")

cur.close()
con.close()