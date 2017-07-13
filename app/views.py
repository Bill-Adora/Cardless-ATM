from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
import sys
sys.path.insert(0, '/home/bill/Flask-ATM/app/Face_Recognizer')

from sendsms import generatePass
from classify import infer
from app import app, login_manager, db
from .models import Customer, Account
from .forms import LoginForm, DepositForm, WithdrawForm, TransferForm

otpPassword = None
customer = None

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/identify')
def identify():
    return render_template('identify.html')

@app.route('/upload', methods=['POST'])
def upload():
    global otpPassword
    global customer
    global acc_id
    if request.method == 'POST':
        rawImage = request.data
        #returns the customer's id
        cust_id = infer(rawImage)
        customer = Customer.query.filter_by(id = cust_id).first()
        account_holder = customer.accounts.all()
        for ac in account_holder:
            acc_id = ac.id
        #generates a random password and sends it to the user
        otpPassword = generatePass(customer.phone_no)
        print("Your password is {}".format(otpPassword))
        print("Your phone number is {}".format(customer.phone_no))
        print(type(customer.phone_no))
        return customer.first_name + ' ' + customer.last_name
    return redirect(url_for('identify'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm(request.form)
    if request.method == 'POST' and form.validate():
        if otpPassword == int(form.password.data):
            print("otpPassword is {}".format(otpPassword))
            print(customer)
            login_user(customer)
            flash('Logged in successfully.')
            return redirect(url_for('transactions'))
    return render_template('/login.html', form=form)

@login_manager.user_loader
def load_user(id):
    return Customer.query.get(int(id))

@app.route("/logout")
@login_required
def logout():
    logout_user()
    return render_template('index.html')

@app.route('/transactions', methods=['GET', 'POST'])
@login_required
def transactions():
    if request.method == 'POST':
        if request.form['submit'] == 'Deposit':
            return redirect(url_for('deposit'))
        elif request.form['submit'] == 'Withdraw':
            return redirect(url_for('withdraw'))
        elif request.form['submit'] == 'Check Balance':
            return redirect(url_for('balance'))
        elif request.form['submit'] == 'Transfer':
            return redirect(url_for('transfer'))
        else:
            return redirect(url_for('transactions'))
    return render_template('transactions.html', customer = customer)

@app.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    form = DepositForm(request.form)
    if request.method == 'POST' and form.validate():
        deposit_amount = form.depositAmount.data
        account = Account.query.filter_by(id = acc_id).first()
        account.balance = account.balance + deposit_amount
        db.session.commit()
        print(account.balance)
        flash('Your account has been credited')
        return redirect(url_for('transactions'))
    return render_template('deposit.html', customer = customer, form=form)

@app.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    form = WithdrawForm(request.form)
    if request.method == 'POST' and form.validate():
        withdraw_amount = form.withdrawAmount.data
        account = Account.query.filter_by(id = acc_id).first()
        if withdraw_amount <= account.balance:
            account.balance = account.balance - withdraw_amount
            flash('Success, collect cash from tray')
            db.session.commit()
        else:
            flash('The withdraw amount is more than your balance')
            return redirect(url_for('withdraw'))
        return redirect(url_for('transactions'))
    return render_template('withdraw.html', customer = customer, form=form)

@app.route('/balance', methods=['GET', 'POST'])
@login_required
def balance():
    account = Account.query.filter_by(id = acc_id).first()
    return render_template('check_balance.html', customer = customer, balance=account.balance)

@app.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer():
    form = TransferForm(request.form)
    if request.method == 'POST' and form.validate():
        account = Account.query.filter_by(id = acc_id).first()
        transfer_amount = form.transferAmount.data
        transfer_id = form.accountNumber.data
        transfer_account = Account.query.filter_by(id = transfer_id).first()
        if transfer_amount > 0 and transfer_amount <= account.balance:
            account.balance = account.balance - transfer_amount
            transfer_account.balance = transfer_account.balance + transfer_amount
            db.session.commit()
            flash('You have transferred cash')
        else:
            flash('The amount you want to transfer is more than your balance')
            return redirect(url_for('transfer'))
        return redirect(url_for('transactions'))
    return render_template('transfer.html', customer = customer, form=form)