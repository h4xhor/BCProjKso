from django.conf.urls import url

from . import views

# map views to urls

# our pattern to match is 
# \w: alphnumeric
# %: percent char
# _: underscore
#  : space
pat = '[\w%_ ]+'

urlpatterns = [
  # getters below
  
  # eg. /genRisks/
  url(r'^$', views.index, name='index'),
  
  # eg. /genRisks/getAllCustNames
  url(r'^getAllCustNames/$', views.getAllCustNames, name='getAllCustNames'),
  
  # eg. /genRisks/Don%20Joe_55/getAllRisks
  url(r'^(?P<cur_cust>' + pat + ')/getAllRisks/$', views.getAllRisks, 
    name='getAllRisks'),
 
   # eg. /genRisks/Don Joe/Current risk/getSingleRiskWithFields
  url(r'^(?P<cur_cust>' + pat + ')/(?P<cur_risk>' + pat + ')/getSingleRiskWithFields/$', 
    views.getSingleRiskWithFields, name='getSingleRiskWithFields'),
 
   # eg. /genRisks/Don%20Joe_55/getAllRisksWithFields
  url(r'^(?P<cur_cust>' + pat + ')/getAllRisksWithFields/$', 
    views.getAllRisksWithFields, name='getAllRisksWithFields'), 

  # setters below
  
  # eg. /genRisks/createNewCust
  url(r'^createNewCust/$', views.createNewCust, name='createNewCust'),

   # eg. /genRisks/delCust
  url(r'^delCust/$', views.delCust, name='delCust'), 

  # eg. /genRisks/createRisk
  url(r'^createRisk/$', views.createRisk, name='createRisk'),
  
  # eg. /genRisks/Don Joe/risk name/delRisk
  url(r'^(?P<cur_cust>' + pat + ')/(?P<cur_risk>' + pat + ')/delRisk/$', views.delRisk, name='delRisk'),

  # eg. /genRisks/Don Joe/risk name/field type/field name/delField
  url(r'^(?P<cust>' + pat + ')/(?P<risk>' + pat + ')/(?P<field_type>' + pat 
    + ')/(?P<field_name>' + pat + ')/delField/$', 
    views.delField, name='delField'),

  # eg. /genRisks/saveField
  url(r'^saveField/$', views.saveField, name='saveField')


]
