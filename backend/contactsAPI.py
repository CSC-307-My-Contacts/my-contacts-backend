import io
import os


from flask import Flask, Response, request, jsonify, send_from_directory
from flask_cors import CORS
from csv import reader

from database import User, Contacts
from datetime import datetime

UPLOAD_FOLDER = 'uploads'
app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

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


@app.route('/img', methods=['POST'])
def image():
    if request.method == 'POST':
        token = request.headers.get('token')
        _id = request.form.get('_id')
        user = User().find_by_token(token)
        contact = Contacts().find_by_id(_id)
       
        # Should never occur
        #if contact['_id'] not in user['contact_list']:
        #    return Response(status=403)

        image_file = request.files['file']
        image_type = os.path.basename(image_file.filename).split(".")[-1]
        hashed_name = f"{hash(_id)!s}{hash(datetime.now().strftime('%d'))!s}.{image_type}"
        image_file.save(os.path.join(os.getcwd(), app.config['UPLOAD_FOLDER'], hashed_name))
        contact['image'] = {'type': 'hosted', 'url': f"img/{hashed_name}"}
        contact.save()
        return jsonify({'contact': contact}), 200


@app.route('/img/<filename>', methods=['GET'])
def get_image(filename):
    if request.method == 'GET':
        return send_from_directory(app.config['UPLOAD_FOLDER'],
                                   filename=filename)


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
        if user['username'] == '' or user['password'] == '':
            return Response(status=403)

        possible_users = user.find_by_username(user['username'])
        # Check if a user already exists with this username
        if possible_users:
            return Response(status=403)

        user['token'] = str(hash(user['username'] + user['password']))
        user['contact_list'] = []
        user.save()

        return jsonify({'token': user['token']})


def parse_google_csv(fields, contacts):
    new_db_contacts = []
    for contact in contacts:
        new_db_contact = Contacts({"name": "",
                                   "emails": [],
                                   "phones": [],
                                   "labels": [],
                                   "image": {"type": "none", "url": ""}})
        for i, field in enumerate(fields):
            # Lol
            #if i == len(contact):
            #    break
            if field == "Name" and contact[i]:
                new_db_contact["name"] = contact[i]

            elif "E-mail" in field and "Type" in field and contact[i]:
                email_type = contact[i].strip("* ")
                data = contact[i + 1]

                # this code exists in case google ever makes there csv format consistent
                if " ::: " in data:
                    emails = data.split(" ::: ")
                    for email in emails:
                        new_db_contact["emails"].append({"address": email,
                                                         "type": email_type})
                else:
                    new_db_contact["emails"].append({"address": data,
                                                     "type": email_type})

            elif "Phone" in field and "Type" in field and contact[i]:
                phone_type = contact[i].strip("* ")
                data = contact[i + 1]
                if " ::: " in data:
                    numbers = data.split(" ::: ")
                    for number in numbers:
                        new_db_contact["phones"].append({"number": number,
                                                         "type": phone_type})

                else:
                    new_db_contact["phones"].append({"number": data,
                                                     "type": phone_type})

            elif "Group Membership" in field and contact[i]:
                new_db_contact["labels"] = contact[i].split(" ::: ")
                new_db_contact["labels"] = [label.strip("* ") for label in new_db_contact["labels"]]

            elif "Photo" in field and contact[i]:
                new_db_contact["image"] = {"type": "external", "url": contact[i]}

        new_db_contacts.append(new_db_contact)

    return new_db_contacts


def parse_outlook_csv(fields, contacts):
    new_db_contacts = []
    for contact in contacts:
        new_db_contact = Contacts({"name": "",

                                   "emails": [],
                                   "phones": [],
                                   "labels": [],
                                   "image": {"type": "none", "url": ""}})
        for i, field in enumerate(fields):
            #if i == len(contact):
            #    break
            if "Name" in field and contact[i]:
                new_db_contact["name"] += contact[i]

            elif "E-mail" in field and contact[i]:
                new_db_contact["emails"].append({"address": contact[i],
                                                 "type": str(len(new_db_contact["emails"]) + 1)})
            elif "Phone" in field and contact[i]:
                new_db_contact["phones"].append({"number": contact[i],
                                                 "type": field.replace(" Phone", "")})

            elif "Categories" in field and contact[i]:
                while i < len(contact) and contact[i]:
                    new_db_contact["labels"].append(contact[i])
                    i += 1

            # outlook csv's don't have any kind of photo field

        new_db_contacts.append(new_db_contact)

    return new_db_contacts


def parse_upload_csv(token, fields, contacts):
    user = User().find_by_token(token)
    if fields[0] == "Name":
        new_db_contacts = parse_google_csv(fields, contacts)
    elif fields[0] == "First Name":
        new_db_contacts = parse_outlook_csv(fields, contacts)
    else:
        return []

    for new_db_contact in new_db_contacts:
        new_db_contact.save()

        # add contact to user who is importing it
        user['contact_list'].append(new_db_contact['_id'])


    user.save()

    return new_db_contacts


@app.route('/csv', methods=['POST'])
def upload_csv():
    file = request.files['file']
    token = request.headers.get('token')
    stream = io.StringIO(file.stream.read().decode(), newline=None)
    csv = reader(stream)
    lines = []
    for row in csv:
        lines.append(row)

    fields = lines[0]
    contacts = parse_upload_csv(token, fields, lines[1:])

    if contacts == []:
        print('returning 422')
        return Response(status=422)


    return jsonify({'contacts': contacts}), 200

if __name__ == "__main__":
    app.run()
