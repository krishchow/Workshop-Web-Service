from flask import abort


class flaskException(Exception):
    '''
    Abstract Exception that implements other subexceptions that require a
    getPage method.
    '''
    def getPage():
        raise NotImplementedError


class notExist(flaskException):
    '''
    Exception if a resouce that does not exist
    '''
    def getPage():
        return abort(404)


class badRequest(flaskException):
    '''
    Exception if the request json has a missing/too many keys
    '''
    def getPage():
        return abort(400)


class noPermissions(flaskException):
    '''
    Exception if the request has incorrect permissions to a resource
    '''
    def getPage():
        return abort(401)


class notAcceptable(flaskException):
    '''
    Exception if a json value has incorrect type
    '''
    def getPage():
        return abort(406)
