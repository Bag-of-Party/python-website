from flask import session
import psycopg2 
import psycopg2.extras
import pytest
import uuid
from psycopg2 import Error
from app.main import home, signup, login, create_party, party, add_items, login_data_check, app, DATABASE_URL, bcrypt
from unittest.mock import Mock


@pytest.fixture
def db_conn_parties():
    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("TRUNCATE TABLE parties")
    db_conn.commit()
    cur.close()
    yield db_conn
    db_conn.close()

@pytest.fixture
def db_conn_items():
    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("TRUNCATE TABLE items")
    db_conn.commit()
    cur.close()
    yield db_conn
    db_conn.close()


def test_home(monkeypatch):
    with app.test_request_context('/'):
        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)
        response = home()
        render_template.assert_called_with('home.html', page_class="home")

def test_signup_get(monkeypatch):
    with app.test_request_context('/signup'):
        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)
        response = signup()
        render_template.assert_called_with('signup.html', page_class="signup")


def test_signup_post_redirect(monkeypatch):
    with app.test_request_context('/signup', method = "POST", data = {
        "party_name": "test",
        "generated_url": "4u3u/test",
        "user_email": "test",
        "party_password": "test"
    }):
        response = signup()
        assert response.status_code == 303
        assert response.headers["location"] == "/4u3u/test"


def test_create_party_database_insertion(db_conn_parties):
    uniqid = uuid.uuid4()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", "test_password")
    cur = db_conn_parties.cursor()
    cur.execute("SELECT * from parties where url = '2u3u/test'")
    data = cur.fetchone()

    assert data == (str(uniqid), 'test_name', '2u3u/test', 'test_email', "test_password")

    
def test_signup_POSTreq_creates_party_input(monkeypatch):
    uniqid = uuid.uuid4()
    with app.test_request_context('/signup', method = "POST", data = {
        "party_name": "test_name",
        "generated_url": "2u3u/test",
        "user_email": "test_email",
        "party_password": "test"
    }):

        create_party = Mock()
        monkeypatch.setattr("app.main.create_party", create_party)

        # uniqid = uuid.uuid4()
        testuniqid = Mock(return_value = uniqid)
        monkeypatch.setattr("uuid.uuid4", testuniqid)

        
        hash_password = b"1234"
        test_password = Mock(return_value = hash_password)
        monkeypatch.setattr("app.main.bcrypt.generate_password_hash", test_password)

        signup()

        create_party.assert_called_with(uniqid, "test_name", "2u3u/test", "test_email", "1234")



def test_login_sucsess_routing(monkeypatch, db_conn_parties):
    uniqid = uuid.uuid4()
    with app.test_request_context('/login', method = "POST", data = {
        "login_group_email": "test_email",
        "login_password": "test_password"
    }):

        test_password = bcrypt.generate_password_hash("test_password").decode()

        create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

        response = login()
        print("response")
        print(response)
        assert response.status_code == 303
        assert response.headers["location"] == "/2u3u/test"


def test_login_fail_routing(monkeypatch, db_conn_parties):
    uniqid = uuid.uuid4()
    with app.test_request_context('/login', method = "POST", data = {
        "login_group_email": "test_email",
        "login_password": "fail_password"
    }):

        test_password = bcrypt.generate_password_hash("test_password").decode()

        create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        response = login()
        render_template.assert_called_with('login.html')


def test_login_bypass_routing(monkeypatch):
    with app.test_request_context('/login'):
        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)
        response = login()
        render_template.assert_called_with('login.html')


def test_login_data_check(db_conn_parties):
    uniqid = uuid.uuid4()

    test_password = bcrypt.generate_password_hash("test_password").decode()

    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

    data =  login_data_check("test_email")

    assert data == (str(uniqid), "test_name", '2u3u/test', 'test_email', test_password)


def test_login_fail_session_empty(monkeypatch, db_conn_parties):
    uniqid = uuid.uuid4()
    with app.test_request_context('/login', method = "POST", data = {
        "login_group_email": "test_email",
        "login_password": "fail_password"
    }):

        test_password = bcrypt.generate_password_hash("test_password").decode()

        create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        response = login()
        
        assert 'group_id' not in session
    

def test_party_page_routing_out_of_session(db_conn_parties, monkeypatch):
    with app.test_request_context("/1j5p/party_name"):
        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        response = party("1j5p", "party_name")

        render_template.assert_called_with('login.html')

def test_party_page_routing_in_session_no_items(db_conn_items, db_conn_parties, monkeypatch):
    uniqid = uuid.uuid4()
    test_password = bcrypt.generate_password_hash("test_password").decode()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)
    
    with app.test_request_context("/2u3u/test"):

        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        session['group_id'] = str(uniqid)

        party("2u3u", "test")

        render_template.assert_called_with('partypage.html', data= [str(uniqid), 'test_name', '2u3u/test', 'test_email', test_password], page_items=[], root_items=[], names=[])


def test_party_page_routing_in_session_with_items_no_contents(db_conn_items, db_conn_parties, monkeypatch):
    uniqid = uuid.uuid4()
    test_password = bcrypt.generate_password_hash("test_password").decode()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

    uniqid_container = uuid.uuid4()
    string_id = str(uniqid)
    add_items(str(uniqid_container), str(uniqid), "test_item", "test_info", None)
    
    with app.test_request_context("/2u3u/test"):

        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        session['group_id'] = str(uniqid)

        party("2u3u", "test")

        render_template.assert_called_with('partypage.html', data= [str(uniqid), 'test_name', '2u3u/test', 'test_email', test_password], page_items=[[str(uniqid_container), str(uniqid), "test_item", "test_info", None]], root_items=[{'id': str(uniqid_container), 'party_id': str(uniqid), 'name': 'test_item', 'info': 'test_info', 'container_id': None, 'contents': [], 'length': 0}], names=['test_item'])


def test_party_page_routing_in_session_with_items_with_contents(db_conn_items, db_conn_parties, monkeypatch):
    uniqid = uuid.uuid4()
    test_password = bcrypt.generate_password_hash("test_password").decode()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

    uniqid_container = uuid.uuid4()
    uniqid_container_inside = uuid.uuid4()
    uniqid_group = uuid.uuid4()
    uniqid_item_inside = uuid.uuid4()

    add_items(str(uniqid_container), str(uniqid), "test_item", "test_info", None)

    add_items(str(uniqid_container_inside), str(uniqid), "test_item_2", "test_info_2", str(uniqid_container))
    cur = db_conn_items.cursor()
    cur.execute("SELECT * from items where party_id = %s",(str(uniqid_group),))
    item_data = cur.fetchone()
    
    with app.test_request_context("/2u3u/test"):

        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        session['group_id'] = str(uniqid)

        party("2u3u", "test")

        render_template.assert_called_with('partypage.html', data=[str(uniqid), 'test_name', '2u3u/test', 'test_email', test_password], page_items=[[str(uniqid_container), str(uniqid), 'test_item', 'test_info', None], [str(uniqid_container_inside), str(uniqid), 'test_item_2', 'test_info_2', str(uniqid_container)]], root_items=[{'id': str(uniqid_container), 'party_id': str(uniqid), 'name': 'test_item', 'info': 'test_info', 'container_id': None, 'contents': [{'id': str(uniqid_container_inside), 'party_id': str(uniqid), 'name': 'test_item_2', 'info': 'test_info_2', 'container_id': str(uniqid_container), 'contents': []}], 'length': 1}], names=['test_item', 'test_item_2'])

# def test_party_page_routing_in_session_with_items(db_conn_items, db_conn_parties, monkeypatch):
#     uniqid = uuid.uuid4()
#     test_password = bcrypt.generate_password_hash("test_password").decode()
#     create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)
    
#     with app.test_request_context("/2u3u/test"):

#         render_template = Mock()
#         monkeypatch.setattr("app.main.render_template", render_template)

#         session['group_id'] = str(uniqid)

#         party("2u3u", "test")

#         render_template.assert_called_with('partypage.html', data= [str(uniqid), 'test_name', '2u3u/test', 'test_email', test_password], page_items=[], root_items=[], names=[])





# def test_add_items(db_conn_items, db_conn_parties):
#     create_party(uniqid, "test_name", "1j5p/party_name", "test_email", "test_password")

#     db_conn = psycopg2.connect(DATABASE_URL)
#     cur = db_conn.cursor()

#     # cur = db_conn_parties.cursor()
#     cur.execute("SELECT * from parties where url = '1j5p/party_name'")
#     data = cur.fetchone()
#     print("data")
#     print(data)

#     # with app.test_request_context('/1j5p/party_name', method = "POST", data = {
#     #     "add_item": "test_item",
#     #     "add_item_info": "test_info",
#     #     "container_id": uniqid_container
#     # }):

#     add_items(str(uniqid_container), str(uniqid), "test_item", "test_info", None)

#     cur.execute("SELECT * from parties where url = '1j5p/party_name'")
#     item_data = cur.fetchone()

#     assert data == (str(uniqid), 'test_name', '1j5p/party_name', 'test_email', "test_password")
#     assert item_data == (str(uniqid_container), str(uniqid), "test_item", "test_info")
    

def test_add_items_no_contents(db_conn_parties, db_conn_items):
    uniqid = uuid.uuid4()
    uniqid_container = uuid.uuid4()
    string_id = str(uniqid)
    add_items(str(uniqid_container), str(uniqid), "test_item", "test_info", None)
    cur = db_conn_items.cursor()
    cur.execute("SELECT * from items where party_id = %s",(str(uniqid),))
    item_data = cur.fetchone()

    assert item_data == (str(uniqid_container), str(uniqid), "test_item", "test_info", None)


def test_delete_item_no_contents_delete_redirect(db_conn_parties, db_conn_items):
    uniqid = uuid.uuid4()

    test_password = bcrypt.generate_password_hash("test_password").decode()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

    # uniqid_item = uuid.uuid4()
    uniqid_container = uuid.uuid4()
    string_id = str(uniqid)
    add_items(str(uniqid_container), str(uniqid), "test_item", "test_info", None)

    with app.test_request_context(f'/2u3u/test/?delete={uniqid}'):
        session['group_id'] = str(uniqid)
        response = party("2u3u", "test")
        print("response")
        print(response)
        assert response.status_code == 303
        assert response.headers["location"] == "/2u3u/test"

def test_delete_item_no_contents(db_conn_parties, db_conn_items):
    uniqid = uuid.uuid4()

    test_password = bcrypt.generate_password_hash("test_password").decode()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

    # uniqid_item = uuid.uuid4()
    uniqid_container = uuid.uuid4()
    string_id = str(uniqid)
    add_items(str(uniqid_container), str(uniqid), "test_item", "test_info", None)

    # with app.test_request_context('/login', method = "POST", data = {
    #     "login_group_email": "test_email",
    #     "login_password": "test_password"
    # }):
    #     login()

    # session data being lost so session need to be created before party call

    with app.test_request_context(f'/2u3u/test/?delete={uniqid}'):
        session['group_id'] = str(uniqid)
        # party("2u3u", "test")

        party("2u3u", "test")

        cur = db_conn_items.cursor()
        cur.execute("SELECT * from items where party_id = %s",(str(uniqid),))
        item_data = cur.fetchone()

        print("item_data")
        print(item_data)

        assert item_data != (str(uniqid_container), str(uniqid), 'test_item', 'test_info', None)


# FIXME this is not testing all the data, only paretnt level bing pulled 
def test_add_items_with_contents(db_conn_parties, db_conn_items):
    uniqid_container = uuid.uuid4()
    uniqid_container_inside = uuid.uuid4()
    uniqid_group = uuid.uuid4()
    uniqid_item_inside = uuid.uuid4()

    add_items(str(uniqid_container), str(uniqid_group), "test_item", "test_info", None)

    add_items(str(uniqid_container_inside), str(uniqid_group), "test_item_2", "test_info_2", str(uniqid_container))
    cur = db_conn_items.cursor()
    cur.execute("SELECT * from items where party_id = %s",(str(uniqid_group),))
    item_data = cur.fetchone()

    print("item_data")
    print(item_data)

    assert item_data == (str(uniqid_container), str(uniqid_group), "test_item", "test_info", None)

# def test_partpage_item_added_page_redirect(db_conn_parties, db_conn_items, monkeypatch):
#     uniqid = uuid.uuid4()
#     test_password = bcrypt.generate_password_hash("test_password").decode()
#     create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

#     with app.test_request_context("/2u3u/test", method = "POST", data = {
#         "add_item": "test_item",
#         "add_item_info": "test_info",
#         "container_id": None
#     }):
#         response = party("2u3u", "test")
#         # print("response")        
#         # print(response)  RETURNIUNG PAGE HTML      
#         assert response.status_code == 303
#         assert response.headers["location"] == "/2u3u/test"



