class OSCException(Exception):
    def __init__(self, service, message, cause=None, actionable_info=None):
        self.message = message
        self.cause = cause
        self.actionable_info = actionable_info

    def __str__(self):
        return 'OSCException: ' + self.message


class ConnectionError(OSCException):
    def __init__(self, service, message, cause=None, actionable_info=None):
        super(ConnectionError, self).__init__(message, cause, actionable_info)
        self.service = service

    def __str__(self):
        return 'ConnectionError (' + self.service + '): ' + self.message


class CadastreException(ConnectionError):
    def __init__(self, message, cause=None, actionable_info=None):
        super(CadastreException, self).__init__('CADASTRE', message, cause, actionable_info)
        self.message = message

    def __str__(self):
        return 'CadastreException (' + self.service + '): ' + self.message


class ElasticException(ConnectionError):
    def __init__(self, message, cause=None, actionable_info=None):
        super(ElasticException, self).__init__('ELASTIC', message, cause, actionable_info)
        self.message = message

    def __str__(self):
        return 'ElasticException (' + self.service + '): ' + self.message
