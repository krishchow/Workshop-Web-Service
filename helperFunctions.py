from flask import request, Response, abort
from flask_sqlalchemy import SQLAlchemy
from database import myDB
from typing import Callable, Union
from flask_sqlalchemy import Model


def keyFunction() -> str:
    return request.headers.get('key')


def check_auth(key, db: myDB) -> bool:
    return db.verifyKey(key)


def _requires_auth(f: Callable, database=None) -> Union[Callable, Response]:
    def decorated(*args, **kwargs):
        auth = request.headers.get('key')
        if not check_auth(auth, database):
            print('{0} auth failed'.format(auth))
            return abort(401)
        return f(*args, **kwargs)
    return decorated


def generatePokeModel(sqlDB: SQLAlchemy) -> Model:
    class Pokemon(sqlDB.Model):
        id = sqlDB.Column(sqlDB.Integer, unique=True, nullable=False,
                          primary_key=True, autoincrement=True)
        Name = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
        Type1 = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
        Type2 = sqlDB.Column(sqlDB.String(80), unique=False, nullable=True)
        Total = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        HP = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        Attack = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        Defense = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        SpAttack = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        SpDefense = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        Speed = sqlDB.Column(sqlDB.Integer, unique=False, nullable=False)
        Gen = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
        isLegend = sqlDB.Column(sqlDB.String(80), unique=False, nullable=False)
        CreatedBy = sqlDB.Column(sqlDB.String(80), unique=False,
                                 nullable=False)

        def __repr__(self):
            return '<User %r>' % self.Name
    return Pokemon


def generateUserModel(sqlDB: SQLAlchemy) -> Model:
    class User(sqlDB.Model):
        key = sqlDB.Column(sqlDB.String(32), unique=True,
                           nullable=False, primary_key=True)

        def __repr__(self):
            return '<User %r>' % self.key
    return User
