from flask import Flask, render_template, request, redirect, session
import psycopg2 
import psycopg2.extras
from psycopg2 import Error
# from databse_connection import db
import re
import random
import string
import uuid
import json

app = Flask(__name__)

app.secret_key = "hello"

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
    uniqid = uuid.uuid4()
    uniqid2 = uuid.uuid4()
    url_request = request.args
    # delete_id = request.args.get('delete')
    # delete_contents = request.args.to_dict().all('another')
    url = slug + "/" + party_name
    print(url)
    db_conn = psycopg2.connect("dbname=postgres user=postgres password=mysecretpassword port=2345 host=127.0.0.1")
    db_cur = db_conn.cursor(cursor_factory=psycopg2.extras.DictCursor)
    # string = ("SELECT * FROM parties where url = %s", (url,))
    db_cur.execute("SELECT * FROM parties where url = %s", (url,))
    print("Selecting all rows from parties row where the url given matches the url in selected the row")
    data = db_cur.fetchone()

    pageId = data["id"]

    if "delete" in request.args:
        # item_id = url_request["delete"]
        # item_contents = url_request["another"]
        # test = json.loads(delete_contents)
        print('********')   
        print('********')
        print(url_request)
        # print(url_request)
        print(type(url_request))
        # for k in delete_contents['another']:
        #     print(k)
        # db_cur.execute("DELETE from items where id = %s", (item_id,))

        # db_cur.execute("DELETE from items where container_id = %s", (item_id,))
        # db_conn.commit()
        # return redirect(f'/{url}', code=303)

    if request.method == 'POST':
        # request.method == 'POST':
        # if "pageId" in session:
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

    # print('page_items')
    # print(page_items)


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
        # print('test')
        # print(len(k['contents']))
        length = len(k['contents'])
        k.update({'length': length}) 
        # print(k)


    sorted_list = sorted(items_without_container_id, key=lambda s: s['length'], reverse=True)
    
    # test_id = request.form.get("container_id")
    # test_contents = request.form.get("content_id")
    # print(test_id)
    # print(test_contents)

    db_cur.close()
    db_conn.close()
    # session["data"] = partyData
    return render_template('partypage.html', data=data, page_items=page_items, root_items=sorted_list )
        

if __name__ == "__main__":
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.run(debug=True)

