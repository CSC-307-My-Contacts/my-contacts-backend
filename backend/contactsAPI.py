from flask import Flask, Response
from flask import request
from flask import jsonify
from flask_cors import CORS
import random
import string
from database import User, Contacts

app = Flask(__name__)

# CORS stands for Cross Origin Requests.
CORS(app)  # Here we'll allow requests coming from any domain. Not recommended for production environment.


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def get_contacts():
    token = request.headers.get('token')

    user = User().find_by_token(token)

    if request.method == 'GET':
        return jsonify({'contacts': user.fetch_contacts()})

    if request.method == 'POST':
        contact = Contacts(request.get_json()['contact'])
        user['contact_list'].append(contact['uid'])
        contact.save()
        user.save()
        return jsonify(contact)

    if request.method == 'DELETE':
        uid = request.get_json()['uid']
        user['contact_list'] = list(filter(user['contact_list'], lambda u: u.uid == uid))
        contact.remove()
        user.save()
        return Response(status=204)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        requested_user = request.get_json()

        user = User().find_by_username(requested_user['username'])

        if not user:
            return Response(status=403)

        if requested_user['password'] == user['password']:
            return jsonify(user['token'])
        # resp.headers['WWW-Authenticate'] = 'Basic realm=Access to contacts'
        return Response(status=403)


@app.route('/create', methods=['POST'])
def create_user():
    if request.method == 'POST':
        user = User(request.get_json())

        possible_users = user.find_by_username(user['username'])
        if possible_users:
            return Response(status=403)

        user['token'] = hash(user['password'])
        user['contact_list'] = []
        user.save()

        return jsonify(user['token'])


if __name__ == "__main__":
    app.run()
