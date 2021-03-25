
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from Dashboard2 import db
from datetime import datetime, date
import random
import string
from barcode import EAN13
import qrcode
import qrcode.image.svg

InventID = 0

# Define models
roles_users = db.Table(
    'roles_users',
    db.Column('user_id', db.Integer(), db.ForeignKey('user.id')),
    db.Column('role_id', db.Integer(), db.ForeignKey('role.id'))
)


class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer(), primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))

    def __str__(self):
        return self.name

users = db.Table('users',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('inventorization_id', db.Integer, db.ForeignKey('inventorization.id'), primary_key=True)
)
usersosft = db.Table('usersosft',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('soft_id', db.Integer, db.ForeignKey('soft.id'), primary_key=True)
)

organizations = db.Table('organizations',
    db.Column('organization_id', db.Integer, db.ForeignKey('organization.id'), primary_key=True),
    db.Column('inventorization_id', db.Integer, db.ForeignKey('inventorization.id'), primary_key=True)
)

categories = db.Table('categories',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('inventorization_id', db.Integer, db.ForeignKey('inventorization.id'), primary_key=True)
)

categoriesoft = db.Table('categoriesoft',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('soft_id', db.Integer, db.ForeignKey('soft.id'), primary_key=True)
)

class Category (db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    category_name = db.Column(db.String(255))


class Incentorystatus (db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True, autoincrement=True)
    status_name = db.Column(db.String(255));

    def __str__(self):
        return self.status_name

istat = db.Table('istat',
    db.Column('incentorystatus_id', db.Integer, db.ForeignKey('incentorystatus.id'), primary_key=True),
    db.Column('inventorizationt_id', db.Integer, db.ForeignKey('inventorization.id'), primary_key=True)
)



class Inventorization(db.Model):

    CURRENT_ID_VALUE = 100000000000

    def inventory_code_setter():
        Inventorization.CURRENT_ID_VALUE +=1
        return Inventorization.CURRENT_ID_VALUE

    def generate_barCode():
        my_code = EAN13(str(Inventorization.CURRENT_ID_VALUE))
        my_code.save("Dashboard2/static/barcodes/barcode"+str(Inventorization.CURRENT_ID_VALUE))
        return "/static/barcodes/barcode"+str(Inventorization.CURRENT_ID_VALUE)+".svg"

    def generate_qr_code():
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        factory = qrcode.image.svg.SvgImage
        qr.add_data(str(Inventorization.CURRENT_ID_VALUE))
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white", image_factory=factory)
        img.save("Dashboard2/static/qrcodes/qrcode"+str(Inventorization.CURRENT_ID_VALUE)+".svg")
        return "/static/qrcodes/qrcode"+str(Inventorization.CURRENT_ID_VALUE)+".svg"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))
    serialid = db.Column(db.String(255))
    model = db.Column(db.String(255))
    buydata = db.Column(db.Date, nullable=False, default=date.today)
    supplier = db.Column(db.String(255))
    purchace_cost = db.Column(db.String(255))
    warrranty = db.Column(db.Date, nullable=False, default=date.today)
    notes = db.Column(db.String(555))
    location = db.Column(db.String(255))
    image_source = db.Column(db.String(255))
    #image = db.Column(db.LargeBinary, nullable=False)
    inventory_code = db.Column(db.String(255), unique = True, default = inventory_code_setter)
    bar_code = db.Column(db.String(500), default = generate_barCode)
    qr_code = db.Column(db.String(500), default = generate_qr_code)
    status = db.relationship('Incentorystatus', secondary=istat, lazy='dynamic',
                            backref=db.backref('inventorization', lazy=True))
    company = db.relationship('Organization', secondary=organizations,
                            backref=db.backref('inventorization', lazy=True))
    category_id = db.relationship('Category', secondary=categories, lazy='dynamic',
                            backref=db.backref('inventorization', lazy=True))
    user_id = db.relationship('User', secondary=users, lazy='dynamic',
                            backref=db.backref('inventorization', lazy=True))
    def __str__(self):
        return self.name



class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255), nullable=False)
    last_name = db.Column(db.String(255))
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    active = db.Column(db.Boolean())
    confirmed_at = db.Column(db.DateTime())
    roles = db.relationship('Role', secondary=roles_users,
                            backref=db.backref('users', lazy='dynamic'))

    def __str__(self):
        return self.email


softinventory = db.Table('softinventory',
    db.Column('inventorization_id', db.Integer, db.ForeignKey('inventorization.id'), primary_key=True),
    db.Column('soft_id', db.Integer, db.ForeignKey('soft.id'), primary_key=True)
)

class Soft(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(255))
    lecense_key = db.Column(db.String(500))
    lecense_source = db.Column(db.String(255))
    buy_date = db.Column(db.String(255))
    end_date = db.Column(db.String(255))
    purchase_location = db.Column(db.String(255))
    prise = db.Column(db.String(255))
    notes = db.Column(db.String(1000))
    inventorization_id = db.relationship('Inventorization', secondary=softinventory, lazy='dynamic',
                            backref=db.backref('soft', lazy=True))
    category_id = db.relationship('Category', secondary=categoriesoft, lazy='dynamic',
                            backref=db.backref('soft', lazy=True))
    user_id = db.relationship('User', secondary=usersosft, lazy='dynamic',
                            backref=db.backref('soft', lazy=True))

    def __str__(self):
        return self.name

class Companylinks(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    web_adress = db.Column(db.String(255))
    service_link = db.Column(db.String(255))
    name = db.Column(db.String(255))
    type = db.Column(db.String(255))
    login = db.Column(db.String(255))
    password = db.Column(db.String(255))
    lecense_date = db.Column(db.String(500))
    licence_end_date = db.Column(db.String(500))
    cost = db.Column(db.String(500))
    notes = db.Column(db.String(1000))
    
    def __str__(self):
        return self.name
  
usermail = db.Table('usermail',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('mail_id', db.Integer, db.ForeignKey('maildata.id'), primary_key=True)
)

class Maildata(db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    domen_name = db.Column(db.String(255))
    service_name = db.Column(db.String(255))
    email = db.Column(db.String(255))
    password = db.Column(db.String(255))
    price = db.Column(db.String(255))
    date_activation = db.Column(db.String(255))
    date_end = db.Column(db.String(500))
    notes = db.Column(db.String(1000))
    user_id = db.relationship('User', secondary=usermail, lazy='dynamic',
                            backref=db.backref('mail', lazy=True))
    
    def __str__(self):
        return self.domen_name

userserver = db.Table('userserver',
    db.Column('user_id', db.Integer, db.ForeignKey('user.id'), primary_key=True),
    db.Column('server_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True)
)

categoryserver = db.Table('categoryserver',
    db.Column('category_id', db.Integer, db.ForeignKey('category.id'), primary_key=True),
    db.Column('servers_id', db.Integer, db.ForeignKey('servers.id'), primary_key=True)
)

class Servers (db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    soft_type = db.Column(db.String(255))
    login = db.Column(db.String(255))
    password = db.Column(db.String(255))
    ip_adress = db.Column(db.String(255))
    notes = db.Column(db.String(255))
    category_id = db.relationship('Category', secondary=categoryserver, lazy='dynamic',
                            backref=db.backref('server', lazy=True))
    user_id = db.relationship('User', secondary=userserver, lazy='dynamic',
                            backref=db.backref('server', lazy=True))
    
    def __str__(self):
        return self.soft_type

class Cameratype (db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    camera_type = db.relationship('Camera', backref='cameratype', lazy=True)


class Camera (db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    camera_type = db.Column(db.Integer, db.ForeignKey('cameratype.id'))
    model = db.Column(db.String(255))
    login = db.Column(db.String(255))
    password = db.Column(db.String(255))
    ip_adress = db.Column(db.String(255))
    notes = db.Column(db.String(1000))
    
    def __str__(self):
        return self



class Organization (db.Model):
    id = db.Column(db.Integer, unique=True, primary_key=True)
    name = db.Column(db.String(255))
    phone = db.Column(db.String(255))
    adress = db.Column(db.String(500))
    email = db.Column(db.String(255))
    link = db.Column(db.String(255))
    notes = db.Column(db.String(1000))
    
    def __str__(self):
        return self.name