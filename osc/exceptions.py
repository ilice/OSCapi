# -*- coding: utf-8 -*-


class OSCException(Exception):
    def __init__(self, service, message, cause=None, actionable_info=None):
        self.service = service
        self.message = message
        self.cause = cause
        self.actionable_info = actionable_info
        self.processed = False

    def __str__(self):
        return 'OSCException: ' + self.message + 'cause = ' + str(self.cause) \
            + ' actionable_info = ' + str(self.actionable_info)


class ConnectionError(OSCException):
    def __init__(self, service, message, cause=None, actionable_info=None):
        super(ConnectionError, self).__init__(service,
                                              message,
                                              cause,
                                              actionable_info)

    def __str__(self):
        return 'ConnectionError (' + self.service + '): ' \
            + self.message + ' cause = ' + str(self.cause) \
            + ' actionable_info = ' + str(self.actionable_info)


class CadastreException(ConnectionError):
    def __init__(self, message, cause=None, actionable_info=None):
        super(CadastreException, self).__init__('CADASTRE',
                                                message,
                                                cause,
                                                actionable_info)

    def __str__(self):
        return 'CadastreException (' + self.service + '): ' \
            + self.message + ' cause = ' + str(self.cause) \
            + ' actionable_info = ' + str(self.actionable_info)


class ElasticException(ConnectionError):
    def __init__(self, service, message, cause=None, actionable_info=None):
        super(ElasticException, self).__init__(service,
                                               message,
                                               cause,
                                               actionable_info)

    def __str__(self):
        return 'ElasticException (' + self.service + '): ' + \
            self.message + ' cause = ' + str(self.cause) \
            + ' actionable_info = ' + str(self.actionable_info)
