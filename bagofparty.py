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
        cur.execute("INSERT into parties (id, name, url, email, password) VALUES (%s, %s, %s, %s, %s)", (str(uniqid), str(party_name), str(generated_url), str(user_email), str(user_password)))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(f'/{generated_url}', code=303)

    return render_template('signup.html', page_class="signup") 



@app.route("/<slug>/<party_name>")
def party(slug, party_name):
    url = slug + party_name
    conn = psycopg2.connect("dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")
    cur = conn.cursor()
    cur.execute("select * from parties where url = %s", (url,))
    print("Selecting all rows from parties row where the url given matches the url in selected the row")
    records = cur.fetchall()

    return render_template('partypage.html', page_class="partypage")    
        

if __name__ == "__main__":
    app.run(debug=True)

