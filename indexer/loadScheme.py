#!/usr/bin/env python
# encoding: utf-8

import os, sys, string, commands, fsconf

def loadScheme(schemefile):
  """Where 'schemefile' is a path to a .scheme file
     Returns a list of field names and key"""
  
  scheme = {}
  file = open(schemefile,'r')
  schemetext = file.read() + '\n'
  file.close()
  fieldMap = fieldNameMappings()
  for key,field in enumerate(schemetext.split(',')):
    if field in fieldMap:
      scheme[fieldMap[field]] = key
  print scheme
  return scheme    
  

def fieldNameMappings(): 
  """Returns a dictionary of field names mapped to varible names. The CVS
  files (and the access databases) are very badly inconsistant, in terms of
  field order, field names and field existance (some data isn't availible or
  given).
  
   This is partly the fault of the data given out, but mainly it's a problem
  in the access databases. This function attempts to:
  
   1) Guess what the field is. For example, we might have 'postcode',
  'post_code', 'code_postal', 'zip', 'zip_code' etc etc. The key of the
  dictionary is this value (so, the value in the cvs file, that varies). The
  value is the normalized name, so in the example above 'zipcode' is prefered,
  so fieldMapping['postcode'] = 'zipcode'
  
   2) Store the position in the field order. This comes in handy later when we
  need to figure out what field a particular one is, as there is no standard
  within the schemes.
  """

  fieldMapping = {}

  fieldMapping['amount'] = 'amount'
  fieldMapping['Amount'] = 'amount'  
  fieldMapping['payment_id'] = 'payment_id'
  fieldMapping['recipient_id'] = 'recipient_id'
  fieldMapping['id_recipient_1'] = 'recipient_id'
  fieldMapping['year'] = 'year'
  fieldMapping['Year'] = 'year'  
  fieldMapping['name'] = 'name'
  fieldMapping['geo1'] = 'geo1'
  fieldMapping['geo2'] = 'geo2'  
  fieldMapping['country'] = 'country'

  return fieldMapping

  
  
if __name__ == '__main__':
  print loadScheme('/Users/sym/Projects/farm-subsidy/data/scheme/estonia/payment/payment20070218.scheme')
  print loadScheme('/Users/sym/Projects/farm-subsidy/data/scheme/estonia/recipient/recipient20070218.scheme')  