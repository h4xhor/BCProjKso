from django.contrib.auth.models import User

from django.shortcuts import render


from django.http import HttpResponse, JsonResponse

from django.contrib.auth import authenticate, login

from .models import Users, GenericRisk, TextField, NumberField, CurrencyField, dateField

# JWT
from rest_framework.views import APIView
from rest_framework_jwt.authentication import JSONWebTokenAuthentication, get_authorization_header
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from rest_framework_jwt.settings import api_settings
jwt_decode_handler = api_settings.JWT_DECODE_HANDLER
jwt_get_username_from_payload = api_settings.JWT_PAYLOAD_GET_USERNAME_HANDLER
jwt_get_user_id_from_paylaod = api_settings.JWT_PAYLOAD_GET_USER_ID_HANDLER
#from rest_framework_jwt.utils import jwt_decode_handler, jwt_get_username_from_payload

import json
from pprint import pprint

ERROR = 'ERROR'
OK = 'OK'

# Auth
USERNAME = 'username'
PASSWORD = 'password'

# fields
USER_NAME = "user_name"
NEW_PW = 'new_pw'
NEW_USER_IS_ADMIN = 'new_user_is_admin'

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

TRUE_STR = 'True'
FALSE_STR = 'False'

def isValidJson(json_str):
  try:
    json_object = json.loads(json_str)
  except ValueError:
    return False
  return True


"""
Test View 
* Requires JWT authentication.
* Only admin users (user.is_staff = true) are able to access this view.
"""
class index(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated, 
                        IsAdminUser,)
  
  def get(self, req):

    auth = get_authorization_header(req).split()
    jwt_value = auth[1]


    payload = jwt_decode_handler(jwt_value)
    username = jwt_get_username_from_payload(payload)
    user_id = jwt_get_user_id_from_paylaod(payload)
#    (user, token) = JSONWebTokenAuthentication().authenticate(request)
#    msg = 'user = ' + user + ', token = ' + token

#    auth = get_authorization_header(request).split()
#    token = auth[1]
#    token_text = token.decode('ascii')
    msg = 'username = ' + username + ', user_id = ' + str(user_id)
    print(msg)

#    msg = 'Yo ' + payload.get('username') + ', ' + payload.get('token')
    return Response({'msg': msg})

def isUserAdmin(uname):
  is_admin = False
  if User.objects.all().filter(username=uname).exists():
    user_obj = User.objects.get(username=uname)
    if user_obj.is_staff:
      is_admin = True 

  return is_admin

class isAdmin(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get(self, req):
    resp = FALSE_STR

    jwt_uname = getUnameFromJWT(req)

    if isUserAdmin(jwt_uname):
      resp = TRUE_STR

    msg = '"' + jwt_uname + '" is admin: ' + resp

    print(msg)
    return Response(resp)

# tests if a user "user" exists
def userExists(user):
  return Users.objects.all().filter(user_name=user).exists()

# tests if a risk type "risk" exists in user "user_obj"
def riskExists(user_obj, risk):
  return user_obj.genericrisk_set.filter(risk_type = risk).exists()

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

def createUserHelper(uname, new_pw, new_user_is_admin_text):

  resp = ""

  msg = 'user_name = ' + uname + ', new_pw = ' + new_pw + ', new_user_is_admin = '

  if TRUE_STR == new_user_is_admin_text:
    new_user_is_admin = True
    msg += 'True'
  else: # anything else assume false
    new_user_is_admin = False
    msg += 'False'

  print(msg)

  # check if user exists
  isExist = userExists(uname)
  
  if isExist:
    resp = ERROR + ": '" + uname + "' already exists. Nothing changed." 
  else:
    # add user to database

    # our model table genRisks_users
    user_obj = Users(user_name=uname)
    user_obj.save()

    # auth_user
    auth_user_obj = User.objects.create_user(uname, '', new_pw)
    auth_user_obj.is_staff = new_user_is_admin
    auth_user_obj.save()
    resp = 'Ok: "' + uname + '" created. Administrator = ' + new_user_is_admin_text

  return resp

def getNumUsers(req):
  if 'GET' == req.method:
    num_users = Users.objects.all().values('user_name').count()

    return HttpResponse(num_users)

# Creates a new user given their name.
# Returns failure / success message.
# Expects POST.
# Does not require authentication if there are 0 existing users.
class createNewUser(APIView):

  def post(self, req):

    print('req = %s' % req)
    # get keyable json object
    json_obj = getJsonObjFromPOST(req)

    uname = json_obj[USER_NAME]
    new_pw = json_obj[NEW_PW]
    new_user_is_admin_text = json_obj[NEW_USER_IS_ADMIN]

    num_users = Users.objects.all().values('user_name').count()
    if 0 == num_users:
      # allow non authenticated users to create and over ride to give
      # first user admin permissions
      new_user_is_admin_text = TRUE_STR

      resp = createUserHelper(uname, new_pw, new_user_is_admin_text)
      print(' creating first user for time, giving admin privileges.')
    else: # requires authentication
      try:
        jwt_uname = getUnameFromJWT(req)

        if isUserAdmin(jwt_uname):
          resp = createUserHelper(uname, new_pw, new_user_is_admin_text)

      except IndexError:
        resp = ERROR + ': not authenticated!' 

    print('\t' + resp)
    return Response(resp)

# Returns user_name, user_obj using USER_NAME in the given json_obj
# On return:
# if USER_NAME is not found user_name = ''
# if user_obj is not found user_obj = {}
def getUserObj(json_obj):
  user_name = ''
  user_obj = {}

  if USER_NAME in json_obj:
    user_name = json_obj[USER_NAME]

    isExist = userExists(user_name)

    if isExist:
      # get Users object with user_name 
      user_obj = Users.objects.get(user_name = user_name)

  return user_name, user_obj

# Deletes user given their name
# Admins can delete any user
class delUser(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def post(self, req):

    jwt_uname = getUnameFromJWT(req)

    resp = ''
    json_obj = getJsonObjFromPOST(req)

    # username to apply delete on
    user_name, user_obj = getUserObj(json_obj)

    if '' == user_name:
      resp = ERROR + ': No ' + USER_NAME + ' field found in ' + json_text

    # if the "user_to_show" requested matches the token's "jwt_uname"
    # or if the token's jwt_uname is an admin then allow
    elif ((jwt_uname == user_name) or
         isUserAdmin(jwt_uname)):

      if {} == user_obj:
        resp = ERROR + ': ' + user_name + '" does not exist. Nothing deleted.' 
      else:

        # delete user from genRisks_users
        user_obj.delete()

        # delete user from auth_user
        auth_user_obj = User.objects.get(username=user_name)
        auth_user_obj.delete()

        resp = OK + ': deleted ' + user_name + '.'

    else:
      resp = ERROR + ': "' + jwt_uname + '" has no permission to delete "' + user_name + '" account.'

    print('\t' + resp)
    return Response(resp)

# Returns existing user names on success.
# Error message on error.
# Return type is a JSON array as a string
#   eg. {["0": "Bob", "1": "Don Joe"]}
# On error
#  []
# Expects GET.
class getAllUserNames(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated, 
                        IsAdminUser,)

  def get(self, req):

    # response as a dictionary
    resp = {}

    queryset = Users.objects.all().values(USER_NAME)
    num = queryset.count()
    
    if 0 == num:
      resp = []
    else: 
      for i in range(num):
        print('%d %s' % (i, queryset[i][USER_NAME]))
        resp[i] = queryset[i][USER_NAME]

    print("resp = %s" % resp)
    return Response(resp)

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

# Returns risk_name, risk_obj using RISK_TYPE in the given json_obj
#'risk_type' On return:
# if RISK_TYPE is not found risk_name = ''
# if risk_obj is not found risk_obj = {}
def getRiskType(user_obj, json_obj):
  risk_name = ''
  risk_obj = {}

  if RISK_TYPE in json_obj:
    risk_name = json_obj[RISK_TYPE] 

    if riskExists(user_obj, risk_name):
      risk_obj = user_obj.genericrisk_set.get(risk_type = risk_name)

  return risk_name, risk_obj

# Expects JSON data to be of form
# { "user_name": "Joe Bloggs", 
#   "risk_type": "Automobiles", 
#   "fields": [{"name": "make", "type": "text", "val": "Toyota" }, 
#              {"name": "num_doors", "type": "number", "val": "5" }, 
#              {"name": "value", "type": "currency", "val": "20000"}, 
#              {"name": "year", "type": "date", "val": "2018-02-02" }, 
#              {"name": "amount_insured", "type": "Currency", "val": "20000"} 
#             ]
# }
class createRisk(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,) 

  def post(self, req):                                
    resp = ""

    jwt_uname = getUnameFromJWT(req)

    json_obj = getJsonObjFromPOST(req)
    json_text = json.dumps(json_obj)

    user_name, user_obj = getUserObj(json_obj)
    print('here jwt_uname = ' + jwt_uname + ', user_name = ' + user_name)

    if '' == user_name:
      resp = ERROR + ': No ' + USER_NAME + ' field found in ' + json_text

    # if the given username matches JWT's or if is admin JWT
    elif ((jwt_uname == user_name) or
        isUserAdmin(jwt_uname)):

      if {} == user_obj:
        resp = ERROR + ': ' + user_name + '" does not exist. Please create first.' 
      else:
        risk_name, risk_obj = getRiskType(user_obj, json_obj)

        if '' == risk_name:
          resp = ERROR + ': No ' + RISK_TYPE + ' field found in ' + json_text

        elif {} != risk_obj:
          resp = ERROR + ': "' + risk_name + '" already exists.'  

        elif FIELDS not in json_obj:
          resp = ERROR + 'No ' + FIELDS + ' field found in ' + json_text

        else:
          num = len(json_obj['fields'])

          if 0 == num:
            resp = ERROR + ': ' + FIELDS + ' array is empty in ' + json_text

          else:
            risk_obj = user_obj.genericrisk_set.create(risk_type = risk_name)
            
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

              resp = OK + ": Done created new risk " + risk_name + " with: " + json_text
    else:
      resp = ERROR + ': "' + jwt_uname + '" has no permission to create risks for "' + user_name + '" account.'

    print("  %s" % resp)
    return Response(resp)


# returns the user object user_obj if user user exists
# else the empty set {}
def getUserObjIfExists(req, user):
  user_obj = {}

  if 'GET' == req.method:
    isExist = userExists(user)
    if isExist:
      user_obj = Users.objects.get(user_name = user)

    else:
      print(ERROR + ': ' + user + ' does not exist. Please create first.' )

  else:
    print(ERROR + ': GET method required')

  return user_obj

# returns all risks given a 
# user object user_obj
# else the empty set {}
def getAllRiskObjIfExists(user_obj):
  risk_obj = {}

  if {} != user_obj:
    num = user_obj.genericrisk_set.all().values().count()

    if 0 == num:
      print(ERROR + ': No risks found for ' + user_obj.user_name)
    else:
      risk_obj = user_obj.genericrisk_set.all()

  return risk_obj

# returns the risk object risk_obj if exists given a 
# user object user_obj
# else the empty set {}
def getSingleRiskObjIfExists(user_obj, cur_risk):
  risk_obj = {}

  if {} != user_obj:
    exists = user_obj.genericrisk_set.filter(risk_type = cur_risk).exists()

    if exists:
      risk_obj = user_obj.genericrisk_set.get(risk_type = cur_risk)
    else:
      print(ERROR + ': No risks found for ' + user_obj.user_name)

  return risk_obj

# Get username from JWT
def getUnameFromJWT(req):
  auth = get_authorization_header(req).split()
  jwt_value = auth[1]

  payload = jwt_decode_handler(jwt_value)
  uname = jwt_get_username_from_payload(payload)

  return uname

# Returns existing risks for user cur_user on success.
# Return type is a JSON object
#   eg. {["0": "Automobiles", "1": "Property"]}
# On error
#  []
# Expects GET.
class getAllRisks(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,) 

  def get(self, req, user_to_show):

    jwt_uname = getUnameFromJWT(req)

    resp = {}

    # if the "user_to_show" requested matches the token's "jwt_uname"
    # or if the token's jwt_uname is an admin then allow
    if ((jwt_uname == user_to_show) or
         isUserAdmin(jwt_uname)):

      user_obj = getUserObjIfExists(req, user_to_show)
      risk_obj = getAllRiskObjIfExists(user_obj)

      if {} != risk_obj:
        r_val = risk_obj.values()
        num = r_val.count()

        for i in range(num):
          resp[i] = r_val[i]['risk_type']

      print("resp = %s" % resp)

    return Response(resp)

# Gets all risks for a single user
#
# eg. A user with 3 risks will have a return JSON string like this:
#
# { 'user_name': 'Joe',
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
class getAllRisksWithFields(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,)

  def get(self, req, user_to_show):

    json_obj = {}

    jwt_uname = getUnameFromJWT(req)

    if ((jwt_uname == user_to_show) or
         isUserAdmin(jwt_uname)):

      user_obj = getUserObjIfExists(req, user_to_show)

      # note risk_obj is an array
      risk_obj = getAllRiskObjIfExists(user_obj)

      json_obj[USER_NAME] = user_to_show
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
      return Response(json_obj)

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
class getSingleRiskWithFields(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated, )

  def get(self, req, user_to_show, risk_type):

    json_obj = {}

    jwt_uname = getUnameFromJWT(req)

    if ((jwt_uname == user_to_show) or
         isUserAdmin(jwt_uname)):

      user_obj = getUserObjIfExists(req, user_to_show)
      risk_obj = getSingleRiskObjIfExists(user_obj, risk_type)
        
      json_obj[USER_NAME] = user_to_show
      json_obj[RISK_TYPE] = risk_type

      if {} != risk_obj:
        getFieldsForSingleRisk(risk_obj, json_obj)

      print('json_obj = %s', json_obj)

    return Response(json_obj)

# deletes risk for user
class delRisk(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,) 

  def get(self, req, user_to_show, risk_type):
    resp = {}

    jwt_uname = getUnameFromJWT(req)

    if ((jwt_uname == user_to_show) or
         isUserAdmin(jwt_uname)):

      resp = OK

      user_obj = getUserObjIfExists(req, user_to_show)
      risk_obj = getSingleRiskObjIfExists(user_obj, risk_type)

      if {} == user_obj:
        resp = ERROR + ': ' + user_to_show + " doesn't exist"
      elif {} == risk_obj:
        resp = ERROR + ': ' + risk_type + " doesn't exist"
      else:
        print('delted risk ' + risk_type + ' for ' + user_to_show)
        risk_obj.delete()

    return Response(resp)

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

# deletes a field name "field" for a "risk" under a "user"
class delField(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated, )

  def get(self, req, user, risk, field_type, field_name):
  
    json_obj = {}

    jwt_uname = getUnameFromJWT(req)

    if ((jwt_uname == user) or
      isUserAdmin(jwt_uname)):

      user_obj = getUserObjIfExists(req, user)
      risk_obj = getSingleRiskObjIfExists(user_obj, risk)

      resp = ''
      if {} == user_obj:
        resp = ERROR + ': ' + user + " doesn't exist"
      elif {} == risk_obj:
        resp = ERROR + ': ' + risk + " doesn't exist"
      else:
        resp = delFieldForSingleRisk(risk_obj, field_type, field_name)

    print('  ' + resp)
    return Response(resp)

# If field exists, saves an exisiting field (due to modification of it's value)
# Else adds the new field in
class saveField(APIView):
  authentication_classes = (JSONWebTokenAuthentication,)
  permission_classes = (IsAuthenticated,) 

  def post(self, req):
    jwt_uname = getUnameFromJWT(req)

    resp = ''

    json_obj = getJsonObjFromPOST(req)
    json_text = json.dumps(json_obj)

    user_name, user_obj = getUserObj(json_obj)
    
    
    if '' == user_name:
      resp = ERROR + ': No ' + USER_NAME + ' field found in ' + json_text

    elif ((jwt_uname == user_name) or
         isUserAdmin(jwt_uname)):

      if {} == user_obj:
        resp = ERROR + ': ' + user_name + '" does not exist. Please create first.' 
      else:

        risk_name, risk_obj = getRiskType(user_obj, json_obj)

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

    else:
      resp = ERROR + ': "' + jwt_uname + '" has no permission to save fields for "' + user_name + '" account.'

    print("  %s" % resp)
    return Response(resp) 


