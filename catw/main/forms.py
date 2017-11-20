from flask_wtf import FlaskForm as Form
from wtforms import StringField, SubmitField, PasswordField, BooleanField, RadioField, TextAreaField
from wtforms.fields.html5 import DateField
import wtforms.validators as wtv
from datetime import datetime


class Login(Form):
    username = StringField('Username', validators=[wtv.InputRequired(), wtv.Length(1, 16)])
    password = PasswordField('Password', validators=[wtv.InputRequired()])
    remember_me = BooleanField('Remember me')
    submit = SubmitField('OK')


class PwdUpdate(Form):
    current_pwd = PasswordField('Current Password', validators=[wtv.InputRequired()])
    new_pwd = PasswordField('New Password', validators=[wtv.InputRequired(),
                                                        wtv.EqualTo('confirm_pwd', message='Passwords must match'),
                                                        wtv.Length(min=10, message='Minimum length is %(min)d')])
    confirm_pwd = PasswordField('Re-Enter New Password')
    submit = SubmitField('Change')


class ProjectAdd(Form):
    name = StringField('Name', validators=[wtv.InputRequired(), wtv.Length(1, 256)])
    wbs = StringField('WBS', validators=[wtv.InputRequired(), wtv.Length(1, 256)])
    billable = RadioField('Billable',
                          choices=[('customer', 'Customer'), ('not', 'Not Billable')],
                          default='customer')
    status = RadioField('Status', choices=[('open', 'Open'), ('closed', 'Closed')],
                        default='open')
    information = TextAreaField('Information', validators=[wtv.Optional()])
    submit = SubmitField('OK')


class SelectDate(Form):
    date = DateField('Select Week', validators=[wtv.InputRequired()], default=datetime.today)
    submit = SubmitField('OK')
