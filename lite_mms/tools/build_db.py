# -*- coding: utf-8 -*-
"""
SYNOPSIS
    python build_db.py [options]
OPTIONS
    -h 
        show this help
    -s  <dbstr>
        the db connection string
"""
from hashlib import md5
import sys
from getopt import getopt
from flask import url_for
from lite_mms.basemain import app
import lite_mms.constants.groups as groups
import lite_mms.constants as constants
from lite_mms.permissions import permissions

def build_db():
    print "initialize " + app.config["SQLALCHEMY_DATABASE_URI"]
    import os
    dbstr = app.config["SQLALCHEMY_DATABASE_URI"]
    if dbstr.startswith("sqlite"):
        dir = os.path.split(dbstr[10:])[0]
        if dir and not os.path.exists(dir):
            os.makedirs(dir)
    from lite_mms.database import db, init_db
    from lite_mms import models
    db.drop_all()
    init_db()
    session = db.session

    for perm in permissions.keys():
        session.add(models.Permission(name=perm))
    session.commit()

    with app.test_request_context():
        app.preprocess_request()
        # init groups
        cargo_clerk = models.Group(u"收发员", url_for("cargo.index"))
        cargo_clerk.id = groups.CARGO_CLERK
        cargo_clerk.permissions = models.Permission.query.filter(
            models.Permission.name.like("%view_order%")).all()
        scheduler = models.Group(u"调度员", url_for("schedule.index"))
        scheduler.id = groups.SCHEDULER
        scheduler.permissions = models.Permission.query.filter(
            models.Permission.name.like(
                "%schedule_order%")).all() + models.Permission.query.filter(
            models.Permission.name.like("work_command%")).all()
        department_leader = models.Group(u"车间主任", url_for("manufacture.QI_work_command_list"))
        department_leader.id = groups.DEPARTMENT_LEADER
        team_leader = models.Group(u"班组长")
        team_leader.id = groups.TEAM_LEADER
        quality_inspector = models.Group(u"质检员", url_for("store_bill.index"))
        quality_inspector.id = groups.QUALITY_INSPECTOR
        quality_inspector.permissions = models.Permission.query.filter(
            models.Permission.name.like("%view_work_command")).all()
        loader = models.Group(u"装卸工")
        loader.id = groups.LOADER
        accountant = models.Group(u"财会人员", url_for("delivery.consignment_list"))
        accountant.permissions = [models.Permission.query.filter(models.Permission.name.like("%export_consignment%")).one()]
        accountant.id = groups.ACCOUNTANT
        administrator = models.Group(u"管理员", url_for("admin.index"))
        administrator.id = groups.ADMINISTRATOR
        administrator.permissions = models.Permission.query.all()

        session.add(cargo_clerk)
        session.add(scheduler)
        session.add(department_leader)
        session.add(team_leader)
        session.add(quality_inspector)
        session.add(loader)
        session.add(accountant)
        session.add(administrator)
        session.commit()

        # init user
        session.add(models.User('admin', md5('admin').hexdigest(), [administrator]))
        session.add(models.User('cc', md5('cc').hexdigest(), [cargo_clerk]))
        session.add(models.User('s', md5('s').hexdigest(), [scheduler]))
        #    -  一号车间
        cj1_dl = models.User('cj1', md5('cj1').hexdigest(), [department_leader])
        session.add(cj1_dl)
        #    -  二号车间
        cj2_dl = models.User('cj2', md5('cj2').hexdigest(), [department_leader])
        session.add(cj2_dl)
        #    -  三号车间
        cj3_dl = models.User('cj3', md5('cj3').hexdigest(), [department_leader])
        session.add(cj3_dl)
        #    -  抛砂车间
        pscj_dl = models.User('pscj', md5('pscj').hexdigest(), [department_leader])
        session.add(pscj_dl)
        #    -  整修车间
        zxcj_dl = models.User('zxcj', md5('zxcj').hexdigest(), [department_leader])
        session.add(zxcj_dl)
        #    -  超级车间主任
        cjcj_dl = models.User('cjcj', md5('cjcj').hexdigest(), [department_leader])
        session.add(cjcj_dl)
        #    -  101
        _101_tl = models.User('101', md5('101').hexdigest(), [team_leader])
        session.add(_101_tl)
        #    -  201
        _201_tl = models.User('201', md5('201').hexdigest(), [team_leader])
        session.add(_201_tl)
        #    -  202
        _202_tl = models.User('202', md5('202').hexdigest(), [team_leader])
        session.add(_202_tl)
        #    -  203
        _203_tl = models.User('203', md5('203').hexdigest(), [team_leader])
        session.add(_203_tl)
        #    -  301
        _301_tl = models.User('301', md5('301').hexdigest(), [team_leader])
        session.add(_301_tl)
        #    -  302
        _302_tl = models.User('302', md5('302').hexdigest(), [team_leader])
        session.add(_302_tl)
        #    -  401
        _401_tl = models.User('401', md5('401').hexdigest(), [team_leader])
        session.add(_401_tl)
        #    -  501
        _501_tl = models.User('501', md5('501').hexdigest(), [team_leader])
        session.add(_501_tl)
        session.add(models.User('qi', md5('qi').hexdigest(), [quality_inspector]))
        session.add(models.User('l', md5('l').hexdigest(), [loader]))
        session.add(models.User('a', md5('a').hexdigest(), [accountant]))
        session.commit()

        # init departments
        d1 = models.Department(u"一号车间", [cj1_dl, cjcj_dl])
        session.add(d1)
        d2 = models.Department(u"二号车间", [cj2_dl, cjcj_dl])
        session.add(d2)
        d3 = models.Department(u"三号车间", [cj3_dl, cjcj_dl])
        session.add(d3)
        d4 = models.Department(u"抛砂车间", [pscj_dl, cjcj_dl])
        session.add(d4)
        d5 = models.Department(u"整修车间", [zxcj_dl, cjcj_dl])
        session.commit()

        # init teams
        team1 = models.Team(u"101", d1, _101_tl)
        team2 = models.Team(u"201", d2, _201_tl)
        team3 = models.Team(u"202", d2, _202_tl)
        team4 = models.Team(u"203", d2, _203_tl)
        team5 = models.Team(u"301", d3, _301_tl)
        team6 = models.Team(u"302", d3, _302_tl)
        team7 = models.Team(u"401", d4, _401_tl)
        team8 = models.Team(u"501", d5, _501_tl)
        session.add(team1)
        session.add(team2)
        session.add(team3)
        session.add(team4)
        session.add(team5)
        session.add(team6)
        session.add(team7)
        session.add(team8)
        session.commit()

        # init procedure
        normal_procedure = models.Procedure(u"一般工序", [d1, d2, d3])
        paosha_procedure = models.Procedure(u"抛砂", [d4])
        zhengxiu_procedure = models.Procedure(u"整修", [d5])
        session.add_all([normal_procedure, paosha_procedure, zhengxiu_procedure])
        session.commit()

        # init harbors
        hr1 = models.Harbor(u"装卸点1", d1)
        hr2 = models.Harbor(u"装卸点2", d2)
        hr3 = models.Harbor(u"装卸点3", d3)
        hr4 = models.Harbor(u"装卸点4", d4)
        hr5 = models.Harbor(u"装卸点5", d5)

        # init harbor
        session.add(hr1)
        session.add(hr2)
        session.add(hr3)
        session.add(hr4)
        session.add(hr5)
        session.commit()

        # init product
        product_type_default = models.ProductType(constants.DEFAULT_PRODUCT_TYPE_NAME)
        session.add(product_type_default)
        session.commit()
        session.add(models.Product(constants.DEFAULT_PRODUCT_NAME, product_type_default))
        session.commit()

        session.flush()
        print "initialize success"

if __name__ == "__main__":
    opts, _ = getopt(sys.argv[1:], "s:h")
    for o, v in opts:
        if o == "-h":
            print __doc__
            exit(1)
        else:
            print "unknown option: " + o
    build_db()
