# import psycopg2 as pg2

# try: 
#     connection = psycpg2.connect(
#             host = "lukeboat",
#             database ="bagofparty_local",
#             user = "postgres",
#             password = "mysecretpassword"
#         )

#     cursor = connection.cursor()

#     postgres_insert_query = """INSERT INTO parties (id, party_name, generated_url, user_email, user_password), VALUES (%s, %s, %s, %s, %s)"""
#     records_to_insert = (party_name, generated_url, user_email, user_password)
#     cursor.execute(postgres_insert_query, records_to_insert)

#     connection.commit()
#     count = cursor.rowcount
#     print(count, "INSERTED INFO")

#     except (Exception, psycopg2.Error) as error:
#         print("Failed to insert record into mobile table", error)

#     finally:
#         if connection:
#             cursor.close()
#             connection.close()
#             print("Closed connections")

# class Database:
#   def __init__(self, db, party_name, generated_url, user_email, user_password):
#     self.db = db
#     self.username = username
#     self.password = password
#     self.port = port
#     self.cur = None
#     self.conn = None
  
#   def connect(self):
#     self.conn = pg2.connect(database=self.db, user=self.user, password=self.password, port=self.port)
#     self.cur = self.conn.cursor()

#   def execute_query(self, query):
#     self.cur.execute(query)
#     self.conn.commit()

#   def close(self):
#     self.cur.close()
#     self.conn.close()
  
#   db = Database(db="bagofparties_local", user="postgres", pas="mysecretpassword", port=2345)
#   db.connect()

# con = psycpg2.connect(
#     host = "lukeboat",
#     database ="bagofparty_local",
#     user = "postgres",
#     password = "mysecretpassword"
# )

# cur = con.cursur()

# # cur.execute(
# #   INSERT INTO parties (id, party_name, generated_url, user_email, user_password),
# #   VALUES (%s, %s, %s, %s, %s),
# #   ()
# # )

# # rows = cur.fetchall()

# # for r in rows:
# #   print (f"id {r[0]} party_name {r[1]} generated_url {r[2]} user_email {r[3]} user_password {r[4]}")

# # cur.close()
# # con.close()