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
        return jsonify({'contacts': user.fetch_contacts()})


    if request.method == 'POST':
        # Create contact
        contact = Contacts(request.get_json()['contact'])
        contact.save()
        # Hack
        user['contact_list'].append(contact['_id'])
        user.save()
        return jsonify({'contact':contact})

    if request.method == 'DELETE':
        _id = request.get_json()['uid']
        # Remove contact from users list
        user['contact_list'] = list(filter(user['contact_list'], lambda u: str(u._id) == _id))
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
            return jsonify({'token':user['token']})
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

        return jsonify({'token' : user['token']})

if __name__ == "__main__":
    app.run()
