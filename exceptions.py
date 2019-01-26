from flask import abort


class flaskException(Exception):
    def getPage():
        raise NotImplementedError


class notExist(flaskException):
    def getPage():
        return abort(404)


class badRequest(flaskException):
    def getPage():
        return abort(400)


class noPermissions(flaskException):
    def getPage():
        return abort(401)


class notAcceptable(flaskException):
    def getPage():
        return abort(406)
