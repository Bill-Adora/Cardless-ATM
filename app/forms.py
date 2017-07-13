from wtforms import Form, BooleanField, StringField, PasswordField, validators, IntegerField

class LoginForm(Form):
    password = PasswordField('PIN Code', [validators.DataRequired(), validators.Length(min=6, max=6)])

class DepositForm(Form):
    depositAmount = IntegerField('Deposit', [validators.Required(),validators.NumberRange(min=100, max=20000)])

class WithdrawForm(Form):
    withdrawAmount = IntegerField('Withdraw', [validators.Required(),validators.NumberRange(min=100, max=20000)])

class TransferForm(Form):
    transferAmount = IntegerField('Amount', [validators.Required(),validators.NumberRange(min=100, max=20000)])
    accountNumber = IntegerField('Account Number', [validators.Required()])