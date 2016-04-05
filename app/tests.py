from django.test import TestCase

import unirest
import json

base = 'http://127.0.0.1:8000/'
restaurant_id = ''

def clear():
    endpoint = base + 'auth/clear/'
    response = unirest.post(endpoint)
    if response.code == 200:
        print 'Cleared database'

def register_restaurant():
    endpoint = base + 'restaurant/register'
    response = unirest.post(endpoint, params={
        'name': 'Awesome Restaurant', 
        'address': '12345 Restaurant St.'})
    if response.code == 201:
        restaurant_json = json.loads(response.raw_body)
        global restaurant_id
        restaurant_id = restaurant_json.get('restaurant_id')
        print 'REGISTER RESTAURANT working'
    else:
        return

def get_restaurant():
    endpoint = base + 'restaurant/' + restaurant_id + '/'
    response = unirest.get(endpoint)
    if response.code == 200:
        print 'GET RESTAURANT BY ID working'

def create_menu_category():
    endpoint = base + 'restaurant/' + restaurant_id + '/create_menu_category/'
    response = unirest.post(endpoint, params={'name': 'Rolls'})
    if response.code == 201:
        print 'CREATE MENU CATEGORY working'

def create_menu_items():
    endpoint = base + 'restaurant/' + restaurant_id + '/create_menu_item/'
    with open('fake_menu.txt', 'r') as f:
        items = json.loads(f.read())
        for item in items:
            response = unirest.post(endpoint, params=item)
            if response.code != 201:
                print 'CREATE MENU ITEM broken'
                return
        print 'CREATE MENU ITEM working'

def register_user():
    endpoint = base + 'auth/register/'
    response = unirest.post(endpoint, params={
        'first_name': 'Bruce',
        'last_name': 'Wayne',
        'email': 'testcustomer@gmail.com',
        'password': '12345'})
    if response.code == 201:
        print 'REGISTER USER working'

def register_server_user():
    endpoint = base + 'auth/register/'
    response = unirest.post(endpoint, params={
        'first_name': 'Alfred',
        'last_name': 'Pennyworth',
        'email': 'testserver@gmail.com',
        'password': '12345'})
    if response.code == 201:
        print 'REGISTER SERVER USER working'

def register_server():
    endpoint = base + 'restaurant/' + restaurant_id + '/register_server/'
    response = unirest.post(endpoint, params={'email': 'testserver@gmail.com'})
    if response.code == 201:
        print 'REGISTER SERVER working'

if __name__=='__main__':
    clear()
    register_restaurant()
    get_restaurant()
    create_menu_category()
    create_menu_items()
    register_user()
    register_server_user()
    register_server()

