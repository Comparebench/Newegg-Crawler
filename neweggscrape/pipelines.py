# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import MySQLdb
import datetime
from scrapy.conf import settings
from scrapy.exceptions import DropItem


class AresPipeline(object):

    def __init__(self):
        self.conn = MySQLdb.connect(user=settings['MYSQL_USER'], passwd=settings['MYSQL_PASSWORD'],
                                    db=settings['MYSQL_DB'], host=settings['MYSQL_SERVER'],
                                    charset="utf8", use_unicode=True)
        self.cursor = self.conn.cursor()

    def process_item(self, item, spider):
        valid = True
        for data in item:
            if not data:
                valid = False
                raise DropItem("Missing {0}!".format(data))

        if valid and spider.name == 'neweggcpu':
            if item['images']:
                imageitem = item['images'][0]['path'].replace("full/", "")
            else:
                imageitem = None
            self.cursor.execute("""SELECT * FROM A_CPU WHERE model = %s""", [item['model']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                # if scraped model is the same as the db model, and price is different, update the row
                if checkmodel[2] == item['model'] and str(checkmodel[4]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_CPU SET price=%s, updated_ts=%s, image=%s WHERE cpuid=%s",
                                        ([str(item['price']).replace(",", ""), datetime.datetime.now(), imageitem, checkmodel[0]]))
                # otherwise, create new row
            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_CPU (make, model, price, neweggurl,
                                                              socket, frequency, threads, turbo,
                                                              l2, l3, die_size, lanes, newegg_sku, cores,
                                                              created_ts, image)
                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
                                             [(item['make'],
                                               item['model'],
                                               item['price'],
                                               item['url'],
                                               item['socket'],
                                               item['freq'],
                                               item['threads'],
                                               item['turbo'],
                                               item['l2'],
                                               item['l3'],
                                               item['die_size'],
                                               item['lanes'],
                                               item['newegg_sku'],
                                               item['cores'],
                                               datetime.datetime.now(),
                                               imageitem
                                                )])
            self.conn.commit()
        elif valid and spider.name == 'neweggintelboard':
            print "board"
            self.cursor.execute("SELECT * FROM A_Motherboard WHERE model = %s", [item['model']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                print checkmodel
                if checkmodel[2] == item['model'] and str(checkmodel[4]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_Motherboard SET price=%s, updated_ts=%s WHERE mid=%s",
                                        (str(item['price']).replace(",", ""), datetime.datetime.now(), checkmodel[0]))
            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_Motherboard (make, model, price, neweggurl, socket, ram_type, chipset, created_ts)
                                          VALUES (%s, %s, %s, %s, %s, %s,%s, %s)""", [(item['make'],
                                                                       item['model'],
                                                                       item['price'],
                                                                       item['url'],
                                                                       item['socket'],
                                                                       item['ram_type'],
                                                                       item['chipset'],
                                                                       datetime.datetime.now(),
                                                                       )])
            self.conn.commit()

        elif valid and spider.name == 'neweggram':
            print "ram"
            self.cursor.execute("SELECT * FROM A_Memory WHERE modelname = %s", [item['modelname']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                print checkmodel
                if checkmodel[7] == item['modelname'] and str(checkmodel[6]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_Memory SET price=%s, updated_ts=%s WHERE memid=%s",
                                        (str(item['price']).replace(",", ""), datetime.datetime.now(), checkmodel[0]))
            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_Memory (make, model, price, neweggurl, gigabytes, modules, type, modelname, created_ts)
                                          VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""", [(item['make'],
                                                                       item['model'],
                                                                       str(item['price']).replace(",", ""),
                                                                       item['url'],
                                                                       item['size'],
                                                                       item['modules'],
                                                                       item['type'],
                                                                       item['modelname'],
                                                                       datetime.datetime.now(),
                                                                       )])
            self.conn.commit()

        elif valid and spider.name == 'newegggpu':
            self.cursor.execute("SELECT * FROM A_GPU WHERE modelname = %s", [item['modelname']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                if checkmodel[10] == item['modelname'] and str(checkmodel[4]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_GPU SET price=%s, updated_ts=%s WHERE gid=%s",
                                        (str(item['price']).replace(",", ""), datetime.datetime.now(), checkmodel[0]))

            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_GPU (make, model, price, neweggurl, ram, bus_size, modelname, created_ts)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", [(item['make'],
                                                                                     item['model'],
                                                                                     str(item['price']).replace(",", ""),
                                                                                     item['url'],
                                                                                     item['ram'],
                                                                                     item['bus_size'],
                                                                                     item['modelname'],
                                                                                      datetime.datetime.now(),
                                                                                      )])
            self.conn.commit()
        elif valid and spider.name == 'neweggcase':
            self.cursor.execute("SELECT * FROM A_Case WHERE modelname = %s", [item['modelname']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                print checkmodel
                if checkmodel[7] == item['modelname'] and str(checkmodel[3]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_GPU SET price=%s, updated_ts=%s WHERE caseid=%s",
                                        (str(item['price']).replace(",", ""), datetime.datetime.now(), checkmodel[0]))

            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_Case (make, model, price, neweggurl, modelname, created_ts)
                                        VALUES (%s, %s, %s, %s, %s, %s)""", [(item['make'],
                                                                             item['model'],
                                                                             str(item['price']).replace(",", ""),
                                                                             item['url'],
                                                                             item['modelname'],
                                                                              datetime.datetime.now(),
                                                                              )])
            self.conn.commit()

        elif valid and spider.name == 'newegghdd':
            self.cursor.execute("SELECT * FROM A_Storage WHERE modelname = %s", [item['modelname']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                print checkmodel
                if checkmodel[9] == item['modelname'] and str(checkmodel[5]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_Storage SET price=%s, updated_ts=%s WHERE sid=%s",
                                        (str(item['price']).replace(",", ""), datetime.datetime.now(), checkmodel[0]))
            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_Storage (make, model, modelname, price, neweggurl, size, type, created_ts)
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""", [(item['make'],
                                                                                      item['model'],
                                                                                      item['modelname'],
                                                                                      item['price'],
                                                                                      item['url'],
                                                                                      item['size'],
                                                                                      'HDD',
                                                                                      datetime.datetime.now(),
                                                                                      )])
            self.conn.commit()

        elif valid and spider.name == 'neweggpsu':
            self.cursor.execute("SELECT * FROM A_PSU WHERE model = %s", [item['model']])
            checkmodel = self.cursor.fetchall()
            if len(checkmodel) > 0:
                checkmodel = checkmodel[0]
                print checkmodel
                if checkmodel[2] == item['model'] and str(checkmodel[4]) != str(item['price']).replace(",", ""):
                    self.cursor.execute("UPDATE A_PSU SET price=%s, updated_ts=%s WHERE psid=%s",
                                        (str(item['price']).replace(",", ""), datetime.datetime.now(), checkmodel[0]))
            elif len(checkmodel) == 0:
                self.cursor.executemany("""INSERT INTO A_PSU (make, model, price, watt, neweggurl, created_ts)
                                        VALUES (%s, %s, %s, %s, %s, %s)""", [(item['make'],
                                                                              item['model'],
                                                                              item['price'],
                                                                              item['watt'],
                                                                              item['url'],
                                                                              datetime.datetime.now(),
                                                                              )])
            self.conn.commit()

        return item
