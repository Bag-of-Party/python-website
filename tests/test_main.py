from flask import session
import psycopg2 
import psycopg2.extras
import pytest
import uuid
from psycopg2 import Error
from app.main import home, signup, login, create_party, party, login_data_check, app, DATABASE_URL, bcrypt
from unittest.mock import Mock

uniqid = uuid.uuid4()

@pytest.fixture
def db_conn():
    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("TRUNCATE TABLE parties")
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


def test_create_party_database_insertion(db_conn):

    create_party(uniqid, "test_name", "2u3u/test", "test_email", "test_password")
    cur = db_conn.cursor()
    cur.execute("SELECT * from parties where url = '2u3u/test'")
    data = cur.fetchone()

    assert data == (str(uniqid), 'test_name', '2u3u/test', 'test_email', "test_password")

    
def test_signup_POSTreq_creates_party_input(monkeypatch):
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



def test_login_sucsess_routing(monkeypatch, db_conn):
    with app.test_request_context('/login', method = "POST", data = {
        "login_group_email": "test_email",
        "login_password": "test_password"
    }):

        test_password = bcrypt.generate_password_hash("test_password").decode()

        create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

        response = login()
        assert response.status_code == 303
        assert response.headers["location"] == "/2u3u/test"


def test_login_fail_routing(monkeypatch, db_conn):
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


def test_login_data_check(db_conn):

    test_password = bcrypt.generate_password_hash("test_password").decode()

    create_party(uniqid, "test_name", "2u3u/test", "test_email", test_password)

    data =  login_data_check("test_email")

    assert data == (str(uniqid), "test_name", '2u3u/test', 'test_email', test_password)


def test_login_fail_session_empty(monkeypatch, db_conn):
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
    

def test_party_page_routing_out_of_session(db_conn, monkeypatch):
    with app.test_request_context("/1j5p/party_name"):
        render_template = Mock()
        monkeypatch.setattr("app.main.render_template", render_template)

        response = party("1j5p", "party_name")

        render_template.assert_called_with('login.html')





# def test_party_page_gets_data(monkeypatch):
#     group_id = uniqid
#     session = Mock(return_value = group_id)
#     monkeypatch.setattr("app.main.group_id", session)

#     party('2u3u', 'test')

#     assert data == (str(uniqid), "test_name", '2u3u/test', 'test_email', 'test_password')





