import psycopg2 
import psycopg2.extras
from psycopg2 import Error
from app.main import home, signup, create_party, app, DATABASE_URL, bcrypt, uuid
from unittest.mock import Mock

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


def test_create_party_database_insertion():
    uniqid = uuid.uuid4()

    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("TRUNCATE TABLE parties")
    db_conn.commit()
    create_party(uniqid, "test_name", "2u3u/test", "test_email", "test_password")
    cur.execute("SELECT * from parties where url = '2u3u/test'")
    data = cur.fetchone()
    cur.close()
    db_conn.close()

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

    uniqid = uuid.uuid4()
    testuniqid = Mock(return_value = uniqid)
    monkeypatch.setattr("uuid.uuid4", testuniqid)

    
    hash_password = b"1234"
    test_password = Mock(return_value = hash_password)
    monkeypatch.setattr("app.main.bcrypt.generate_password_hash", test_password)

    signup()

    create_party.assert_called_with(uniqid, "test_name", "2u3u/test", "test_email", "1234")


# def test_signup_post_redirect(monkeypatch):
#   with app.test_request_context('signup'):
#     render_template = Mock()
    # monkeypatch.setattr("app.main.render")

  




