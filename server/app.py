#!/usr/bin/env python3

import os
from faker import Faker
from flask import Flask, request, jsonify, make_response
from flask_migrate import Migrate
from sqlalchemy.exc import IntegrityError
from models import db, Sweet, Vendor, VendorSweet

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.environ.get(
    "DB_URI", f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}")

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.json.compact = False

migrate = Migrate(app, db)

db.init_app(app)

@app.route('/')
def home():
    return '<h1>Code challenge</h1>'

@app.route('/vendors', methods=['GET'])
def get_vendors():
    vendors = Vendor.query.all()
    vendors_list = [{'id': v.id, 'name': v.name} for v in vendors]
    return jsonify(vendors_list)

@app.route('/vendors/<int:id>', methods=['GET'])
def get_vendor(id):
    vendor = Vendor.query.get(id)
    if vendor:
        return jsonify({
            'id': vendor.id,
            'name': vendor.name,
            'vendor_sweets': []  
        })
    else:
        return make_response(jsonify({'error': 'Vendor not found'}), 404)



@app.route('/sweets', methods=['GET'])
def get_sweets():
    sweets = Sweet.query.all()
    sweets_list = [{'id': s.id, 'name': s.name} for s in sweets]
    return jsonify(sweets_list)

@app.route('/sweets/<int:id>', methods=['GET'])
def get_sweet(id):
    sweet = Sweet.query.get(id)
    if sweet:
        return jsonify({'id': sweet.id, 'name': sweet.name})
    else:
        return make_response(jsonify({'error': 'Sweet not found'}), 404)

@app.route('/vendor_sweets', methods=['POST'])
def create_vendor_sweet():
    data = request.get_json()
    if not data or 'price' not in data or data['price'] < 0:
        return jsonify({'errors': ['validation errors']}), 400
    
    sweet_id = data.get('sweet_id')
    vendor_id = data.get('vendor_id')

    sweet = Sweet.query.get(sweet_id)
    vendor = Vendor.query.get(vendor_id)

    if not sweet:
        return jsonify({'errors': ['Sweet not found']}), 400
    
    if not vendor:
        return jsonify({'errors': ['Vendor not found']}), 400

    vendor_sweet = VendorSweet(price=data['price'], sweet=sweet, vendor=vendor)
    db.session.add(vendor_sweet)
    db.session.commit()

    return jsonify({
        'id': vendor_sweet.id,
        'price': vendor_sweet.price,
        'sweet': {
            'id': sweet.id,
            'name': sweet.name
        },
        'sweet_id': sweet.id,
        'vendor': {
            'id': vendor.id,
            'name': vendor.name
        },
        'vendor_id': vendor.id
    }), 201

@app.route('/vendor_sweets/<int:id>', methods=['DELETE'])
def delete_vendor_sweet(id):
    vendor_sweet = VendorSweet.query.get(id)
    if vendor_sweet:
        db.session.delete(vendor_sweet)
        db.session.commit()
        return '', 204
    else:
        return make_response(jsonify({'error': 'VendorSweet not found'}), 404)

if __name__ == '__main__':
    app.run(port=5555, debug=True)

