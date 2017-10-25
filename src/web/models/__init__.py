#! /usr/bin/env python
# -*- coding: utf-8 -*-

from .user import User
from .service import Service
from .request import Request

__all__ = ['Service', 'User', 'Request']

from sqlalchemy.engine import reflection
from sqlalchemy.schema import (MetaData,
                               Table,
                               DropTable,
                               ForeignKeyConstraint,
                               DropConstraint)


def db_empty(db):
    "Will drop every datas stocked in db."
    # From http://www.sqlalchemy.org/trac/wiki/UsageRecipes/DropEverything
    conn = db.engine.connect()

    # the transaction only applies if the DB supports
    # transactional DDL, i.e. Postgresql, MS SQL Server
    trans = conn.begin()

    inspector = reflection.Inspector.from_engine(db.engine)

    # gather all data first before dropping anything.
    # some DBs lock after things have been dropped in
    # a transaction.
    metadata = MetaData()

    tbs = []
    all_fks = []

    for table_name in inspector.get_table_names():
        fks = []
        for fk in inspector.get_foreign_keys(table_name):
            if not fk['name']:
                continue
            fks.append(ForeignKeyConstraint((), (), name=fk['name']))
        t = Table(table_name, metadata, *fks)
        tbs.append(t)
        all_fks.extend(fks)

    for fkc in all_fks:
        conn.execute(DropConstraint(fkc))

    for table in tbs:
        conn.execute(DropTable(table))
    # trans.commit()


def db_init(db):
    "Will create the database from conf parameters."
    db.create_all()
