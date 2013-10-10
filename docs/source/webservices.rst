###########
webservices
###########

userGroup:
1：车间主任
2：班组长
3：装卸工
4：质检员
5:收发员
6：调度员

'''注释后面打*的字段可选填'''

************************
post-auth-login(客户端登陆接口)
************************

：request
=======

**POST /auth_ws/login?username=<str>&password=<str>**

* username - 用户名 
* password - 用户密码 

response
========
* 200 - 成功::

.. code-block:: python
   
   {
    "username": <str>, # 用户名
    "teamID": <int>, # 班组ID
    "userID": <int>, # 用户ID
    "departmentID": <int+>, # 车间ID, 包括多个，存在一个车间主任管理多个班组的情况。
    "userGroup": <int>, # 
    "token": <str>, 
   }
      
* 403/401 - 错误::

.. code-block:: python

   "actual error reason"
   
example
=======

* 请求

**POST /auth_ws/login?username=xiechao&password=asdf**

* 返回
   
   * http code - 200
   * 数据
.. code-block:: python
   
   {
       "username": "wangjiali",
       "teamID": "22",
       "userID": "10000",
       "departmentID": "2,3",
       "userGroup": "1"
   }
   
*********************************
get-unload-session-list(获取卸货会话列表)
*********************************

获取的卸货会话都是未完成的

request
=======
**GET /cargo_ws/unload-session-list?index=<int>&cnt=<int>&auth_token=<str>**

* \*index - 返回的集合在所有卸货会话列表中的起始位置，默认为0
* \*cnt - 返回的卸货会话数量，默认为sys.maxint

response
========
* 200 - 成功
.. code-block:: python
   
   {
    "total_cnt": <int>,
    "data": [
        {
            "sessionID": <int>, # 会话ID
            "plateNumber": <str>, # 车牌号 
            "isLocked": 1|0, # 是否被锁定
        },
        ...
    ]
   }
* 403/401 - 错误
.. code-block:: python

   "actual error reason"

example
=======
* 请求
**GET /cargo_ws/unload-session-list&auth_token=xxx**

* 响应

   * http code: 200
   * 数据

.. code-block:: python
   {
    "total_cnt": 400,
    "data": [
        {
            "sessionID": 1,
            "plateNumber": "ZA000001",
            "isLocked": 1,
        },
        {
            "sessionID": 2,
            "plateNumber": "ZA000002",
            "isLocked": 0,
        },
        {
            "sessionID": 3,
            "plateNumber": "ZA000003",
            "isLocked": 0,
        }
    ]
   }

**************************
get-harbour-list(获取装卸货点列表)
**************************

request
=======
**GET /cargo_ws/harbour-list&auth_token=<str>**

response
========
* 200 - 成功

.. code-block:: python

   [
      <str>, # harbours
      ...
   ]

* 401 - 失败

.. code-block:: python
   
   "actual error reason"

example
=======

* 请求
**GET /cargo_ws/harbour-list&auth_token=<str>**

* 响应

   * http code - 200
   * 数据
.. code-block:: python

   [
      "车间一",
      "车间二"
   ]

************************
post-unload-task(生成卸货任务)
************************

此接口需要装卸工角色

request
=======

**POST /cargo_ws/unload-task?customer_id=<int>&harbour=<int>&is_finished=[0|1]&session_id=<int>&auth_token=<str>**

**<raw_picture_data>**

* customer_id - 客户id
* harbour - 卸货点名称
* \* is_finished - 是否完全卸货, 0代表没有，1代表完毕。可选项，默认为0
* session_id - 卸货会话id
* raw_picture_data - 原始图片数据

response
========
* 200 - 成功 

.. code-block:: python
   
   <int> # unload task id, 代表新创建的卸货任务ID 

* 403/401 - 失败 

.. code-block:: python

   "error reason"
 
example
=======
* 请求：
**POST http://<your site>/cargo_ws/unload-task?session_id=1&is_finished=1&harbour=装卸点1&customer_id=2&auth_token=xxx**

* 返回：
     * http code - 200
     * 数据:
      
.. code-block:: python

     10001


**************************
get-work-command(获取工单)
**************************

获取单个工单

request
=======

**GET /manufacture_ws/work-command/<work_command_id:int>?auth_token=<str>**

* work_command_id - 工单ID


response
========

* 200 - 成功

.. code-block:: python

    {
        "customerName": <string>, # 客户名称
        "department": {
            "id": <int>, # 车间ID
            "name": <string>, # 车间名称	
        }
        "handleType": <int>, # 处理类型
        "id": <int>, # 工单ID
        "isUrgent": 1|0, # 是否加急，1加急。
        "lastMod": <int>, # last modified time, seconds since epoch
        "orderID": <int>, # 订单ID
        "orderNum": <str>, # 订单号
        "orderCreateTime": <int>, # 订单创建时间，seconds since epoch
        "orderType": <int>, # 工单类型
        "orgWeight": <int>, # 工序前重量 , 需要说明的是，若工单类型为瑞格或者紧固件，那么这个值只有参考意义。               
        "orgWeight": <int>, # 工序前重量 
        "picPath": <str>, # 图片链接
        "previousProcedure": <string>, # 上一道工序名称，可为空
        "procedure": <string>, # 当前工序名，可为空
        "processedCount": <int>, # 桶数或者件数，视工单所属的订单类型而定
        "processedWeight": <int>, # 工序后重量， 若工单类型为瑞格或者紧固件，那么这个值只有参考意义。
        "productName": <string>, # 产品名称 
        "status": <int>, # 状态
        "subOrderId": <int>, # 子订单ID
        "team": {
            id: <int>, # 班组ID
            name: <string>, # 组名称
        }
        "technicalRequirements": <string>, # 技术要求，可为空
        "rejected": <int>, # 是否退货
        "qirList": [
            {
                result: <int>,  # 质检结果,
                weight: <int>,  # 质检重量,
                id: <int>,  # 质检报告ID,
                quantity: <int>,  # 质检数量,
                picUrl: <str>,  # 质检报告图片链接
                actorId: <int>,  # 操作员ID
            }
        ]
    }
   
* 404 - 该工单不存在

*****************************
get-work-command-list(获取工单列表)
*****************************

获取一系列的工单列表，其排序规则如下：

* 首先按加急与否进行排序
* 其次，按工单上一次状态变更的时间由远及近进行排序。
例如：存在A，B两个待分配工单，这两个工单排产的时间分别是 \*2012-9-10[10:09:10]\* 和 \*2012-9-10[9:50:07]\* , 那么B要排在A的前面 


request
=======

**GET /manufacture_ws/work-command-list?department_id=<int>&team_id=<int>&start=<int:0>&cnt=<int:sys.maxint>&status=<int>+&auth_token=<str>**

* \*department_id - 车间ID， 若为空，则team_id不能为空
* \*team_id - 班组ID， 若为空，则department_id不能为空
* \*start - 返回的工单列表在所有符合其他参数条件的工单列表中的起始位置, 若为空，默认为0
* \*cnt - 返回的工单数量，若为空，默认为sys.maxint
* status - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单状态的说明, 可以是多种工单状态的组合, 若是多种工单状态的组合，中间用','隔开

response
========
* 200 - 成功

.. code-block:: python

    {
        "totalCnt": <int>, # 总数量
        "data": [
            {
                "customerName": <string>, # 客户名称
                "department": {
                    "id": <int>, # 车间ID
                    "name": <string>, # 车间名称	
                }
                "handleType": <int>, # 处理类型
                "id": <int>, # 工单ID
                "isUrgent": 1|0, # 是否加急，1加急。
                "lastMod": <int>, # last modified time, seconds since epoch
                "orderID": <int>, # 订单ID
                "orderNum": <str>, # 订单号
                "orderCreateTime": <int>, # 订单创建时间，seconds since epoch
                "orderType": <int>, # 工单类型
                "orgWeight": <int>, # 工序前重量 , 需要说明的是，若工单类型为瑞格或者紧固件，那么这个值只有参考意义。               
                "orgCount": <int>, # 工序前数量 
                "picPath": <str>, # 图片链接
                "previousProcedure": <string>, # 上一道工序名称，可为空
                "procedure": <string>, # 当前工序名，可为空
                "processedCount": <int>, # 桶数或者件数，视工单所属的订单类型而定
                "processedWeight": <int>, # 工序后重量， 若工单类型为瑞格或者紧固件，那么这个值只有参考意义。
                "productName": <string>, # 产品名称 
                "status": <int>, # 状态
                "subOrderId": <int>, # 子订单ID
                "team": {
                    id: <int>, # 班组ID
                    name: <string>, # 组名称
                }
                "technicalRequirements": <string>, # 技术要求，可为空
                "rejected": <int>, # 是否退货
                "qirList": [
                    {
                    result: <int>,  # 质检结果,
                    weight: <int>,  # 质检重量,
                    id: <int>,  # 质检报告ID,
                    quantity: <int>,  # 质检数量,
                    picUrl: <str>,  # 质检报告图片链接
                    actorId: <int>,  # 操作员ID
                    }
                ]
            }
        ]
    }
   

有关orderType的说明，请见 :py:mod:`lite_mms.constants.default` 中对各种订单类型的说明

这里特别需要说明的是 **picPath** 字段， 这个字段的含义是工序的工序前加工件的照片，也就是说：

1. 工单第一次分配时，取子订单的照片。

2. 工单结束，进入下道工序时，质检员拍的工序后产品照片。

若照片有缺失，不会回溯。

* 401 - 失败

.. code-block:: python
   
   "actual error reason"
   
example
=======
* 请求：
**POST http://<your site>/manufacture_ws/work-command-list?department_id=1&team_id=2&status=3,5&auth_token=xxx**

* 返回：
     * http code - 200
     * 数据:

.. code-block:: python

   {
       "totalCnt": 8,
       "data": [
           {
               "status": 3,
               "processedWeight": 0,
               "customerName": "赛瑞",
               "orgCount": 0,
               "team":  {
			"id": 1, 
			"name": "1号班组",
		}
               "productName": "workpiece",
               "department":  {
			"id": 1,
			"name": "一号车间",
		}
               "subOrderId": 1,
               "technicalRequirements": "",
               "lastMod": 1349851179,
               "id": 1,
               "orderID": 1,
               "previousProcedure": "",
               "orderType": 1,
               "isUrgent": 0,
               "picPath": "",
               "processedCount": 0,
               "handleType": 1,
               "orgWeight": 1000,
               "procedure": "screw"
               "rejected": 0, 
           }
       ]
   }

*************************
get-customer-list(获取客户列表)
*************************

request
=======
**GET /order_ws/customer-list&auth_token=<str>**

response
========

* 200 - 成功， 即使没有一个客户列表

.. code-block:: python

   [
       {
           "id": <int>, # 用户ID
           "name": <str>, # 用户名称
           "abbr": <str>, # 拼音首字母缩写，例如"杭州Nokia"的缩写是"hznokia"
       },
   ]

example
=======
略

*********************
get-team-list(获取班组列表)
*********************

request
=======
**GET /manufacture_ws/team-list?department_id=<int>&auth_token=<str>**

* \* department_id - 车间ID

response
========
* 200 - 成功

.. code-block:: python

   [
       {
           "id": <int>, # 班组ID
           "name": <str>, # 班组名称
       },
       ...
   ]

* 401 - 失败

.. code-block:: python
   
   "actual error reason"
   
example
=======

* 请求

**GET /manufacture_ws/team-list?department_id=100&auth_token=xxx**

* 返回值
   * http code - 200
   * 数据

.. code-block:: python

   [
       {
           "id": 100,
           "name": "alpha"
       },
       {
           "id": 101,
           "name": "delta"
       }
   ]

.. _assign-work-command:

*************************
assign-work-command(分配工单)
*************************

此接口需要车间主任权限

request
=======

**PUT /manufacture_ws/work-command/<int>?team_id=<int>&action=203&auth_token=<str>**

* work_command_id - 工单id
* team_id - 被分配的班组id
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明

response
========

* 200 - 成功, 返回更新后的工单

.. code-block:: python

    {
        "customerName": <string>, # 客户名称
	"department": {
		"id": <int>, # 车间ID
		"name": <string>, # 车间名称	
	}
        "handleType": <int>, # 处理类型
        "id": <int>, # 工单ID
        "isUrgent": 1|0, # 是否加急，1加急。
        "lastMod": <int>, # last modified time, seconds since epoch
        "orderID": <int>, # 工单ID
        "orderType": <int>, # 工单类型
        "orgCount": <int>, # 工序前的桶数或者件数，视工单所属的订单类型而定
        "orgWeight": <int>, # 工序前重量 , 需要说明的是，若工单类型为瑞格或者紧固件，那么这个值只有参考意义。
        "picPath": <str>, # 图片链接
        "previousProcedure": <string>, # 上一道工序名称，可为空
        "procedure": <string>, # 当前工序名，可为空
        "processedCount": <int>, # 桶数或者件数，视工单所属的订单类型而定 
        "processedWeight": <int>, # 工序后重量， 若工单类型为瑞格或者紧固件，那么这个值只有参考意义。        
        "productName": <string>, # 产品名称 
        "status": <int>, # 状态
        "subOrderId": <int>, # 子订单ID
        "team": {
		"id": <string>, # 班组ID
		"name": <string>, # 组名称
	}
        "technicalRequirements": <string>, # 技术要求，可为空
        "unit": <string>, # 单位
        "rejected": <int>, # 是否退货
    }
   
有关orderType的说明，请见 :py:mod:`lite_mms.constants.default` 中对各种订单类型的说明

* 403/401 - 失败

一般可能发生在工单当前状态不是 **待分配** 

.. code-block:: python

   "actual error reason"
   
example
=======

* 请求

**PUT /manufacture_ws/work-command/123?team_id=23&action=203&auth_token=xxx**

* 返回值

   * http code: 200
   * 数据
   
.. code-block:: python
   
     {
         "status": 2,
         "processedWeight": 0,
         "customerName": "赛瑞",
         "orgCount": 0,
         "team": "1号班组",
         "productName": "workpiece",
         "department":  {
		"id": 1, 
		"name": "一号车间",
	}
	"team": {
		"id": 1, 
		"name": "一号班组", 
	}
         "subOrderId": 1,
         "technicalRequirements": "",
         "lastMod": 1349851179,
         "id": 1,
         "orderID": 1,
         "previousProcedure": "",
         "orderType": 1,
         "isUrgent": 0,
         "picPath": "",
         "processedCount": 0,
         "handleType": 1,
         "orgWeight": 1000,
         "procedure": "screw",
         "unit: "件",
         "rejected": 0, 
     }

*****************************
add-processed-weight(增加工序后重量)
*****************************

只有工单在 **待请求结束或结转** 时才可以增加工序后重量

此接口需要班组长权限

request
=======

**PUT /manufacture_ws/work-command/<int>?weight=<int>&quantity=<int>&action=204&is_finished=<1|0>&auth_token=str>**

* work_command_id - 工单id
* weight - 重量
* \*quantity - **增加** 的件数，对于不同类型的工单有不同的含义，标准-公斤；瑞格-件数；紧固件-桶数；对于计件类型，quantity是必须填写的
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明
* \*is_finished - 是否结束，1为结束，若不传，默认为0


response
========

* 200 - 成功，返回修改后的工单信息, 返回信息见 :ref:`assign-work-command`

* 403/401 - 失败

一般可能发生在工单当前状态不是"待请求结束或结转"

.. code-block:: python

   "actual error reason"

example
=======

请参考 :ref:`assign-work-command`
   
***********************************
request-end-work-command(请求结束或结转工单)
***********************************

此接口需要班组长权限

request
=======

**PUT /manufacture_ws/work-command/<int>?action=[205|206]&auth_token=<str>**

* work_command_id - 工单id, 可以是一个工单id列表。例如 **1,2,3**
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明, 205代表**结束**， 206代表**结转**

response
========

* 200 - 成功，返回修改后的工单信息, 返回信息见 :ref:`assign-work-command`

 *这里特别需要说明的是： 若修改的是多个工单，那么返回的工单信息是多个*

* 403/401 - 失败

一般可能发生在工单当前状态不是**待请求结束或结转**

.. code-block:: python

   "actual error reason"

example
=======

   请参考 :ref:`assign-work-command`


*************************
refuse-work-command(打回工单)
*************************
车间主任打回工单

此接口需要车间主任权限

reqeust
=======

**PUT /manufacture_ws/work-command/<int>?reason=<str>&action=209&auth_token=<str>**

* work_command_id - 工单id
* \*reason - 理由
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明

response
========

* 200 - 成功
   返回数据请参考 :ref:`assign-work-command`
   
* 403/401 - 失败

一般可能发生在工单当前状态不是**待分配**

example
=======

   请参考 :ref:`assign-work-command`

************************************
affirm-retrieve-work-command(确认回收工单)
************************************
车间主任确认回收工单

此接口需要车间主任权限

request
=======

**PUT /manufacture_ws/work-command/<int>?action=211&weight=<int>&quantity=<int>&auth_token=<str>**

* work_command_id - 工单id
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明
* \*quantity - 最终生产完成的件数，对于不同类型的工单有不同的含义，标准-公斤；瑞格-件数；紧固件-桶数；对于计件类型，quantity是必须填写的
* weight - 最终生产完成的重量

response
========

* 200 - 成功

   返回数据请参考 :ref:`assign-work-command`
   
* 403/401 - 失败

一般可能发生在工单当前状态不是**锁定**

example
=======

   请参考 :ref:`assign-work-command`

******************************************
refuse-retrieval-work-command(拒绝回收工单)
******************************************
车间主任拒绝回收工单

此接口需要车间主任权限

request
=======

**PUT /manufacture_ws/work-command/<int>?action=213&auth_token=<str>**

* work_command_id - 工单id, 支持多个工单id，可以用","隔开
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明

response
========

* 200 - 成功

   返回数据请参考 :ref:`assign-work-command`
   
* 403/401 - 失败
一般可能发生在工单当前状态不是**锁定**

example
=======

   请参考 :ref:`assign-work-command`


****************************************
create-quality-inspection-report(生成质检报告)
****************************************
生成质检报告

此接口需要质检员权限

request
=======

**POST /manufacture_ws/quality-inspection-report?&work_command_id=<int>&quantity=<int>&result=<int>&auth_token=<str>**

<picture data>

* actor_id - 提交人id
* work_command_id - 对应的工单id
* \*quantity - **增加** 的重量，对于不同类型的工单有不同的含义，标准-公斤；瑞格-件数；紧固件-桶数；
* result - 质检结果，请参考 :py:mod:`lite_mms.constants.quality_inspection`

response
========

* 200 - 成功
   
.. code-block:: python

    {
        "id": <int>, # 质检报告id
        "quantity": <int>, # 数量
        "weight": <int>, # 质量，对于瑞格和紧固件，仅仅有参考意义
        "result": <int>, # 质检结果
        "work_command_id": <int>, # 工单id
        "actor_id": <str>, # 质检人id
        "pic_url": <string>, # 图片链接
    }
   
* 403/401 - 失败

.. code-block:: python
   
   "actual error reason"
   
example
=======

略

****************************************
update-quality-inspection-report(修改质检报告)
****************************************
修改质检报告

此接口需要质检员权限

request
=======

**PUT /manufacture_ws/quality-inspection-report?id=<int>&quantity=<int>&result=<int>&auth_token=<str>**

* id - 质检报告id
* actor_id - 提交人id
* \*quantity - **增加** 的重量，对于不同类型的工单有不同的含义，标准-公斤；瑞格-件数；紧固件-桶数；
* result - 质检结果，请参考 :py:mod:`lite_mms.constants.quality_inspection`

response
========

* 200 - 成功
返回更新的质检报告数据:

.. code-block:: python

    {
        "id": <int>, # 质检报告id
        "quantity": <int>, # 数量
        "weight": <int>, 
        "result": <int>, # 质检结果
        "work_command_id": <int>, # 工单id
        "actor_id": <str>, # 质检人id
        "pic_url": <string>, # 图片链接
    }
   
* 404 - 没有对应的质检报告

.. code-block:: python
   
   "actual error reason"

* 403/401 - 失败

.. code-block:: python
   
   "actual error reason"
   
example
=======

略

****************************************
delete-quality-inspection-report(删除质检报告)
****************************************
删除质检报告
此接口需要质检员权限

request
=======

**DELETE /manufacture_ws/quality-inspection-report?id=<int>&auth_token=<str>**

或者

**POST /manufacture_ws/delete-quality-inspection-report?id=<int>&actor_id=<int>**

* id - 质检报告id
* actor_id - 提交人id

response
========

* 200 - 成功
   
* 403/401 - 失败

.. code-block:: python
   
   "actual error reason"
   
example
=======

略


********************************
submit-quality-inspection(提交质检单)
********************************

提交质检单，根据对应的质检报告，生成新的工单, 对于已经完成的，需要加入待发货列表中去。

此接口需要质检员权限

request
=======

**PUT /manufacture_ws/work-command/<int>?action=212&deduction=<int>&auth_token=<str>**

* work_command_id - 工单id
* actor_id - 发起人id，这里为质检员
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明
* \*deduction - 扣量，必须以公斤为单位，默认为0

response
========

* 200 - 成功

   返回数据请参考 :ref:`assign-work-command`, 即处于结束状态的原工单
   
* 403/401 - 失败

一般可能发生在工单当前状态不是**待质检**

example
=======

   请参考 :ref:`assign-work-command`
   
*********************************
get-delivery-session-list(获取发货会话列表)
*********************************

获取的发货会话都是未完成的，而且有仓单的，按创建时间由近及远进行排序


request
=======
**GET /delivery_ws/delivery-session-list&auth_token=<str>**

response
========
* 200 - 成功

.. code-block:: python

    [
        {
            "sessionID": <int>, # 会话ID
            "plateNumber": <str>, # 车牌号 
            "isLocked": 1|0, # 是否被锁定 
        },
        ...
    ]
   

* 401 - 错误

.. code-block:: python

   "actual error reason"

example
=======
* 请求
**GET /delivery_ws/delivery-session-list&auth_token=xxx**

* 响应

   * http code: 200
   * 数据

.. code-block:: python

    [
        {
            "sessionID": 1,
            "plateNumber": "ZA000001",
            "isLocked": 0,
        },
        {
            "sessionID": 2,
            "plateNumber": "ZA000002",
            "isLocked": 0,
        },
        {
            "sessionID": 3,
            "plateNumber": "ZA000003",
            "isLocked": 0,
        }
    ]

**************************************
get-delivery-session(获取发货会话详情)
**************************************

request
=======

**GET /delivery_ws/delivery-session?id=<int>&auth_token=<str>**

response
========

* 200 - 成功

.. code-block:: python

    {
        "id": <int>, # 发货会话id
        "plate": <str>, # 车牌号
        "store_bills": {      
            <str>: # 订单编号
            {
                <str>: # 子订单编号
                [ 
                    {
                        "id": <int>, # 仓单ID
                        "harbor": <str>, # 装卸点
                        "product_name": <str>, # 产品名称
                        "customer_name": <str>, # 客户名称
                        "pic_url": <str>, # 图片链接
                        "unit": <str>, # 单位
                    }
                    ...
                ]
            }
            ...
        } # 卸货任务列表，按创建时间，由新到旧进行排序
    }

* 404/401 

.. code-block:: python

   "actual error reason"
  

example
=======

.. code-block:: python

    {
        "id": 1, 
        "plate": "浙A 00001",
        "store_bills": {
            "123465691233": {
                "1":
                [
                    {
                        "id": 1,
                        "habor": "卸货点1",
                        "product_name": "螺丝",
                        "customer_name": "宁波紧固件厂",
                        "pic_url": "xxxxxxxx",
                        "unit": "件", 
                    },
                    {
                        "id": 2,
                        "habor": "卸货点2",
                        "product_name": "螺母",
                        "customer_name": "宁波紧固件厂",
                        "pic_url": "xxxxxxxx",
                        "unit": "件"， 
                    },
                ]
                "2":
                [
                    {
                        "id": 3,
                        "habor": "卸货点2",
                        "product_name": "螺丝刀",
                        "customer_name": "宁波紧固件厂",
                        "pic_url": "xxxxxxxx",
                        "unit": "件"， 
                    },
                ]
            }
        }
    }

***********************************
post-delivery-task(创建发货任务)
***********************************

已经完成的仓单不能反复提交， 只能选择同一个订单的一个或多个仓单，只能有一个未完成仓单

此接口需要装卸工权限

request
=======

**POST /delivery_ws/delivery-task?sid=<int>&is_finished=[0|1]&remain=<int>&auth_token=<str>**

.. code-block:: python
    
    [
        {
            "store_bill_id": <int>, # 处理的仓单号
            "is_finished": <1|0>, # 该仓单是否完全装货, 1代表完全装货
        }
        ...
    ]

* sid - 发货会话id
* is_finished - 是否发货会话结束, 1代表结束
* auth_token - login返回的token
* \*remain - 未完成件数(计件类型)或重量（计重类型），若有为完成仓单，为必填项

response
========

* 200 - 成功

.. code-block:: python

    {
        "store_bill_id_list": [
            <int>+, # 已经完成的仓单列表，其规则具体见[ticket 224]
        ],
        "actor_id": <int>, 
        "id": <int>, # 新生成的发货任务ID
    }

* 403/401 - 失败

.. code-block:: python

   "actual reason"

***********************************
retrive-quality-inspection(打回质检单)
***********************************

前一天提交的或者生成的工单、仓单已经排产或者发货的都不能打回质检单

此操作需要质检员权限

request
=======

**PUT /manufacture_ws/work-command/<int>?action=214&auth_token=<str>**

* work_command_id - 工单id
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明

response
========

* 200 - 成功

   返回数据请参考 :ref:`assign-work-command`, 即处于结束状态的原工单
   
* 403/401 - 失败

.. code-block:: python

   "actual reason"


example
=======

   请参考 :ref:`assign-work-command`

***********************************
quick-carry-forward(快速结转)
***********************************

班组长可以将工单快速结转，使工单完成的部分先质检剩下的继续做
此操作需要质检员权限

request
=======

**PUT /manufacture_ws/work-command/<int>?action=215**

* work_command_id - 工单id
* action - 见 :py:mod:`lite_mms.constants.work_command` 中对各种工单操作的说明

response
========

* 200 - 成功

   返回数据请参考 :ref:`assign-work-command`, 即处于结束状态的原工单
   
* 403/401 - 失败

.. code-block:: python

   "actual reason"


example
=======

   请参考 :ref:`assign-work-command`
