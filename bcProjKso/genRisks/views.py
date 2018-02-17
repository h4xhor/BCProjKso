from django.shortcuts import render

from django.http import HttpResponse, JsonResponse

from .models import CustomerName, GenericRisk, TextField, NumberField, CurrencyField, dateField

import json

ERROR = 'ERROR'
OK = 'OK'

# fields
CUSTOMER_NAME = "customer_name"
RISK_TYPE = "risk_type"
FIELDS = "fields"
NAME = 'name'
TYPE = 'type'
VAL = 'val'
ALL_RISKS = 'all_risks'

# field types
TEXT = 'text'
NUMBER = 'number'
CURRENCY = 'currency'
DATE = 'date'

def isValidJson(json_str):
  try:
    json_object = json.loads(json_str)
  except ValueError:
    return False
  return True

def index(req):
  return HttpResponse("Hello, world. You're at the genRisks index.")

# tests if a customer "cust" exists
def customerExists(cust):
  return CustomerName.objects.all().filter(customer_name=cust).exists()

# tests if a risk type "risk" exists in customer "cust_obj"
def riskExists(cust_obj, risk):
  return cust_obj.genericrisk_set.filter(risk_type = risk).exists()

# get JSON object from POST request
# returns {} on failure
def getJsonObjFromPOST(req):
  json_obj = {}

  if 'POST' == req.method:
    print("\tgot request.body = %s" % req.body)

    # convert binary string to normal string
    json_text = req.body.decode('ascii')

    if isValidJson(json_text): 

      # get keyable json object
      json_obj = json.loads(json_text)
    else:
      print(ERROR + ': malformed json string ' + json_text)
  else:
    print(ERROR + ': POST method required')

  return json_obj

# Use the Django built in API

# Creates a new customer given their name.
# Returns failure / success message.
# Expects POST.
def createNewCust(req):
  resp = ""

  print('req = %s' % req)
  # get keyable json object
  json_obj = getJsonObjFromPOST(req)

  cust_name = json_obj[CUSTOMER_NAME]

  # check if customer exists
  isExist = customerExists(cust_name)
  
  if isExist:
    resp = ERROR + ': "' + cust_name + '" already exists. Nothing changed.' 
  else:
    # add customer to database
    cust_obj = CustomerName(customer_name=cust_name)
    cust_obj.save()
    resp = 'Ok: ' + cust_name + '" created.'
  
  print('\t' + resp)
  return HttpResponse(resp)

# Deletes customer given their name
def delCust(req):
  resp = ''
  json_obj = getJsonObjFromPOST(req)

  cust_name, cust_obj = getCustObj(json_obj)

  if '' == cust_name:
    resp = ERROR + ': No ' + CUSTOMER_NAME + ' field found in ' + json_text

  elif {} == cust_obj:
    resp = ERROR + ': ' + cust_name + '" does not exist. Nothing deleted.' 

  else:
    # delete customer from database
    cust_obj.delete()
    resp = OK + ': deleted ' + cust_name + '.'

  print('\t' + resp)
  return HttpResponse(resp)

# Returns existing customer names on success.
# Error message on error.
# Return type is a JSON array as a string
#   eg. {["0": "Bob", "1": "Don Joe"]}
# On error
#  []
# Expects GET.
def getAllCustNames(req):
  # response as a dictionary
  resp = {}

  if 'GET' != req.method:
    print(ERROR + ': GET method required')
    return JsonResponse(resp, safe=False) 

  queryset = CustomerName.objects.all().values(CUSTOMER_NAME)
  num = queryset.count()
  
  if 0 == num:
    resp = []
  else: 
    for i in range(num):
      print('%d %s' % (i, queryset[i][CUSTOMER_NAME]))
      resp[i] = queryset[i][CUSTOMER_NAME]

  print("resp = %s" % resp)
  return JsonResponse(resp, safe=False)

# adds a text field for the risk_obj
def addTextField(risk_obj, name, val):
  print('  %s addTextField(): %s %s' % (risk_obj, name, val))
  risk_obj.textfield_set.create(field_name = name, 
    field_val = val)

# adds a number field for the risk_obj
def addNumberField(risk_obj, name, val):
  print('  %s addNumberField(): %s %s' % (risk_obj, name, val))
  risk_obj.numberfield_set.create(field_name = name, 
    field_val=val)

# adds a currency field for the risk_obj
def addCurrencyField(risk_obj, name, val):
  print('  %s addCurrencyField(): %s %s' % (risk_obj, name, val))
  risk_obj.currencyfield_set.create(field_name = name, 
    field_val=val)

# adds a date field for the risk_obj
def addDateField(risk_obj, name, val):
  print('  %s addDateField(): %s %s' % (risk_obj, name, val))
  risk_obj.datefield_set.create(field_name = name, 
    field_val=val)

# adds a field for the risk_obj given the field_type
def addField(risk_obj, name, field_type, val):

  if field_type == TEXT:
    addTextField(risk_obj, name, val)

  elif field_type == NUMBER:
    addNumberField(risk_obj, name, val)

  elif field_type == CURRENCY:
    addCurrencyField(risk_obj, name, val)

  elif field_type == DATE:
    addDateField(risk_obj, name, val)

# Returns cust_name, cust_obj using CUSTOMER_NAME in the given json_obj
# On return:
# if CUSTOMER_NAME is not found cust_name = ''
# if cust_obj is not found cust_obj = {}
def getCustObj(json_obj):
  cust_name = ''
  cust_obj = {}

  if CUSTOMER_NAME in json_obj:
    cust_name = json_obj[CUSTOMER_NAME]

    isExist = customerExists(cust_name)

    if isExist:
      # get CustomerName object with cust_name 
      cust_obj = CustomerName.objects.get(customer_name = cust_name)

  return cust_name, cust_obj

# Returns risk_name, risk_obj using RISK_TYPE in the given json_obj
#'risk_type' On return:
# if RISK_TYPE is not found risk_name = ''
# if risk_obj is not found risk_obj = {}
def getRiskType(cust_obj, json_obj):
  risk_name = ''
  risk_obj = {}

  if RISK_TYPE in json_obj:
    risk_name = json_obj[RISK_TYPE] 

    if riskExists(cust_obj, risk_name):
      risk_obj = cust_obj.genericrisk_set.get(risk_type = risk_name)

  return risk_name, risk_obj

# Expects JSON data to be of form
# { "customer_name": "Joe Bloggs", 
#   "risk_type": "Automobiles", 
#   "fields": [{"name": "make", "type": "text", "val": "Toyota" }, 
#              {"name": "num_doors", "type": "number", "val": "5" }, 
#              {"name": "value", "type": "currency", "val": "20000"}, 
#              {"name": "year", "type": "date", "val": "2018-02-02" }, 
#              {"name": "amount_insured", "type": "Currency", "val": "20000"} 
#             ]
# }
def createRisk(req):
  resp = ""

  json_obj = getJsonObjFromPOST(req)
  json_text = json.dumps(json_obj)

  cust_name, cust_obj = getCustObj(json_obj)
  
  if '' == cust_name:
    resp = ERROR + ': No ' + CUSTOMER_NAME + ' field found in ' + json_text

  elif {} == cust_obj:
    resp = ERROR + ': ' + cust_name + '" does not exist. Please create first.' 

  else:
    risk_name, risk_obj = getRiskType(cust_obj, json_obj)

    if '' == risk_name:
      resp = ERROR + ': No ' + RISK_TYPE + ' field found in ' + json_text

    elif {} != risk_obj:
      resp = ERROR + ': ' + risk_name + '" already exists.'  
    elif FIELDS not in json_obj:
      resp = ERROR + 'No ' + FIELDS + ' field found in ' + json_text

    else:
      num = len(json_obj['fields'])

      if 0 == num:
        resp = ERROR + ': ' + FIELDS + ' array is empty in ' + json_text

      else:
        risk_obj = cust_obj.genericrisk_set.create(risk_type = risk_name)
        
        # We know that risk_type and it's associated fields
        # does not exist yet in the database. So no need to check 
        # for further existing fields in database from here.
        print("  %d fields" % num)

        for i in range(num):
          print("%d. %s " % (i,json_obj[FIELDS][i]))
          
          name = json_obj[FIELDS][i][NAME]
          field_type = json_obj[FIELDS][i][TYPE]
          val = json_obj[FIELDS][i][VAL]

          print("%d %s %s %s" % (i, name, field_type, val))

          addField(risk_obj, name, field_type, val)

          resp = OK + "Done created new risk " + risk_name + " with: " + json_text

  print("  %s" % resp)
  return HttpResponse(resp)

# returns the customer object cust_obj if customer cust exists
# else the empty set {}
def getCustObjIfExists(req, cust):
  cust_obj = {}

  if 'GET' == req.method:
    isExist = customerExists(cust)
    if isExist:
      cust_obj = CustomerName.objects.get(customer_name = cust)

    else:
      print(ERROR + ': ' + cust + ' does not exist. Please create first.' )

  else:
    print(ERROR + ': GET method required')

  return cust_obj

# returns all risks given a 
# customer object cust_obj
# else the empty set {}
def getAllRiskObjIfExists(cust_obj):
  risk_obj = {}

  if {} != cust_obj:
    num = cust_obj.genericrisk_set.all().values().count()

    if 0 == num:
      print(ERROR + ': No risks found for ' + cust_obj.customer_name)
    else:
      risk_obj = cust_obj.genericrisk_set.all()

  return risk_obj

# returns the risk object risk_obj if exists given a 
# customer object cust_obj
# else the empty set {}
def getSingleRiskObjIfExists(cust_obj, cur_risk):
  risk_obj = {}

  if {} != cust_obj:
    exists = cust_obj.genericrisk_set.filter(risk_type = cur_risk).exists()

    if exists:
      risk_obj = cust_obj.genericrisk_set.get(risk_type = cur_risk)
    else:
      print(ERROR + ': No risks found for ' + cust_obj.customer_name)

  return risk_obj

# Returns existing risks for customer cur_cust on success.
# Return type is a JSON array as a string
#   eg. {["0": "Automobiles", "1": "Property"]}
# On error
#  []
# Expects GET.
def getAllRisks(req, cur_cust):
  resp = {}

  cust_obj = getCustObjIfExists(req, cur_cust)
  risk_obj = getAllRiskObjIfExists(cust_obj)

  if {} != risk_obj:
    r_val = risk_obj.values()
    num = r_val.count()

    for i in range(num):
      resp[i] = r_val[i]['risk_type']

  print("resp = %s" % resp)
  return JsonResponse(resp, safe=False)

# Gets all risks for a single customer
#
# eg. A customer with 3 risks will have a return JSON string like this:
#
# { 'customer_name': 'Joe',
#  'all_risks': 
#   [{"risk_type": "risk0", 
#   "fields": [{"name": "make0", "type": "text", "val": "Toyota0" }, 
#              {"name": "num_doors0", "type": "number", "val": "50" }]
#    },
#    {"risk_type": "risk1", 
#   "fields": [{"name": "make1", "type": "text", "val": "Toyota1" }, 
#              {"name": "num_doors1", "type": "number", "val": "50" }]
#    },
#    {"risk_type": "risk2", 
#   "fields": [{"name": "make2", "type": "text", "val": "Toyota2" }, 
#              {"name": "num_doors2", "type": "number", "val": "52" }]
#    }
#   ]
# }
#
# returns {} if there no risks exist in database
def getAllRisksWithFields(req, cur_cust):
  json_obj = {}

  cust_obj = getCustObjIfExists(req, cur_cust)

  # note risk_obj is an array
  risk_obj = getAllRiskObjIfExists(cust_obj)

  json_obj[CUSTOMER_NAME] = cur_cust
  json_obj[ALL_RISKS] = []

  if {} != risk_obj:
    risk_obj_val = risk_obj.values()
    num = risk_obj_val.count()

    for i in range(num):
      # get a single risk object from array risk_obj
      text_obj, num_obj, currency_obj, date_obj = getFieldsForRiskObj(risk_obj[i])

      # temporary fields object to store risks for single risk_obj[i]
      single_fields_obj = {}
      single_fields_obj[FIELDS] = []

      # get all the fields related to risk_obj[i]
      appendFieldsToJsonMultipleObj(text_obj, num_obj, 
        currency_obj, date_obj, single_fields_obj)

      # append it onto json_obj
      json_obj[ALL_RISKS].append(
        {RISK_TYPE: risk_obj_val[i][RISK_TYPE],
         FIELDS: single_fields_obj[FIELDS]})

  print("json_obj = %s" % json_obj)
  return JsonResponse(json_obj, safe=False)

# Given risk_obj returns it's related
# text_obj 
# num_obj
# currency_obj
# date_obj 
def getFieldsForRiskObj(risk_obj):
  text_obj = risk_obj.textfield_set.all()
  num_obj = risk_obj.numberfield_set.all()
  currency_obj = risk_obj.currencyfield_set.all()
  date_obj = risk_obj.datefield_set.all()

  return text_obj, num_obj, currency_obj, date_obj

# Returns true if field "in_field_name" of "field_type" exists 
# in "risk_obj" 
# Else returns false 
def fieldExists(risk_obj, field_type, in_field_name):

  exists = False
  if (TEXT == field_type):
    if risk_obj.textfield_set.filter(field_name = in_field_name).exists():
      exists = True

  elif (NUMBER == field_type):
    if risk_obj.numberfield_set.filter(field_name = in_field_name).exists():
      exists = True

  elif (CURRENCY == field_type):
     if risk_obj.currencyfield_set.filter(field_name = in_field_name).exists():
      exists = True

  elif (DATE == field_type):
     if risk_obj.datefield_set.filter(field_name = in_field_name).exists():
      exists = True

  return exists

# Given risk_obj and type returns it's related field object
# Returns {} if field does not exist
def getOneFieldObjForRiskObj(risk_obj, field_type, in_field_name):
  obj = {}
  if (TEXT == field_type):
    if risk_obj.textfield_set.filter(field_name = in_field_name).exists():
      obj = risk_obj.textfield_set.get(field_name = in_field_name)

  elif (NUMBER == field_type):
    if risk_obj.numberfield_set.filter(field_name = in_field_name).exists():
      obj = risk_obj.numberfield_set.get(field_name = in_field_name)

  elif (CURRENCY == field_type):
     if risk_obj.currencyfield_set.filter(field_name = in_field_name).exists():
      obj = risk_obj.currencyfield_set.get(field_name = in_field_name)

  elif (DATE == field_type):
     if risk_obj.datefield_set.filter(field_name = in_field_name).exists():
      obj = risk_obj.datefield_set.get(field_name = in_field_name)

  return obj

# Given a "field_obj" and it's type will append it's fields to the "json_obj"'s FIELD field
# field_obj is one of:
#   text_obj 
#   num_obj
#   currency_obj
#   date_obj 
#
# field_type is one of 
#   TEXT
#   NUMBER
#   currency
#   DATE
#
# modifies the json_obj
def appendFieldsToJson(field_obj, field_type, json_obj):
  num = field_obj.count()

  for i in range(num):

    json_obj[FIELDS].append({
      NAME: field_obj[i].field_name,
      TYPE: field_type,
      VAL: field_obj[i].field_val})
 
def appendFieldsToJsonMultipleObj(text_obj, num_obj, currency_obj,
  date_obj, json_obj):
  
  appendFieldsToJson(text_obj, TEXT, json_obj)
  appendFieldsToJson(num_obj, NUMBER, json_obj)
  appendFieldsToJson(currency_obj, CURRENCY, json_obj)
  appendFieldsToJson(date_obj, DATE, json_obj)

# gets the fields for a single risk object and
# given an existing json_obj appends this to it:
#   "fields": [{"name": "make", "type": "Text", "val": "Toyota" }, 
#              {"name": "num_doors", "type": "Number", "val": "5" }, 
#              {"name": "value", "type": "Currency", "val": "20000"}, 
#              {"name": "year", "type": "Date", "val": "2018-02-02" }, 
#              {"name": "amount_insured", "type": "Currency", "val": "20000"} 
#             ]
def getFieldsForSingleRisk(risk_obj, json_obj):

  text_obj, num_obj, currency_obj, date_obj = getFieldsForRiskObj(risk_obj)

  json_obj[FIELDS] = []

  appendFieldsToJsonMultipleObj(text_obj, num_obj, 
    currency_obj, date_obj, json_obj)

  return json_obj

# gets all the fields associated with a single risk
# returns a string version of a Json object json_obj
# 
# The Json object is something similar to the one shown in the
# comment for createRisk
def getSingleRiskWithFields(req, cur_cust, cur_risk):
  json_obj = {}

  cust_obj = getCustObjIfExists(req, cur_cust)
  risk_obj = getSingleRiskObjIfExists(cust_obj, cur_risk)
    
  json_obj[CUSTOMER_NAME] = cur_cust
  json_obj[RISK_TYPE] = cur_risk

  if {} != risk_obj:
    getFieldsForSingleRisk(risk_obj, json_obj)

  print('json_obj = %s', json_obj)
  return JsonResponse(json_obj, safe=False)

# deletes risk for customer
def delRisk(req, cur_cust, cur_risk):
  resp = OK

  cust_obj = getCustObjIfExists(req, cur_cust)
  risk_obj = getSingleRiskObjIfExists(cust_obj, cur_risk)

  if {} == cust_obj:
    resp = ERROR + ': ' + cur_cust + " doesn't exist"
  elif {} == risk_obj:
    resp = ERROR + ': ' + cur_risk + " doesn't exist"
  else:
    print('delted risk ' + cur_risk + ' for ' + cur_cust)
    risk_obj.delete()

  return HttpResponse(resp)

def delFieldForSingleRisk(risk_obj, field_type, field_name):
  resp = OK + ': deleted ' + field_name

  if {} != risk_obj:
    field_obj = getOneFieldObjForRiskObj(risk_obj, field_type, field_name)

    print('%s %s' % (risk_obj, field_obj))

    if {} == field_obj:
      resp = ERROR + ': ' + field_type + " doesn't exist"
    else:
      field_obj.delete()

  return resp

# deletes a field name "field" for a "risk" under a "customer"
def delField(req, cust, risk, field_type, field_name):
  json_obj = {}
      
  cust_obj = getCustObjIfExists(req, cust)
  risk_obj = getSingleRiskObjIfExists(cust_obj, risk)

  resp = ''
  if {} == cust_obj:
    resp = ERROR + ': ' + cust + " doesn't exist"
  elif {} == risk_obj:
    resp = ERROR + ': ' + risk + " doesn't exist"
  else:
    resp = delFieldForSingleRisk(risk_obj, field_type, field_name)

  print('  ' + resp)
  return HttpResponse(resp)

# If field exists, saves an exisiting field (due to modification of it's value)
# Else adds the new field in
def saveField(req):
  resp = ''

  json_obj = getJsonObjFromPOST(req)
  json_text = json.dumps(json_obj)

  cust_name, cust_obj = getCustObj(json_obj)

  if '' == cust_name:
    resp = ERROR + ': No ' + CUSTOMER_NAME + ' field found in ' + json_text

  elif {} == cust_obj:
    resp = ERROR + ': ' + cust_name + '" does not exist. Please create first.' 

  else:
    risk_name, risk_obj = getRiskType(cust_obj, json_obj)

    if '' == risk_name:
      resp = ERROR + ': No ' + RISK_TYPE + ' field found in ' + json_text

    elif {} == risk_obj:
      resp = ERROR + ': ' + risk_name + '" does not exist. Please create first.' 
    elif FIELDS not in json_obj:
      resp = ERROR + 'No ' + FIELDS + ' field found in ' + json_text
    else:
      num = len(json_obj['fields'])
      print("  %d fields" % num)

      if 0 == num:
        resp = ERROR + ': ' + FIELDS + ' array is empty in ' + json_text
      elif 1 == num:

        name = json_obj[FIELDS][0][NAME]
        field_type = json_obj[FIELDS][0][TYPE]
        val = json_obj[FIELDS][0][VAL]

        if ('' == name) or ('' == val):
          resp = ERROR + ": name or val can't be Empty"
        else:
          if fieldExists(risk_obj, field_type, name):
            # field exists, update it
            field_obj = getOneFieldObjForRiskObj(risk_obj, field_type, name)
            print(field_obj)
            field_obj.field_val = val

            field_obj.save();
            resp = OK + ': Saved risk = ' + risk_name + ', ' + name + ' = ' + val + ' (type = ' + field_type + ')'
          else:
            # field doesn't exist, add it in
            addField(risk_obj, name, field_type, val)
            resp = OK + ': Added ' + field_type + ' type ' + name + ' = ' + val
      else:
        resp = ERROR + ': JSON string has no "' + FIELDS + '" field.' 


  print("  %s" % resp)
  return HttpResponse(resp) 

