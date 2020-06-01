import pytest
import datetime
from database import User, Contacts
from bson import ObjectId


def test_create_user():
    uname = hash(str(datetime.datetime.now()))
    u = {
        'username': uname,
        'password': 'test'
    }
    u = User(u)
    u.save()
    u['_id'] = ObjectId(u['_id'])
    assert u.find_by_username(uname) == u


def test_create_contact():
    _c = {
        'name': 'test',
        'emails': [
                {'address': "address", 'type': "home"},
        ],
        'phones': [
            {'number': "#######", 'type': "work"},
        ],
        'labels': ["Friends", "Family"]
    }
    c = Contacts(_c)
    c.save()
    assert Contacts().find_by_id(str(c['_id'])) == c


def test_compare_contacts():
    _c1 = {
        'name': 'test1',
        'emails': [
                {'address': "address", 'type': "home"},
        ],
        'phones': [
            {'number': "#######", 'type': "work"},
        ],
        'labels': ["Friends", "Family"]
    }
    _c2 = {
        'name': 'test2',
        'emails': [
                {'address': "address", 'type': "home"},
        ],
        'phones': [
            {'number': "#######", 'type': "work"},
        ],
        'labels': ["Friends", "Family"]
    }
    c1 = Contacts(_c1)
    c1.save()
    c2 = Contacts(_c2)
    c2.save()
    assert Contacts().find_by_id(str(c1['_id'])) == c1
    assert Contacts().find_by_id(str(c2['_id'])) == c2
    assert c1 != c2


def test_update_contact():
    _c = {
        'name': 'test',
        'phone number': 'test',
        'email': 'test',
    }
    c = Contacts(_c)
    c.save()
    assert Contacts().find_by_id(str(c['_id'])) == c

    c['name'] = 'new_name'
    c.save()
    assert Contacts().find_by_id(str(c['_id'])) == c
