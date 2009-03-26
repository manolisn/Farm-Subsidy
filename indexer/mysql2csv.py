#!/usr/bin/env python
# encoding: utf-8

import sys
sys.path.append('..')
import os
import commands
import re
import MySQLdb
import csv
import codecs

import fsconf


def mysql2csv():
  mysql_prefix = fsconf.mysql_prefix
  mysql_user = fsconf.mysql_user
  mysql_pass = fsconf.mysql_pass
  
  mysql_string = "mysql -u %s --password=%s " % (mysql_user,mysql_pass)
  databases = re.findall("((^|(?<=\n))%s[^\n]+)" % mysql_prefix,commands.getoutput("echo 'SHOW DATABASES' | %s" % (mysql_string)))
  
  for database in databases:
    database = database[0]
    mysql_string
    tables = commands.getoutput('echo "SHOW TABLES" | %s %s' % (mysql_string, database)).split("\n")
    for table in tables:
      
      if table[0:7] == 'payment':
        payment_table = table
      if table[0:9] == 'recipient':
        recipient_table = table

    if recipient_table and payment_table:
      print "working with %s" % database
      
      writer = csv.writer(codecs.open("%s/%s.csv" % (fsconf.csvdir, database),'w'))
      
      print "Opening Connection"
      
      connection = MySQLdb.connect (host = "localhost",
                                 user = mysql_user,
                                 passwd = mysql_pass,
                                 db = database)
        
      start = 0
      length = 1000                         
      db_end = 0
      while db_end is 0:
        c = connection.cursor()
            
        query = """

        SELECT *,
          (SELECT sum(%(payment)s.amount) 
           FROM %(payment)s, %(recipient)s 
           WHERE %(payment)s.recipient_id=%(recipient)s.recipient_id 
           AND R.recipient_id_x=recipient_id_x 
           GROUP BY recipient_id_x) AS total_amount 
        FROM %(recipient)s AS R, %(payment)s AS P
        WHERE R.recipient_id=P.recipient_id
        LIMIT %(start)s,%(length)s;
         
        """ % {'payment' : payment_table, 'recipient' : recipient_table, 'start' : start, 'length' : length}
          

        print "Execute Query %s to %s" % (start,start+length)

        c.execute(query)
            
        if start == 0:
          print "Load Scheme"
          scheme = []
          for f in c.description:
            scheme.append(f[0])
      
          file = csv.writer(codecs.open("%s/%s.scheme" % (fsconf.csvdir, database),'w'))
          file.writerow(scheme)
    
        print "Writing rows"
        row = c.fetchone()
        while row:
          writer.writerow(row)
          row = c.fetchone()
        
        c.scroll(0,mode='absolute')
        # print "rows:%s" % len(c.fetchall())
        if len(c.fetchall()) <= length-1:
          print "yes"
          db_end = 1
  
      
        start +=length  
        c.close()
      connection.close()
    
    

# def calcTotalAmount(name,ridx):
#   """docstring for calcTotalAmount"""
#   mysql_prefix = fsconf.mysql_prefix
#   mysql_user = fsconf.mysql_user
#   mysql_pass = fsconf.mysql_pass
# 
#   connection = MySQLdb.connect (host = "localhost",
#                              user = mysql_user,
#                              passwd = mysql_pass,
#                              db = name.split('.')[0])
# 
#   c = connection.cursor()
# 
#   query = """
#   SELECT SUM(p.amount) FROM recipient r LEFT JOIN payment p
#   ON r.recipient_id=p.recipient_id
#   WHERE r.recipient_id_x = %s
#   GROUP BY r.recipient_id_x
#   """ % ridx
#   c.execute(query)
# 
#   return c.fetchone()[0]
#   c.close()
# 
# 





if __name__ == '__main__':
  mysql2csv()







