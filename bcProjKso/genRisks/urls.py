from django.conf.urls import url

from . import views

from rest_framework_jwt.views import obtain_jwt_token, refresh_jwt_token, verify_jwt_token


# map views to urls

# our pattern to match is 
# \w: alphnumeric
# %: percent char
# _: underscore
#  : space
pat = '[\w%_ ]+'

urlpatterns = [
  # Authentication below

  # use the built in views of djangorestframework_jwt
  url(r'^auth/obtain_token/', obtain_jwt_token), # login
  url(r'^auth/refresh_token/', refresh_jwt_token),
  url(r'^auth/verify_token/', verify_jwt_token),

  # getters below
  
  # eg. /genRisks/
  url(r'^$', views.index.as_view(), name='index'),

  # eg. /genRisks/getNumUsers
  url(r'^getNumUsers/$', views.getNumUsers, name='getNumUsers'),

  # eg. /genRisks/isAdmin
  url(r'^isAdmin/$', views.isAdmin.as_view(), name='isAdmin'),
  
  # eg. /genRisks/getAllUserNames
  url(r'^getAllUserNames/$', views.getAllUserNames.as_view(), name='getAllUserNames'),
  
  # eg. /genRisks/Don%20Joe_55/getAllRisks
  url(r'^(?P<user_to_show>' + pat + ')/getAllRisks/$', 
    views.getAllRisks.as_view(), name='getAllRisks'),
 
   # eg. /genRisks/Don Joe/Current risk/getSingleRiskWithFields
  url(r'^(?P<user_to_show>' + pat + ')/(?P<risk_type>' + pat + ')/getSingleRiskWithFields/$', 
    views.getSingleRiskWithFields.as_view(), name='getSingleRiskWithFields'),
 
   # eg. /genRisks/Don%20Joe_55/getAllRisksWithFields
  url(r'^(?P<user_to_show>' + pat + ')/getAllRisksWithFields/$', 
    views.getAllRisksWithFields.as_view(), name='getAllRisksWithFields'), 

  # setters below
  
  # eg. /genRisks/createNewUser
  url(r'^createNewUser/$', views.createNewUser.as_view(), name='createNewUser'),

   # eg. /genRisks/delUser
  url(r'^delUser/$', views.delUser.as_view(), name='delUser'), 

  # eg. /genRisks/createRisk
  url(r'^createRisk/$', views.createRisk.as_view(), name='createRisk'),
                         
  # eg. /genRisks/Don Joe/risk name/delRisk
  url(r'^(?P<user_to_show>' + pat + ')/(?P<risk_type>' + pat + ')/delRisk/$', views.delRisk.as_view(), name='delRisk'),

  # eg. /genRisks/Don Joe/risk name/field type/field name/delField
  url(r'^(?P<user>' + pat + ')/(?P<risk>' + pat + ')/(?P<field_type>' + pat 
    + ')/(?P<field_name>' + pat + ')/delField/$', 
    views.delField.as_view(), name='delField'),

  # eg. /genRisks/saveField
  url(r'^saveField/$', views.saveField.as_view(), name='saveField')


]
