import psycopg2 
import psycopg2.extras
from app.main import DATABASE_URL, app



# @app.route("/api/parties")
# def parties():
#     db_conn = psycopg2.connect(DATABASE_URL)
#     db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#     db_cur.execute('SELECT * from parties')
#     data = db_cur.fetchall()
#     parties = []
#     for party in data:
#         parties.append(dict(party))
#     return parties