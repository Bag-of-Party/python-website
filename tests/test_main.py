import psycopg2 
import psycopg2.extras
from psycopg2 import Error
from app.main import home, signup, app, DATABASE_URL, bcrypt, uuid
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

    
def test_signup_post_database_insertion(monkeypatch):
  with app.test_request_context('/signup', method = "POST", data = {
    "party_name": "test",
    "generated_url": "2u3u/test",
    "user_email": "test",
    "party_password": "test"
  }):

    party_name = "test"
    generated_url = "2u3u/test"
    user_email = "test"
    user_password = "test"

    uniqid = uuid.uuid4()

    testuniqid = Mock(return_value=uniqid)

    monkeypatch.setattr("uuid.uuid4", testuniqid)

    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("TRUNCATE TABLE parties")
    db_conn.commit()
    signup()
    cur.execute("SELECT * from parties where url = '2u3u/test'")
    data = cur.fetchone()
    cur.close()
    db_conn.close()

    test_password = bcrypt.check_password_hash(data[4], user_password)

    print(data)

    assert data[0:4] == (str(uniqid), 'test', '2u3u/test', 'test')




# def test_signup_post_redirect(monkeypatch):
#   with app.test_request_context('signup'):
#     render_template = Mock()
    # monkeypatch.setattr("app.main.render")

  




