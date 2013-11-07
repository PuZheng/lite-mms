# -*- coding: UTF-8 -*-
"""
@author: Yangminghua
@version: $
"""
import ConfigParser
import json
import os
import sys
from pyodbc import DatabaseError
import types
import datetime
import tornado.ioloop
import tornado.web
import win32serviceutil
import win32service
import win32event

cursor = None


def get_config():
    cf = ConfigParser.ConfigParser()
    cf.readfp(open(os.path.join(sys.prefix, "config.ini")))
    return cf


def init_db():
    import pyodbc

    args = get_config()

    server = args.get("SQLServer", "SQLServerHost")

    db = args.get("SQLServer", "DatabaseName")

    user = args.get("SQLServer", "User")

    password = args.get("SQLServer", "Password")

    cnxn = pyodbc.connect(
        r'DRIVER={SQL SERVER};SERVER=%s;DATABASE=%s;CHARSET=UTF8;UID=%s;PWD'
        r'=%s' % (
            server, db, user, password))
    global cursor
    cursor = cnxn.cursor()


def main(host, port):
    init_db()
    handlers = [
        (r"/", IndexRequestHandler),
        (r"/products", ProductRequestHandler),
        (r"/customers", CustomerRequestHandler),
        (r"/consignments", ConsignmentRequestHandler),
        (r"/product-types", ProductTypeRequestHandler)
    ]
    application = tornado.web.Application(handlers)
    print "Running on http://%(host)s:%(port)s/" % {"host": host, "port": port}
    application.listen(port, address=host)
    tornado.ioloop.IOLoop.instance().start()


class BaseRequestHandler(tornado.web.RequestHandler):
    @tornado.web.asynchronous
    def get(self, *args, **kwargs):
        self._write(self._get, *args, **kwargs)

    @tornado.web.asynchronous
    def post(self, *args, **kwargs):
        self._write(self._post, *args, **kwargs)

    def _get(self, *args, **kwargs):
        pass

    def _post(self, *args, **kwargs):
        pass

    def _write(self, f, *args, **kwargs):
        try:
            result = f(*args, **kwargs)
            if isinstance(result, types.DictType) or \
                    isinstance(result, types.ListType):
                self.write(json.dumps(result))
                self.set_header("Content-Type",
                                "application/json; charset=UTF-8")
            else:
                self.write(result)
            self.finish()
        except Exception, e:
            self.send_error(403, exception=e)


class ProductRequestHandler(BaseRequestHandler):
    def _get(self, *args, **kwargs):
        ret = {}
        cursor.execute(
            "select ProductId,ProductName,MateriaID from TotalProduct")
        rows = cursor.fetchall()
        for row in rows:
            ret.setdefault(row.MateriaID, []).append(
                dict(id=row.ProductId,
                     name=row.ProductName.strip().decode("GBK")))
        return ret


class ProductTypeRequestHandler(BaseRequestHandler):
    def _get(self, *args, **kwargs):
        types = []
        cursor.execute(
            "select MateriaID,MateriaName from TotalMateria where "
            "MateriaID in (select DISTINCT(MateriaID) from TotalProduct)"
        )
        rows = cursor.fetchall()
        for row in rows:
            types.append(dict(id=row.MateriaID,
                              name=row.MateriaName.strip().decode("GBK")))
        return types


class CustomerRequestHandler(BaseRequestHandler):
    def _get(self, *args, **kwargs):
        customers = []
        cursor.execute(
            "select companyid,companyname,pinyin from TotalClient where "
            "clienttype=2 and ifactive=0")
        rows = cursor.fetchall()
        for row in rows:
            customers.append(
                dict(id=row.companyid,
                     name=row.companyname.strip().decode("GBK"),
                     short=row.pinyin.strip().decode("GBK")))
        return customers


class ConsignmentRequestHandler(BaseRequestHandler):
    def _post(self, *args, **kwargs):
        d = json.loads(self.request.body) if self.request.body else None
        if not d:
            self.send_error(status_code=403)
        consignment_id = d["consignment_id"]
        customer_id = d["customer_id"]
        plate = d["plate"]
        weight = d["weight"]
        quantity = d.get("quantity", 0)
        product_list = d["product_list"]

        cursor.execute(
            "insert into OutDepotNew(PaperID,ClientID,AutoName,OutDate,"
            "AllWeight,PackNo,PiWeight,DeduceWeight,IfActive) values(?,"
            "?,?,?,?,?,?,?,?)",
            (consignment_id, customer_id, plate, datetime.datetime.today(),
             weight, quantity, 0, 0, 1))
        row = cursor.execute("SELECT @@IDENTITY").fetchone()
        id = int(row[0])

        for product in product_list:
            cursor.execute(
                "insert into OutDepotDetail(OutPaperID,ProductID,Amount,"
                "Weight,IfRedo) values(?,?,?,?,?)",
                (id, product["id"], product.get("quantity", 0),
                 product["weight"], product.get("isReturned", 0)))
        try:
            cursor.commit()
        except DatabaseError, e:
            cursor.rollback()
            raise e
        return dict(id=id)

    def _get(self, *args, **kwargs):
        acceptances = []
        sql = "select num, PaperID, ClientID from OutDepotNew"
        PaperID = self.get_argument("PaperID", "")
        if PaperID:
            sql += " where PaperId = '%s'" % PaperID
        cursor.execute(sql)
        rows = cursor.fetchall()
        for row in rows:
            acceptances.append(dict(id=row.PaperID.strip().decode("GBK"),
                                    MSSQL_ID=row.num,
                                    clientID=row.ClientID))
        return acceptances


class IndexRequestHandler(tornado.web.RequestHandler):
    def get(self, *args, **kwargs):
        self.write("hello")


class BrokerService(win32serviceutil.ServiceFramework):
    _svc_name_ = 'BrokerService'
    _svc_display_name_ = 'BrokerService'

    def __init__(self, *args):
        win32serviceutil.ServiceFramework.__init__(self, *args)
        self.log(u'init')
        self.stop_event = win32event.CreateEvent(None, 0, 0, None)

    def log(self, msg):
        import servicemanager

        servicemanager.LogInfoMsg(msg)

    def SvcDoRun(self):
        self.ReportServiceStatus(win32service.SERVICE_START_PENDING)
        try:
            self.ReportServiceStatus(win32service.SERVICE_RUNNING)
            self.start()
            self.log('wait')
            win32event.WaitForSingleObject(self.stop_event,
                                           win32event.INFINITE)
            self.log('done')
        except Exception, x:
            self.log('Exception : %s' % x)
            self.SvcStop()

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self.stop_event)
        self.ReportServiceStatus(win32service.SERVICE_STOPPED)

    def start(self):
        args = get_config()
        host = args.get("Broker", "Host")
        port = args.get("Broker", "Port")
        import sys
        from getopt import getopt

        opts, _ = getopt(sys.argv[1:], "s:p:h")
        for o, v in opts:
            if o == "-s":
                host = v
            elif o == "-p":
                port = int(v)
            elif o == "-h":
                print __doc__
            else:
                print "unkown option: " + o
                print __doc__
        self.log(u"启动host:%s, port:%s" % (host, port))
        main(host, port)


if __name__ == '__main__':
    win32serviceutil.HandleCommandLine(BrokerService)