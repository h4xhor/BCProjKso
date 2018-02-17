from django.db import models

from datetime import date
import datetime

class CustomerName(models.Model):
  customer_name = models.CharField(max_length=200)
#   user_name = models.CharField(max_length=200)
#   password = models.CharField(max_length=200)

  def __str__(self):
    return self.customer_name
    
# Each GenericRisk (eg. Automobile)
#   Relates to a single CustomerName
#   Can have multiple fields:
#      TextField
class GenericRisk(models.Model):
  risk_type = models.CharField(max_length=200)

  customer_name = models.ForeignKey(CustomerName, on_delete=models.CASCADE)

  def __str__(self):
    return self.risk_type

# All text fields (eg. name, model, serial)
# Each TextField:
#   Relates to a single GenericRisk
class TextField(models.Model):
  field_name = models.CharField(max_length=200)
  field_val = models.CharField(max_length=200, default='')

  generic_risk = models.ForeignKey(GenericRisk, on_delete=models.CASCADE)

  def __str__(self):
    return self.field_name + ' = ' + self.field_val

# All number fields (eg. number of doors)
# Each NumberField:
#   Relates to a single GenericRisk
class NumberField(models.Model):
  field_name = models.CharField(max_length=200)
  field_val = models.IntegerField(default=0)

  generic_risk = models.ForeignKey(GenericRisk, on_delete=models.CASCADE)

  def __str__(self):
    return self.field_name + ' = ' + str(self.field_val)

# All currency fields (eg. number of doors)
# Each NumberField:
#   Relates to a single GenericRisk
class CurrencyField(models.Model):
  field_name = models.CharField(max_length=200)
  field_val = models.IntegerField(default=0)

  generic_risk = models.ForeignKey(GenericRisk, on_delete=models.CASCADE)

  def __str__(self):
    return self.field_name + ' = ' + str(self.field_val)

# All date fields (eg. year of manufacture)
# Each NumberField:
#   Relates to a single GenericRisk
class dateField(models.Model):
  field_name = models.CharField(max_length=200)

  # set default date of today
  field_val = models.DateField(default=date.today)
  
  generic_risk = models.ForeignKey(GenericRisk, on_delete=models.CASCADE)

  def __str__(self):
    return self.field_name + ' = ' + self.field_val.strftime("%Y/%m/%d")
          
