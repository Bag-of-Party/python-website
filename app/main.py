from flask import Flask, render_template, request, redirect, session
from flask_bcrypt import Bcrypt
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
bcrypt = Bcrypt(app)

DATABASE_URL = os.environ.get("DATABASE_URL", "dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")

app.secret_key = "hello"

@app.route("/")
def home():
    return render_template('home.html', page_class="home")
        
def create_party(group_id, party_name, generated_url, user_email, hash_password):
        conn = psycopg2.connect(DATABASE_URL)
        cur = conn.cursor()
        cur.execute("INSERT into parties (id, name, url, email, password) VALUES (%s, %s, %s, %s, %s)", (str(group_id), str(party_name), str(generated_url), str(user_email), str(hash_password)))
        conn.commit()
        cur.close()
        conn.close()


@app.route("/signup", methods=['GET', 'POST'])
def signup():
    uniqid = uuid.uuid4()
    uniqid2 = uuid.uuid4()
    if request.method == 'POST':
        app.logger.info('Post')
        # FIXME : handle empty pathways 
        # TODO : add ability to not add password
        party_name = request.form['party_name']
        generated_url = request.form['generated_url']
        user_email = request.form['user_email']
        user_password = request.form['party_password']
        
        hash_password = bcrypt.generate_password_hash(user_password).decode()
        session['group_id'] = uniqid

        create_party(session['group_id'], party_name, generated_url, user_email, hash_password)

        return redirect(f'/{generated_url}', code=303) 

    return render_template('signup.html', page_class="signup") 

def session_pop():
    session.pop('group_id', None)
    session.pop('group_name', None)
    session.pop('group_url', None)
    session.pop('group_password', None)

def session_create(data):
    session['group_id'] = data[0]
    session['group_name'] = data[1]
    session['group_url'] = data[2]
    session['group_email'] = data[3]
    session['group_password'] = data[4]


def login_data_check(group_email_input):
    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("SELECT * from parties where email = %s", (group_email_input,)) 
    data = cur.fetchone()
    return data

@app.route("/login", methods=['GET', 'POST'])
def login():
    session_pop()
    if request.method == 'POST':
        app.logger.info('Post')

        group_email_input = request.form['login_group_email']
        
        password_input = request.form['login_password']

        data = login_data_check(group_email_input)

        print(data)

        session_create(data)

        url = session['group_url']

        if bcrypt.check_password_hash(data[4], password_input):
            return redirect(f'/{url}', code=303) 
        return render_template('login.html')

    return render_template('login.html')



# def party_check(group_id):
#         db_conn = psycopg2.connect(DATABASE_URL)
#         db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
#         db_cur.execute("SELECT * FROM parties where id = %s", (str(session['group_id']),))
#         data = db_cur.fetchone()

@app.route("/<slug>/<party_name>", methods=['GET', 'POST'])
def party(slug, party_name):
    if 'group_id' in session:

        uniqid = uuid.uuid4()

        url_request = request.args
        url = slug + "/" + party_name

        group_id = session['group_id']

        db_conn = psycopg2.connect(DATABASE_URL)
        db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
        db_cur.execute("SELECT * FROM parties where id = %s", (str(session['group_id']),))
        data = db_cur.fetchone()

        pageId = session['group_id']

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
            db_cur.execute("INSERT into items (id, party_id, name, info, container_id) VALUES (%s, %s, %s, %s, %s)",(str(uniqid), str(pageId), str(newItem), str(itemInfo), container_id))
            db_conn.commit()
            db_cur.close()
            db_conn.close()
            return redirect(f'/{url}', code=303)

        db_cur.execute("SELECT * FROM items where party_id = %s", (str(pageId),))
        page_items = db_cur.fetchall()

        print("page_items")
        print(page_items)

        items_without_container_id = []
        items_by_id = {}
        items_names = []

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
            print(item['name'])
            items_names.append(item['name'])

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

        return render_template('partypage.html', data=data, page_items=page_items, root_items=sorted_list, names=items_names )
    return render_template('login.html')

@app.route("/action",methods=["POST","GET"])
def action():
    print("INN AACCTTIIOONN")
    uniqid = uuid.uuid4()
    db_conn = psycopg2.connect(DATABASE_URL)
    db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # db_conn = get_db()
    if request.method == 'POST':
        app.logger.info('Post')
        name = request.form['itemName']
        info = request.form['infoDetails']
        container = request.form.get('container')
        print(name)
        print(info)
        print(session['group_id'])
        print(session['group_name'])
        print(session['group_url'] )
        print(session['group_email'])
        print(session['group_password'])
        url = session['group_url']

        print("container_id")
        print(container)
        db_cur.execute("INSERT into items (id, party_id, name, info, container_id) VALUES (%s, %s, %s, %s, %s)",(str(uniqid), session['group_id'], str(name), str(info), container))
        db_conn.commit()
        db_cur.close()

        return redirect(f'/{url}', code=303)

@app.route("/contact")
def contact():
    return render_template('contact.html', page_class="contact")
    
@app.route("/terms")
def terms():
    return render_template('terms.html', page_class="terms")
 
if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)


