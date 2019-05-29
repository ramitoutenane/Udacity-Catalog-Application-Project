from flask import Flask, render_template, request, flash
from flask import redirect, jsonify, url_for, make_response
from flask import session as login_session
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Category, Item, User
import httplib2
import requests
import json
import random
import string

app = Flask(__name__)

engine = create_engine('sqlite:///catalog.db')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()
categories = session.query(Category).all()

client_id = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']


@app.route('/')
@app.route('/catalog')
def showCatalog():
    session = DBSession()
    categories = session.query(Category).all()
    items = session.query(Item).order_by(desc(Item.id)).limit(9)
    if 'username' not in login_session:
        return render_template('public_catalog.html',
                               categories=categories, items=items)
    return render_template('catalog.html', categories=categories, items=items)


@app.route('/catalog/<int:category_id>')
def showItems(category_id):
    session = DBSession()
    caterory = session.query(Category).filter_by(id=category_id).one()
    items = session.query(Item).filter_by(category_id=category_id)
    return render_template('items.html', categories=categories,
                           items=items, category=caterory)


@app.route('/catalog/<int:category_id>/<int:item_id>')
def showDescription(category_id, item_id):
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).one()
    creator = getUserInfo(item.user_id)
    if 'username' not in login_session or\
            login_session['user_id'] != creator.id:
        return render_template('public_description.html', item=item)
    return render_template('description.html', item=item)


@app.route('/catalog/add', methods=['GET', 'POST'])
def addItem():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        session = DBSession()
        newItem = Item(name=request.form['title'],
                       description=request.form['description'],
                       category_id=request.form['category'],
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash("Item Added Successfully.")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('add.html', categories=categories)


@app.route('/catalog/<int:item_id>/edit', methods=['GET', 'POST'])
def editItem(item_id):
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('Only the creator of item can edit it');}" \
               "</script><body onload='myFunction()'>"
    if request.method == 'POST':
        item.name = request.form['title']
        item.description = request.form['description']
        item.category_id = request.form['category']
        session.add(item)
        session.commit()
        flash("Item Updated Successfully.")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('edit.html', categories=categories, item=item)


@app.route('/catalog/<int:item_id>/delete', methods=['GET', 'POST'])
def deleteItem(item_id):
    session = DBSession()
    item = session.query(Item).filter_by(id=item_id).one()
    if 'username' not in login_session:
        return redirect('/login')
    if item.user_id != login_session['user_id']:
        return "<script>function myFunction() " \
               "{alert('Only the creator of item can delete it');}" \
               "</script><body onload='myFunction()'>"
    if request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Item Removed Successfully.")
        return redirect(url_for('showCatalog'))
    else:
        return render_template('delete.html', item=item)


@app.route('/catalog/json')
def showCatalogJson():
    if 'username' not in login_session:
        return redirect('/login')
    session = DBSession()
    json = []
    for c in categories:
        items = session.query(Item).filter_by(category_id=c.id)
        json.append(c.serialize)
        json[len(json) - 1]['Item'] = [item.serialize for item in items]
    print json

    return jsonify(category=json)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    return render_template('login.html', client_id=client_id, STATE=state)


# Udacity Lesson : Creating Google Signin
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != client_id:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(
            json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['email'] = data['email']

    # see if user exists, if it doesn't make a new one
    user_id = getUserID(data["email"])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h3>Welcome, '
    output += login_session['username']
    output += '!</h3>'
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Only disconnect a connected user.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        del login_session['gplus_id']
        del login_session['access_token']
        del login_session['email']
        del login_session['user_id']
        del login_session['username']
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(
            json.dumps('Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


def createUser(login_session):
    session = DBSession()
    newUser = User(name=login_session['username'], email=login_session[
        'email'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


def getUserInfo(user_id):
    session = DBSession()
    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserID(email):
    session = DBSession()
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


if __name__ == '__main__':
    app.secret_key = 'secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=8000)
