from flask import Flask, render_template, request, redirect, session
import psycopg2 
from psycopg2 import Error
# from databse_connection import db
import re
import random
import string
import uuid

uniqid = uuid.uuid4()

app = Flask(__name__)

app.secret_key = "hello"

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



@app.route("/<slug>/<party_name>", methods=['GET', 'POST'])
def party(slug, party_name):
    if request.method == 'GET':
        url = slug + "/" + party_name
        print(url)
        db_conn = psycopg2.connect("dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")
        db_cur = db_conn.cursor()
        # string = ("SELECT * FROM parties where url = %s", (url,))
        db_cur.execute("SELECT * FROM parties where url = %s", (url,))
        print("Selecting all rows from parties row where the url given matches the url in selected the row")
        data = db_cur.fetchall()
        print("DATA BELOW")
        print(data)

        for x in data:
            item = data[0]
        pageId = item[0]
        print('pageId')
        print(pageId)
        session["pageId"] = pageId

        db_cur.execute("SELECT * FROM items where party_id = %s", (pageId,))
        page_items = db_cur.fetchall()
        print('All Items')
        print(page_items)

        db_cur.close()
        db_conn.close()
        # session["data"] = partyData
        return render_template('partypage.html', data=data, page_items=page_items)   
    else:
        # request.method == 'POST':
        if "pageId" in session:
            url = slug + "/" + party_name
            app.logger.info('Post')
            newItem = request.form['add_item']
            itemInfo = request.form['add_item_info']
            print('inside button')
            print(newItem)
            print(url)
            pageId = session["pageId"]
            print(pageId)
        # print(data)
            conn = psycopg2.connect("dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")
            cur = conn.cursor()
            cur.execute("INSERT into items (id, party_id, name, info, container_id) VALUES (%s, %s, %s, %s, %s)",(str(uniqid), pageId, str(newItem), str(itemInfo), str(uniqid)))
    # cur.execute("INSERT into parties (id, name, url, email, password) VALUES (%s, %s, %s, %s, %s)", (str(uniqid), str(party_name), str(generated_url), str(user_email), str(user_password)))
            conn.commit()
            cur.close()
            conn.close() 
        return render_template('partypage.html',)
        

if __name__ == "__main__":
    app.run(debug=True)

