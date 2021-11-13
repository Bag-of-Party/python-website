from flask import Flask, render_template, request, redirect, session
import cryptography
from cryptography.fernet import Fernet
import psycopg2 
import psycopg2.extras
from psycopg2 import Error
import os
import re
import random
import string
import uuid
import json
import hashlib

app = Flask(__name__)

DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")

app.secret_key = "hello"

def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)

def load_key():
    return open("secret.key", "rb").read()

def encrypt_message(message):
    key = load_key()
    encoded_message = message.encode('utf-16')
    f = Fernet(key)
    print("fkey decript1")
    print(f)
    encrypted_message = f.encrypt(encoded_message)

    print(encrypted_message)
    return encrypted_message

def decrypt_message(encrypted_message):
    key = load_key()
    f = Fernet(key)
    print("fkey decript")
    print(f)
    decrypted_message = f.decrypt(encrypted_message)
    decrypted_message_decoded = decrypted_message.decode('utf-16')

    print(decrypted_message.decode())
    return decrypted_message_decoded

@app.route("/")
def home():
    return render_template('home.html', page_class="home") 
        

@app.route("/signup", methods=['GET', 'POST'])
def signup():
    uniqid = uuid.uuid4()
    uniqid2 = uuid.uuid4()
    if request.method == 'POST':
        app.logger.info('Post')
        party_name = request.form['party_name']
        generated_url = request.form['generated_url']
        user_email = request.form['user_email']
        user_password = request.form['party_password']
        print(generated_url, party_name, user_email, user_password)

        user_password = encrypt_message(user_password)

        print("test")
        print(user_password)

        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT into parties (id, name, url, email, password) VALUES (%s, %s, %s, %s, %s)", (str(uniqid), str(party_name), str(generated_url), str(user_email), str(user_password)))
        conn.commit()
        cur.close()
        conn.close()

        return redirect(f'/login', code=303)

    return render_template('signup.html', page_class="signup") 

@app.route("/login", methods=['GET', 'POST'])
def login():
    session.pop('group_id', None)
    session.pop('group_name', None)
    session.pop('group_url', None)
    session.pop('group_password', None)

    if request.method == 'POST':
        app.logger.info('Post')
        group_name_input = request.form['login_group_email']
        password_input = request.form['login_password']
        print(password_input, group_name_input)

        db_conn = psycopg2.connect(DATABASE_URL)
        cur = db_conn.cursor()
        cur.execute("SELECT * from parties where email = %s", (group_name_input,)) 
        data = cur.fetchone()
        print(data)       
        password = data[4]
        session['group_id'] = data[0]
        session['group_name'] = data[1]
        session['group_url'] = data[2]
        session['group_email'] = data[3]
        session['group_password'] = data[4]

        test_password = encrypt_message(password)
        print("TESTPASSWORD")
        print(test_password)


        # test = decrypt_message(password)

        # print("password")
        # print(test)

        if password_input == password:
            return redirect(f'/{data[2]}', code=303) 
        return render_template('login.html')


    return render_template('login.html')



@app.route("/<slug>/<party_name>", methods=['GET', 'POST'])
def party(slug, party_name):
    if 'group_password' in session:
        uniqid = uuid.uuid4()
        uniqid2 = uuid.uuid4()
        url_request = request.args
        url = slug + "/" + party_name
        print(url)

        db_conn = psycopg2.connect(DATABASE_URL)
        db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        db_cur.execute("SELECT * FROM parties where url = %s", (url,))
        print("Selecting all rows from parties row where the url given matches the url in selected the row")
        data = db_cur.fetchone()
        pageId = data["id"]

        if "delete" in request.args:
            item_id = url_request["delete"]
            db_cur.execute("DELETE from items where id = %s", (item_id,))
            db_conn.commit()
            return redirect(f'/{url}', code=303)

        if request.method == 'POST':
            app.logger.info('Post')
            newItem = request.form['add_item']
            itemInfo = request.form['add_item_info']
            print('inside button')
            print(newItem)
            print(url)
            print(pageId)
            container_id = request.form.get("container_id")
            db_cur.execute("INSERT into items (id, party_id, name, info, container_id) VALUES (%s, %s, %s, %s, %s)",(str(uniqid), pageId, str(newItem), str(itemInfo), container_id))
            db_conn.commit()
            db_cur.close()
            db_conn.close()
            return redirect(f'/{url}', code=303)

        db_cur.execute("SELECT * FROM items where party_id = %s", (pageId,))
        page_items = db_cur.fetchall()

        items_without_container_id = []
        items_by_id = {}

        for item in page_items:
            items_by_id[item['id']] = {
                'id': item['id'],
                'party_id': item['party_id'],
                'name': item['name'],
                'info': item['info'],
                'container_id': item['container_id'],
                'contents': []
            }

        for item in page_items:
            if item['container_id']:
                items_by_id[item['container_id']]['contents'].append(items_by_id[item['id']])
            else:
                items_without_container_id.append(items_by_id[item['id']])

        for k in items_without_container_id:
            length = len(k['contents'])
            k.update({'length': length}) 

        sorted_list = sorted(items_without_container_id, key=lambda s: s['length'], reverse=True)
        
        db_cur.close()
        db_conn.close()

        return render_template('partypage.html', data=data, page_items=page_items, root_items=sorted_list )
    return render_template('login.html')


@app.route("/contact")
def contact():
    return render_template('contact.html', page_class="contact")
    
@app.route("/terms")
def terms():
    return render_template('terms.html', page_class="terms")


if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)

