from flask import Flask, render_template, request, redirect
import psycopg2 
from psycopg2 import Error
# from databse_connection import db
import re
import random
import string
import uuid

uniqid = uuid.uuid4()

app = Flask(__name__)

@app.route("/")
def home():
    return render_template('home.html', page_class="home") 
        

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        app.logger.info('Post')
        party_name = request.form['party_name']
        generated_url = request.form['generated_url']
        user_email = request.form['user_email']
        user_password = request.form['party_password']
        print(generated_url, party_name, user_email, user_password)

        conn = psycopg2.connect("dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")
        cur = conn.cursor()
        # cur.execute("CREATE TABLE test (id serial PRIMARY KEY, party_name varchar, generated_url varchar, user_email varchar, user_password varchar);")
        cur.execute("INSERT into parties (id, name, url, email, password) VALUES (%s, %s, %s, %s, %s)", (str(uniqid), str(party_name), str(generated_url), str(user_email), str(user_password)))
        # (party_name, generated_url, user_email, user_password)
        # ("TESTNAME", "WWW.TEST.COM", "TEST@TEST.COM", "TESTPWORD")

        conn.commit()
        cur.close()
        conn.close()

        return redirect(f'/{generated_url}', code=303)
        
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

        # except (Exception, psycopg2.Error) as error:
        #     print("Failed to insert record into mobile table", error)

        # finally:
        #     if connection:
        #         cursor.close()
        #         connection.close()
        #         print("Closed connections")



        # table = ( "INSERT INTO parties (id, party_name, generated_url, user_email, user_password), VALUES (%s, %s, %s, %s, %s)",
        #     (str[party_name], str[generated_url], str[user_email], str[user_password])
        # )
        # db.execute_query(table)
        # app.logger.info('Adding info')

        # return ""

    return render_template('signup.html', page_class="signup") 

    
        

if __name__ == "__main__":
    app.run(debug=True)

