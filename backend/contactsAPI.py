from flask import Flask, Response, request, jsonify
from flask_cors import CORS

from database import User, Contacts

app = Flask(__name__)

# CORS stands for Cross Origin Requests.
CORS(app)  # Here we'll allow requests coming from any domain. Not recommended for production environment.


@app.route('/', methods=['GET', 'POST', 'DELETE'])
def get_contacts():
    token = request.headers.get('token')

    user = User().find_by_token(token)

    if request.method == 'GET':
        return jsonify({'contacts': sorted(user.fetch_contacts(), key=lambda c: c['name'])})

    if request.method == 'POST':
        # Create contact
        contact = Contacts(request.get_json()['contact'])
        contact.save()

        if contact['_id'] not in user['contact_list']:
            user['contact_list'].append(contact['_id'])
        user.save()
        return jsonify({'contact': contact})

    if request.method == 'DELETE':
        _id = request.get_json()['_id']
        # Remove contact from users list
        contact = Contacts().find_by_id(_id)
        user['contact_list'] = list(filter(lambda id: id != _id, user['contact_list']))
        # Delete contact from database. TODO test
        contact.remove()
        user.save()
        return Response(status=204)


@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        requested_user = request.get_json()

        user = User().find_by_username(requested_user['username'])

        if not user:
            # Username not found
            return Response(status=403)

        if requested_user['password'] == user['password']:
            return jsonify({'token': user['token']})
        # Invalid password
        return Response(status=403)


@app.route('/create', methods=['POST'])
def create_user():
    if request.method == 'POST':
        # Create user object
        user = User(request.get_json())

        possible_users = user.find_by_username(user['username'])
        # Check if a user already exists with this username
        if possible_users:
            return Response(status=403)

        user['token'] = str(hash(user['password']))
        user['contact_list'] = []
        user.save()

        return jsonify({'token': user['token']})


@app.route('/csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    lines = file.readlines()
    for line in lines:
        print(line)
    return Response(status=200)


if __name__ == "__main__":
    app.run()
