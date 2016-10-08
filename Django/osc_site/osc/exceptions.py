class ConnectionError(Exception):
    def __init__(self, service, message):
        self.service = service
        self.message = message

    def __str__(self):
        return 'ConnectionError (' + self.service + '): ' + self.message
