from app import db
from hashlib import md5

class Customer(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    first_name = db.Column(db.String(20))
    last_name = db.Column(db.String(20))
    gender = db.Column(db.String(1))
    email = db.Column(db.String(30))
    phone_no = db.Column(db.String(10))

    accounts = db.relationship('Account', backref='customer', lazy='dynamic')

    def __init__(self, first_name, last_name, gender, email, phone_no):
        self.first_name = first_name
        self.last_name = last_name
        self.gender = gender
        self.email = email
        self.phone_no = phone_no
    
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return False

    def get_id(self):
        return str(self.id)
    
    def avatar(self, size):
        return 'http://www.gravatar.com/avatar/%s?d=mm&s=%d' % (md5(self.email.encode('utf-8')).hexdigest(), size)

    def __repr__(self):
        return '<Customer %r>' % self.first_name

class Account(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    balance = db.Column(db.Integer)
    customer_id = db.Column(db.Integer, db.ForeignKey('customer.id'))

    transactions = db.relationship("Transaction", backref='account', lazy='dynamic')

    def __init__(self, balance, customer_id):
        self.balance = balance
        self.customer_id = customer_id
        
    def __repr__(self):
        return '<Account %r>' % self.id

class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    amount = db.Column(db.Integer)
    transaction_time = db.Column(db.DateTime())
    account_id = db.Column(db.Integer, db.ForeignKey('account.id'))

    def __init__(self, amount, transaction_time, account_id):
        self.amount = amount
        self.transaction_time = transaction_time
        self.account_id = account_id

    def __repr__(self):
        return '<Transaction %r>' % self.id
