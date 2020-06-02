# My Contacts App (Back End) [![Build Status](https://travis-ci.org/CSC-307-My-Contacts/my-contacts-backend.svg?branch=develop)](https://travis-ci.org/github/CSC-307-My-Contacts/my-contacts-backend)

### [Front End](https://github.com/CSC-307-My-Contacts/my-contacts-frontend/)

__CSC 307 Project:__ Alex, Bailey, Ryan, Yogi

This project uses [Travis CI](https://travis-ci.org/github/CSC-307-My-Contacts/my-contacts-backend) for continuous integration.

## Description
The My Contacts web application provides users with a secure and intuitive interface to manage their contacts. Users can create an account with a username and password and then login to safely view their contacts. Information such as a contact’s name, email addresses, phone numbers, and picture can be recorded for future use. In addition, users can search their contacts and organize them by groups. For compatibility with existing contact services My Contacts supports importing a contact CSV, which can be exported from Google Contacts or Outlook Contacts.


Note: At the start of this project, we were using one repo for the backend and frontend, because of this issues and documentation are kept in the frontend repo. Issues for the backend are available in the frontend repo.



## Testing
This project uses `pytest` for unit testing against the model and database.
```bash
pytest --cov-report term-missing --cov=backend
```
This will run the tests and display the test coverage.

## Dev Setup

### Install packages
```bash
pip3 install -r requirements.txt
```

### Start Backend
```python
python3 backend/contactsAPI.py
```

## Documentation
 - [UI Prototype](https://www.figma.com/file/gYEXAMvHRGv5uwydDPbMMg/Landing-Page-Contact-Details) (updated: 5/6/20)
 - [Class Diagram](https://github.com/CSC-307-My-Contacts/my-contacts-frontend/wiki/Class-Diagram) (updated: 5/13/20)
 - [Use Case Diagram](https://github.com/CSC-307-My-Contacts/my-contacts-frontend/wiki/Use-Case-Diagram) (updated: 5/21/20)
 - [API Specs](https://github.com/CSC-307-My-Contacts/my-contacts-frontend/blob/develop/docs/API-Specs.md) (updated: 6/1/20)

## Style Guide

* [pycodestyle 2.6.0](https://pypi.org/project/pycodestyle/)
* [autopep8](https://pypi.org/project/autopep8/)
