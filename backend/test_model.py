import pytest

from database import User
from contactsAPI import *
import io


@pytest.fixture
def client():
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client

def test_test_delete(client):
    # This test case is needed to rerun the tests on your local machine.
    # Because the test creates a testing user, we must ensure the test user
    # does not already have data associated with it. This is not a problem on Travis.
    rv = client.post('/create', json={
        'username': 'test',
        'password': 'test'})
    if rv.status_code == 403:
        u = User().find_by_username('test')
        u.remove()

    assert True

def get_token(client):
    rv = client.post('/login', json={
        'username': 'test',
        'password': 'test'})
    return rv.get_json()['token']

def get_contact(client):
    token = get_token(client)
    rv = client.get('/', headers={'token': token})
    return rv.get_json()['contacts'][0]

def test_create_account(client):
    u = User().find_by_username('test')
    if u:
        u.remove()
    rv = client.post('/create', json={
        'username': 'test',
        'password': 'test'})

    assert rv.status_code == 200
    assert rv.get_json()['token']


def test_dup_account(client):
    rv = client.post('/create', json={
        'username': 'test',
        'password': 'test'})
    assert rv.status_code == 403


def test_login(client):
    rv = client.post('/login', json={
        'username': 'test',
        'password': 'test'})
    assert rv.get_json()['token']

def test_invalid_login(client):
    rv = client.post('/login', json={
        'username': 'nonexistant',
        'password': 'nonexistant'})

    assert rv.status_code == 403

def test_invalid_pw(client):
    rv = client.post('/login', json={
        'username': 'test',
        'password': 'nonexistant'})

    assert rv.status_code == 403


def test_create_contact(client):
    token = get_token(client)
    rv = client.post('/', headers={'token': token}, json={
        'contact': {'name': 'test',
                   'emails': [
                       {'address': "address", 'type': "home"},
                   ],
                   'phones': [
                       {'number': "#######", 'type': "work"},
                   ],
                   'labels': ["Friends", "Family"]
                   }
    })
    assert rv.status_code == 200

def test_get_contacts(client):
    token = get_token(client)
    rv = client.get('/', headers={'token': token})
    assert rv.status_code == 200
    assert b'contacts' in rv.data

def test_delete_contact(client):
    token = get_token(client)
    rv = client.get('/', headers={'token': token})
    id = rv.get_json()['contacts'][0]['_id']
    assert id
    rv = client.delete('/', headers={'token':token}, json={
        '_id': str(id)})
    assert rv.status_code == 204

def test_create_contact_after_delete(client):
    token = get_token(client)
    rv = client.post('/', headers={'token': token}, json={
        'contact': {'name': 'test',
                   'emails': [
                       {'address': "address", 'type': "home"},
                   ],
                   'phones': [
                       {'number': "#######", 'type': "work"},
                   ],
                   'labels': ["Friends", "Family"]
                   }
    })
    assert rv.status_code == 200

def test_img(client):
    c = get_contact(client)
    token = get_token(client)
    data = {'file': (io.BytesIO(b'test'), 'test_file.jpg'),
    '_id': c['_id']}

    rv = client.post('/img', headers={'token': token},
            data=data,
            content_type='multipart/form-data'
        )

    assert rv.status_code == 200

def test_get_img(client):
    rv = client.get('/img/test.jpg')
    assert rv.status_code == 200

def test_google_csv(client):
    token = get_token(client)
    data = {'file': (open('./test_files/contacts-google.csv', "rb"), 'contacts-google.csv')}

    rv = client.post('/csv', headers={'token': token},
            data=data,
            content_type='multipart/form-data'
        )
    assert rv.status_code == 200
def test_outlook_csv(client):
    token = get_token(client)
    data = {'file': (open('./test_files/contacts-outlook.csv', "rb"), 'contacts-outlook.csv')}

    rv = client.post('/csv', headers={'token': token},
            data=data,
            content_type='multipart/form-data'
        )
    assert rv.status_code == 200

def test_bad_csv(client):
    token = get_token(client)
    data = {'file': (open('./test_files/contacts-bad.csv', "rb"), 'contacts-bad.csv')}

    rv = client.post('/csv', headers={'token': token},
            data=data,
            content_type='multipart/form-data'
        )
    assert rv.status_code == 422
