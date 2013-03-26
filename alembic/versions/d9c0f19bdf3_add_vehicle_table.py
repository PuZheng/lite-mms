"""add vehicle table

Revision ID: 2c0588fede83
Revises: d9c0f19bdf2
Create Date: 2013-03-25 11:47:03.826029

"""

# revision identifiers, used by Alembic.
revision = 'd9c0f19bdf3'
down_revision = 'd9c0f19bdf2'

from datetime import datetime
from alembic import op
import sqlalchemy as sa
from lite_mms.constants import cargo as cargo_const


def upgrade():
    op.create_table("TB_VEHICLE", 
                   sa.Column("id", sa.Integer, primary_key=True),
                   sa.Column("plate", sa.String(64), nullable=False, unique=True))
    vehicle = sa.sql.table("TB_VEHICLE", 
                   sa.Column("id", sa.Integer, primary_key=True),
                   sa.Column("plate", sa.String(64), nullable=False, unique=True))
    plate = sa.sql.table("TB_PLATE", 
                    sa.Column("name", sa.String(32), nullable=False, primary_key=True))
    conn = op.get_bind()
    plates = [p for p in conn.execute(plate.select())]
    op.bulk_insert(vehicle, [{"plate": p.name} for p in plates])

    op.add_column("TB_UNLOAD_SESSION", sa.Column("status", sa.Integer, default=cargo_const.STATUS_LOADING, nullable=False))
    op.add_column("TB_UNLOAD_SESSION", sa.Column("vehicle_id", sa.Integer, sa.ForeignKey('TB_VEHICLE.id')))
    unload_session = sa.sql.table("TB_UNLOAD_SESSION", 
                                  sa.Column("id", sa.Integer, primary_key=True),
                                  sa.Column("plate", sa.String(32), nullable=False),
                                  sa.Column("gross_weight", sa.Integer, nullable=False),
                                  sa.Column("status", sa.Integer, default=cargo_const.STATUS_LOADING, nullable=False),
                                  sa.Column("vehicle_id", sa.Integer, sa.ForeignKey('TB_VEHICLE.id'), nullable=False),
                                  sa.Column("with_person", sa.Boolean, default=False),
                                  sa.Column("create_time", sa.DateTime, default=datetime.now),
                                  sa.Column("finish_time", sa.DateTime))
    unload_session_list = [us for us in conn.execute(unload_session.select())]
    for us in unload_session_list:
        vehicle_id = conn.execute(vehicle.select().where(vehicle.c.plate==us.plate)).fetchone().id
        op.execute(unload_session.update().where(unload_session.c.id==us.id).values(vehicle_id=vehicle_id).values(status=cargo_const.STATUS_CLOSED))


def downgrade():
    vehicle = sa.sql.table("TB_VEHICLE", 
                   sa.Column("id", sa.Integer, primary_key=True),
                   sa.Column("plate", sa.String(64), nullable=False, unique=True))
    op.drop_column("TB_UNLOAD_SESSION", "status")
    op.drop_column("TB_UNLOAD_SESSION", "vehicle_id")
    op.drop_table("TB_VEHICLE")

