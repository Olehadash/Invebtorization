import os
from flask import Flask, url_for, redirect, render_template, request, abort
from flask_sqlalchemy import SQLAlchemy
from flask_security import Security, SQLAlchemyUserDatastore, \
    UserMixin, RoleMixin, login_required, current_user
from flask_security.utils import encrypt_password
import flask_admin
import imghdr
from flask_admin.contrib import sqla
from flask_admin.form.upload import FileUploadField
from flask_admin import helpers as admin_helpers
from flask_admin import BaseView, expose, Admin
from wtforms import PasswordField, ValidationError
from jinja2 import Markup


# Create customized model view class
class MyModelView(sqla.ModelView):

    def is_accessible(self):
        if not current_user.is_active or not current_user.is_authenticated:
            return False

        if current_user.has_role('superuser'):
            return True

        return False

    def _handle_view(self, name, **kwargs):
        """
        Override builtin _handle_view in order to redirect users when a view is not accessible.
        """
        if not self.is_accessible():
            if current_user.is_authenticated:
                # permission denied
                abort(403)
            else:
                # login
                return redirect(url_for('security.login', next=request.url))


    can_edit = True
    edit_modal = True
    create_modal = True    
    can_export = True
    can_view_details = True
    details_modal = True

class UserView(MyModelView):
    column_editable_list = ['email', 'first_name', 'last_name']
    column_searchable_list = column_editable_list
    column_exclude_list = ['password']
    #form_excluded_columns = column_exclude_list
    column_details_exclude_list = column_exclude_list
    column_filters = column_editable_list
    form_overrides = {
        'password': PasswordField
    }

class InventoryzationView(MyModelView):

    def picture_validation(form, field):
      if field.data:
         filename = field.data.filename
         if filename[-4:] != '.jpg': 
            raise ValidationError('file must be .jpg')
         if imghdr.what(field.data) != 'jpeg':
            raise ValidationError('file must be a valid jpeg image.')
      field.data = field.data.stream.read()
      return True

    form_columns = ['name','image_source','serialid', 'model', 'buydata', 'supplier','purchace_cost', 'warrranty', 'location','status', 'company','category_id', 'user_id']
    column_labels = dict(name='Name', image_source="Picture's URL", serialid='Serial Number', model = 'Model', buydata = 'Date of Buying', supplier = 'Supplier', purchace_cost = 'Purchace Cost', warrranty = 'Warranty', location = 'Location', status = 'Status', company = 'Company', category_id = 'Category', user_id = 'User')

    def pic_formatter(view, context, model, name):
       return 'NULL' if len(getattr(model, name)) == 0 else 'a picture'

    def barcode_formatter(view, context, model, name):
        return Markup('<img src="%s">' % model.bar_code)
    def qrcode_formatter(view, context, model, name):
        return Markup('<img src="%s">' % model.qr_code)

    #column_formatters =  dict(image=pic_formatter)
    #form_overrides = dict(image= FileUploadField)
    #form_args = dict(image=dict(validators=[picture_validation]))

    column_formatters = dict(bar_code = barcode_formatter, qr_code = qrcode_formatter)

    column_editable_list = ['name',  'serialid']
    column_searchable_list = column_editable_list
    

class SoftView(MyModelView):
    form_columns = ['name','lecense_key', 'lecense_source', 'buy_date','end_date', 'purchase_location', 'prise','notes', 'inventorization_id','category_id', 'user_id']
    column_labels = dict(name='Name', lecense_key="Lecense key", lecense_source='Lecense Source', buy_date='Date of Buying', end_date = 'Over License Date', purchase_location = 'Purchase Location', prise = 'Purchace Cost', notes = 'Notes', inventorization_id = 'Inventory', category_id = 'Category', user_id = 'User')
    column_editable_list = ['name',  'lecense_key']
    column_searchable_list = column_editable_list

class CompanylinksView(MyModelView):
    form_columns = ['web_adress','service_link', 'name', 'type','login', 'password', 'lecense_date','licence_end_date', 'cost','notes']
    column_labels = dict(web_adress="Web adress", service_link='Service Link', name='Name', type='Type', login = 'Login', password = 'Password', lecense_date = 'Date of Buying', licence_end_date = 'Over License Date', cost = 'Purchace Cost', notes = 'Notes')
    column_editable_list = ['name',  'web_adress']
    column_searchable_list = column_editable_list

class MaildataView(MyModelView):
    form_columns = ['domen_name','service_name', 'email', 'password','price', 'date_activation', 'date_end','notes', 'user_id']
    column_labels = dict(domen_name="Domen Name", service_name='Service Name', email='Email', password='Password', date_activation = 'Date of Buying', date_end = 'Over License Date', price = 'Purchace Cost', notes = 'Notes', user_id = 'User')
    column_editable_list = ['domen_name',  'email']
    column_searchable_list = column_editable_list

class ServersView(MyModelView):
    form_columns = ['soft_type','login', 'password', 'ip_adress','notes', 'category_id', 'user_id']
    column_labels = dict(soft_type="Soft Type", login ='Login', password='Password', ip_adress = 'IP adress', notes = 'Notes', category_id = 'Category', user_id = 'User')
    column_editable_list = ['soft_type']
    column_searchable_list = column_editable_list

class ServersView(MyModelView):
    form_columns = ['soft_type','login', 'password', 'ip_adress','notes', 'category_id', 'user_id']
    column_labels = dict(soft_type="Soft Type", login ='Login', password='Password', ip_adress = 'IP adress', notes = 'Notes', category_id = 'Category', user_id = 'User')
    column_editable_list = ['soft_type']
    column_searchable_list = column_editable_list

class CameraView(MyModelView):
    form_columns = ['camera_type','model', 'login', 'password', 'ip_adress','notes']
    column_labels = dict(camera_type="Camera Type", model = 'Model', login ='Login', password='Password', ip_adress = 'IP adress', notes = 'Notes')
    column_editable_list = ['model']
    column_searchable_list = column_editable_list


class OrganizationView(MyModelView):
    form_columns = ['name','phone', 'adress', 'email','link', 'notes']
    column_labels = dict(name="NAME", phone='PHONE', adress='ADDRES', email='E-MAIL', link = 'WEB SITE', notes = 'NOTES')
    column_editable_list = ['name']
    column_searchable_list = column_editable_list

class CustomView(BaseView):
    @expose('/')
    def index(self):
        return self.render('admin/custom_index.html')


