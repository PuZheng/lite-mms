#! /usr/bin/env python
import sys

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print 'Usage: create_codernity_db.py <db_path>'
        sys.exit(1)

    from CodernityDB.database import Database
    codernity_db = Database(sys.argv[1])
    codernity_db.create()
    from lite_task_flow.indexes import add_index
    add_index(codernity_db)
    from lite_mms.indexes import TaskWithGroup
    codernity_db.add_index(TaskWithGroup(codernity_db.path, TaskWithGroup.TAG))
