
from .views import * 

from django.test import TestCase
from django.urls import reverse

import json

# Create your tests here.
from .models import CustomerName, GenericRisk, TextField, NumberField, CurrencyField, dateField

class CustomerNameTests(TestCase):

  def create_new_customer(self):
    self.assertIs(customerExists("Bob"), False)

    resp = self.client.post('/genRisks/createNewCust/', 
      json.dumps({"customer_name":"Bob"}), 
      content_type='application/json')

    self.assertIs(customerExists("Bob"), True)
    self.assertIs(resp.status_code, 200)

  def create_risk(self):

    json_obj = {"customer_name": "Bob", "risk_type": "Property", "fields": [{"name": "Builder", "type": "text", "val": "Quality Homes"}, {"name": "Property Type", "type": "text", "val": "House"}, {"name": "Number of Rooms", "type": "number", "val": "3"}, {"name": "Number of Bathrooms", "type": "number", "val": "1"}, {"name": "Cost", "type": "currency", "val": "70000"}, {"name": "Insured", "type": "currency", "val": "70000"}, {"name": "Date Built", "type": "date", "val": "2016-06-02"}, {"name": "Date Owned", "type": "date", "val": "2017-03-23"}]} 

    resp = self.client.post('/genRisks/createRisk/', 
      json.dumps(json_obj), 
      content_type='application/json')

    self.assertIs(resp.status_code, 200)

    cust_name, cust_obj = getCustObj(json_obj)

    self.assertIs(riskExists(cust_obj, "Property"), True)

    risk_name, risk_obj = getRiskType(cust_obj, json_obj)

#    text_obj, num_obj, currency_obj, date_obj = getFieldsForRiskObj(risk_obj)

    self.assertIs(fieldExists(risk_obj, 'text', 'Builder'), True)
    self.assertIs(fieldExists(risk_obj, 'text', 'Property Type'), True)
    self.assertIs(fieldExists(risk_obj, 'number', 'Number of rooms'), True)
    self.assertIs(fieldExists(risk_obj, 'number', 'Number of Bathrooms'), True)
    self.assertIs(fieldExists(risk_obj, 'currency', 'Cost'), True)
    self.assertIs(fieldExists(risk_obj, 'currency', 'Insured'), True)
    self.assertIs(fieldExists(risk_obj, 'date', 'Date Built'), True)
    self.assertIs(fieldExists(risk_obj, 'date', 'Date Owned'), True)

  def save_fields(self):
    # text
    json_obj = {"customer_name":"Bob","risk_type":"Property","fields":[{"name":"Builder","type":"text","val":"5 Star Homes"}]}

    cust_name, cust_obj = getCustObj(json_obj)
    risk_name, risk_obj = getRiskType(cust_obj, json_obj)

    resp = self.client.post('/genRisks/saveField/', 
      json.dumps(json_obj), 
      content_type='application/json')

    self.assertIs(fieldExists(risk_obj, 'text', 'Builder'), True)

    field_obj = risk_obj.textfield_set.get(field_name = "Builder")
    self.assertIs(field_obj.field_val == "5 Star Homes", True)

    # number
    json_obj = {"customer_name":"Bob","risk_type":"Property","fields":[{"name":"Number of rooms","type":"number","val":"9"}]}

    resp = self.client.post('/genRisks/saveField/', 
      json.dumps(json_obj), 
      content_type='application/json')

    self.assertIs(fieldExists(risk_obj, 'number', 'Number of rooms'), True)

    field_obj = risk_obj.numberfield_set.get(field_name = "Number of rooms")
    self.assertIs(field_obj.field_val == 9, True)

    # currency
    json_obj = {"customer_name":"Bob","risk_type":"Property","fields":[{"name":"Cost","type":"currency","val":"90000"}]}

    resp = self.client.post('/genRisks/saveField/', 
      json.dumps(json_obj), 
      content_type='application/json')

    self.assertIs(fieldExists(risk_obj, 'currency', 'Cost'), True)

    field_obj = risk_obj.currencyfield_set.get(field_name = "Cost")
    self.assertIs(field_obj.field_val == 90000, True)

    # date 
    json_obj = {"customer_name":"Bob","risk_type":"Property","fields":[{"name":"Date Built","type":"date","val":"2016-07-03"}]}

    resp = self.client.post('/genRisks/saveField/', 
      json.dumps(json_obj), 
      content_type='application/json')

    self.assertEqual(fieldExists(risk_obj, 'date', 'Date Built'), True)

    field_obj = risk_obj.datefield_set.get(field_name = "Date Built")
    print("%s = %s" % (field_obj.field_val, '2016-07-03'))
    self.assertIs(field_obj.field_val == '2016-07-03', True)

  def del_fields(self):
    resp = self.client.get('/genRisks/Bob/Property/text/Property%20Type/delField/') 
    cust_obj = CustomerName.objects.get(customer_name = 'Bob')

    risk_obj = getSingleRiskObjIfExists(cust_obj, 'Property')

    self.assertIs(fieldExists(risk_obj, 'text', 'Property Type'), False)
    self.assertIs(resp.status_code, 200)

    resp = self.client.get('/genRisks/Bob/Property/number/Number%20of%20rooms/delField/') 
    self.assertIs(fieldExists(risk_obj, 'number', 'Number of rooms'), False)
    self.assertIs(resp.status_code, 200)

    resp = self.client.get('/genRisks/Bob/Property/currency/Cost/delField/') 
    self.assertIs(fieldExists(risk_obj, 'currency', 'Cost'), False)
    self.assertIs(resp.status_code, 200)

    resp = self.client.get('/genRisks/Bob/Property/date/Date%20Built/delField/') 
    self.assertIs(fieldExists(risk_obj, 'date', 'Date Built'), False)
    self.assertIs(resp.status_code, 200)

  def add_fields(self):
    json_obj = {"customer_name":"Bob","risk_type":"Property","fields":[{"name":"Number of Carparks","type":"number","val":"2"}]}

    resp = self.client.post('/genRisks/saveField/', 
      json.dumps(json_obj), 
      content_type='application/json')

    self.assertIs(fieldExists(risk_obj, 'number', 'Number of Carparks'), True)

    field_obj = risk_obj.numberfield_set.get(field_name = "Number of Carparks")
    self.assertIs(field_obj.field_val == 2, True)

  def del_customer(self):
    resp = self.client.post('/genRisks/delCust/', 
      json.dumps({"customer_name":"Bob"}), 
      content_type='application/json')

    self.assertIs(customerExists("Bob"), False)
    self.assertIs(resp.status_code, 200)

  def test_everything(self):
    self.create_new_customer()
    self.create_risk()
    self.save_fields()
    self.add_fields()
    self.del_fields()
    self.del_customer()

