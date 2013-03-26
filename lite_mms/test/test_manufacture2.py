#-*- coding:utf-8 -*-
from pyfeature import Feature, Scenario, given, and_, then, when

from lite_mms.basemain import app, db


def test():
    from pyfeature import flask_sqlalchemy_setup

    flask_sqlalchemy_setup(app, db, create_step_prefix=u"创建")

    with Feature(u"调度员预排产", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            sub_order1 = and_(u"计重类型子订单", department, weight=1000)
            sub_order2 = and_(u"计件类型子订单", department, weight=800, quantity=8)
            sub_order3 = and_(u"计重类型子订单,退货", department, weight=200)

        with Scenario(u"最简场景"):
            when(u"调度员从子订单中预排产,成功", sub_order1, 100, username, password)
            then(u"子订单中未分配的重量是900公斤", sub_order1)
            and_(u"生成了新的工单,其重量是100公斤", sub_order1)

        with Scenario(u"排产重量超过子订单重量"):
            rv = when(u"调度员从子订单中预排产,失败", sub_order1, 1000, username, password)
            and_(u"子订单中未分配的重量是900公斤", sub_order1)

        with Scenario(u"预排产计件类型的子订单"):
            when(u"调度员从子订单中预排产,成功", sub_order2, 500, username, password,
                 quantity=5)
            then(u"子订单中未分配的重量是300公斤,件数是3件", sub_order2)
            and_(u"生成了新的工单,其重量是500公斤,件数是5件")

        with Scenario(u"退货流程"):
            when(u"调度员从子订单中预排产,成功", sub_order3, 200, username, password)
            work_command = then(u"质检员的待质检列表中增加了一个200公斤的工单")
            and_(u"这个工单的子订单是3", work_command, sub_order3)

    with Feature(u"调度员调度", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            sub_order1 = and_(u"计重类型子订单", department, weight=1000)
            wc = and_(u"调度员从子订单中预排产,成功", sub_order1, 100, username, password)

        with Scenario(u"最简场景"):
            when(u"调度员将工单调度给车间", wc, department, username, password)
            then(u"车间主任可获取的工单列表包括工单", department, wc)

    with Feature(u"调度员回收工单", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            sub_order1 = and_(u"计重类型子订单", department, weight=1000)
            wc1 = and_(u"调度员从子订单中预排产,成功", sub_order1, 100, username, password)
            and_(u"调度员将工单调度给车间", wc1, department, username, password)
            wc2 = and_(u"调度员从子订单中预排产,成功", sub_order1, 500, username, password)
            and_(u"调度员将工单调度给车间", wc2, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc2, team)

        with Scenario(u"调度员回收未分配的工单"):
            when(u"调度员回收工单", wc1, username, password)
            then(u"工单的状态转变为未调度", wc1)
            and_(u"工单没有出现在车间主任的工单列表中", department, wc1)

        with Scenario(u"调度员回收已经分配的工单"):
            when(u"调度员回收工单", wc2, username, password)
            then(u"工单的状态转变为锁定", wc2)
            and_(u"工单不能够再次增加重量", wc2)
            when(u"车间主任确认回收工单", wc2)
            wc3 = then(u"工单生产完毕的部分成为一个待质检工单,重量是300公斤", wc2)
            and_(u"工单重新变成待调度,重量是200公斤", wc2)

        with Scenario(u"调度员回收已经生产完毕的工单"):
            result_code = when(u"调度员回收工单", wc3, username, password)
            then(u"返回403错误", result_code)
            and_(u"工单的状态仍然是待质检", wc3)

    with Feature(u"车间主任分配工单", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            sub_order1 = and_(u"计重类型子订单", department, weight=1000)
            wc1 = and_(u"调度员从子订单中预排产,成功", sub_order1, 100, username, password)
            and_(u"调度员将工单调度给车间", wc1, department, username, password)
            wc2 = and_(u"调度员从子订单中预排产,成功", sub_order1, 500, username, password)
            and_(u"调度员将工单调度给车间", wc2, department, username, password)

        with Scenario(u"最简流程"):
            when(u"车间主任分配工单给班组", department, wc2, team)
            then(u"工单出现在班组的工单列表中", wc2, team)

        with Scenario(u"车间主任打回工单"):
            when(u"车间主任打回工单", wc1)
            then(u"工单的状态转变为车间主任打回", wc1)

    with Feature(u"班组长生产工单", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            sub_order1 = and_(u"计重类型子订单", department, weight=1000)
            wc1 = and_(u"调度员从子订单中预排产,成功", sub_order1, 100, username, password)
            and_(u"调度员将工单调度给车间", wc1, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc1, team)
            wc2 = and_(u"调度员从子订单中预排产,成功", sub_order1, 500, username, password)
            and_(u"调度员将工单调度给车间", wc2, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc2, team)
            sub_order2 = and_(u"计件类型子订单", department, weight=1000, quantity=10)
            wc3 = and_(u"调度员从子订单中预排产,成功", sub_order2, 500, username, password,
                       quantity=5)
            and_(u"调度员将工单调度给车间", wc3, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc3, team)
            wc4 = and_(u"调度员从子订单中预排产,成功", sub_order2, 500, username, password,
                       quantity=5)
            and_(u"调度员将工单调度给车间", wc4, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc4, team)

        with Scenario(u"最简流程"):
            when(u"班组长增加了工单的工序后重量100公斤", wc1)
            and_(u"班组长结束工单", wc1)
            then(u"工单的状态转变为待质检", wc1)
            and_(u"工单的工序后重量是100公斤", wc1)

        with Scenario(u"结束计件类型的工单"):
            when(u"班组长增加了工单的工序后重量210公斤,件数是2件", wc3)
            and_(u"班组长结束工单", wc3)
            then(u"工单的状态转变为待质检", wc3)
            and_(u"工单的工序后重量是210公斤,件数是2件", wc3)

        with Scenario(u"结转计重类型的工单"):
            when(u"班组长增加了工单的工序后重量400公斤", wc2)
            new_work_command = and_(u"班组长结转工单", wc2)
            then(u"工单的状态转变为待质检", wc2)
            and_(u"工单的状态转变为待分配", new_work_command)
            and_(u"工单重量是100公斤", new_work_command)

        with Scenario(u"结转计件类型的工单"):
            when(u"班组长增加了工单的工序后重量210公斤,件数是2件", wc4)
            new_work_command = and_(u"班组长结转工单", wc4)
            then(u"工单的状态转变为待分配", new_work_command)
            and_(u"工单的状态转变为待质检", wc4)
            and_(u"工单重量是300公斤,件数是3件", new_work_command)

        with Scenario(u"快速结转计重类型的工单"):
            and_(u"车间主任分配工单给班组", department, new_work_command, team)
            when(u'班组长增加了工单的工序后重量200公斤', new_work_command)
            gene_work_command = then(u'班组长快速结转工单成功', new_work_command)
            and_(u'工单状态还是待结束结转', new_work_command)
            and_(u"工单的状态转变为待质检", gene_work_command)

    with Feature(u"质检员质检工单", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            sub_order1 = and_(u"计重类型子订单", department, weight=1000)
            wc1 = and_(u"调度员从子订单中预排产,成功", sub_order1, 100, username, password)
            and_(u"调度员将工单调度给车间", wc1, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc1, team)
            and_(u"班组长增加了工单的工序后重量100公斤", wc1)
            and_(u"班组长结束工单", wc1)
            wc2 = and_(u"调度员从子订单中预排产,成功", sub_order1, 500, username, password)
            and_(u"调度员将工单调度给车间", wc2, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc2, team)
            and_(u"班组长增加了工单的工序后重量600公斤", wc2)
            and_(u"班组长结束工单", wc2)
            sub_order2 = and_(u"计件类型子订单", department, weight=1000, quantity=10)
            wc3 = and_(u"调度员从子订单中预排产,成功", sub_order2, 500, username, password,
                       quantity=5)
            and_(u"调度员将工单调度给车间", wc3, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc3, team)
            wc4 = and_(u"调度员从子订单中预排产,成功", sub_order2, 500, username, password,
                       quantity=5)
            and_(u"调度员将工单调度给车间", wc4, department, username, password)
            and_(u"车间主任分配工单给班组", department, wc4, team)
            and_(u"班组长增加了工单的工序后重量210公斤,件数是2件", wc4)
            and_(u"班组长结转工单", wc4)

        with Scenario(u"计重类型全部合格结束"):
            weight = 100
            qir = when(u"质检结果合格结束", wc1, weight)
            and_(u"质检员提交质检单", wc1)
            then(u"生成一个仓单", qir, weight)

        with Scenario(u"计重类型部分返修,部分合格结束"):
            qir = when(u"质检结果部分返修,其他合格结束", wc2, 500, 100)
            and_(u"质检员提交质检单", wc2)
            then(u"生成一个仓单", qir, 100)
            and_(u"工单的状态转变为结束", wc2)
            new_work_command = and_(u"新工单状态为待分配", 500)

        with Scenario(u"质检员打回质检单"):
            when(u"取消质检单", wc2)
            then(u"工单状态还原为待质检", wc2)
            and_(u"新工单被删除", new_work_command)


    with Feature(u"检货", ["lite_mms.test.steps.manufacture2"]):
        with Scenario(u"准备数据"):
            group = given(u"调度员组")
            department = and_(u"车间1")
            team = and_(u"班组1", department)
            username = u'调度员'
            password = u"123dd"
            and_(u"调度员001", username, password, group)
            weight = 1000
            sub_order4 = and_(u"计重类型子订单,退货", department, weight)

        with Scenario(u"调度员分配"):
            when(u"调度员从子订单中预排产,成功", sub_order4, weight, username, password)
            work_command = then(u"生成一个待质检的工单, 工序为空", weight)

        with Scenario(u"质检员质检"):
            when(u"全部返镀", work_command, weight)
            and_(u"质检员提交质检单", work_command)
            then(u"原工单的状态为结束,待发货重量为0", work_command)
            work_command_new = and_(u"新工单状态为待排产", weight)

        with Scenario(u"质检员打回质检单"):
            when(u"取消质检单", work_command)
            then(u"工单状态还原为待质检", work_command)
            and_(u"新工单被删除", work_command_new)