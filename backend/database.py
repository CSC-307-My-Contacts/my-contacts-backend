import pymongo
from bson import ObjectId


class Model(dict):
    """
    A simple model that wraps mongodb document
    """
    __getattr__ = dict.get
    __delattr__ = dict.__delitem__
    __setattr__ = dict.__setitem__

    def save(self):
        if not self._id:
            self.collection.insert_one(self)
        else:
            self._id = ObjectId(self._id)
            self.collection.update(
                { "_id": ObjectId(self._id) }, self)
        self._id = str(self._id)

    def reload(self):
        if self._id:
            result = self.collection.find_one({"_id": ObjectId(self._id)})
            if result :
                self.update(result)
                self._id = str(self._id)
                return True
        return False

    def remove(self):
        if self._id:
            resp = self.collection.remove({"_id": ObjectId(self._id)})
            self.clear()
            return resp



class User(Model):
    db_client = pymongo.MongoClient('localhost', 27017)
    collection = db_client["MyContactsApp"]["users_list"]

    def find_by_username(self, username):
        u = self.collection.find_one({"username": username})
        if u:
            return User(u)
        return None

    def find_by_token(self, token):
        u = User(self.collection.find_one({"token": token}))
        if u:
            return u
        return None

    def fetch_contacts(self):
        return Contacts().find_by_ids(self['contact_list'])




class Contacts(Model):
    db_client = pymongo.MongoClient('localhost', 27017)
    collection = db_client["MyContactsApp"]["contacts_list"]

    def find_by_id(self, id):
        c = self.collection.find_one({"_id": ObjectId(id)})
        if c:
            c['_id'] = str(c['_id'])
            return Contacts(c)

    def find_by_ids(self, ids):
        contacts = []
        for id in ids:
            c = self.collection.find_one({'_id': ObjectId(id)})
            if c:
                c['_id'] = str(c['_id'])
                contacts.append(c)
        return contacts

