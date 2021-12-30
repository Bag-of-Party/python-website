from app.main import bcrypt, create_party, DATABASE_URL
from app.main import parties
import uuid
import psycopg2 
import psycopg2.extras
import pytest

@pytest.fixture
def db_conn_parties():
    db_conn = psycopg2.connect(DATABASE_URL)
    cur = db_conn.cursor()
    cur.execute("TRUNCATE TABLE parties")
    db_conn.commit()
    cur.close()
    yield db_conn
    db_conn.close()

def test_PARTIES_api_returns_all_parties(db_conn_parties):
    uniqid1 = uuid.uuid4()
    uniqid2 = uuid.uuid4()
    uniqid3 = uuid.uuid4()

    test_password_1 = bcrypt.generate_password_hash("test_password_1").decode()
    create_party(uniqid1, "test_name", "1u3u/test", "test_email", test_password_1)

    test_password_2 = bcrypt.generate_password_hash("test_password_2").decode()
    create_party(uniqid2, "test_name", "2u3u/test", "test_email", test_password_2)

    test_password_3 = bcrypt.generate_password_hash("test_password_3").decode()
    create_party(uniqid3, "test_name", "3u3u/test", "test_email", test_password_3)

    data = parties()

    assert data == [
            {"id" : str(uniqid1), "name" : "test_name", "url" : "1u3u/test", "email" : "test_email", "password" : test_password_1},
            {"id" : str(uniqid2), "name" : "test_name", "url" : "2u3u/test", "email" : "test_email", "password" : test_password_2},
            {"id" : str(uniqid3), "name" : "test_name", "url" : "3u3u/test", "email" : "test_email", "password" : test_password_3}
        ]