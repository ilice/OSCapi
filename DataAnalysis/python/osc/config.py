from slack.error_bot import ErrorHandler
import logging

# Error handler
error_handler = ErrorHandler()

# Logging configuration
FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
logging.basicConfig(format=FORMAT)
