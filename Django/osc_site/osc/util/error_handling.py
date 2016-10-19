from slacker import Slacker
from osc.models import Error
from django.utils import timezone
from osc.util.config import config
import atexit

from osc.exceptions import OSCException


class error_managed(object):
    def __init__(self, default_answer=None):
        self.default_answer = default_answer
        self.error_handlers = [DBErrorHandler]

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                self.handle_exception(e, f)
                return self.default_answer
        return wrapper

    def handle_exception(self, e, f):
        actionable_info = e.actionable_info if isinstance(e, OSCException) else None

        error_handler.error(e.service, f.__module__, f.__name__, str(type(e)) + ': ' + e.message, actionable_info)
        raise e


class SlackErrorHandler:

    slack = None
    errors_dir = None
    url = None

    def __init__(self, token, flush_bucket, url):
        self.slack = Slacker(token)
        self.url = url
        self.flush_bucket = flush_bucket
        self.num_errors = 0

    def flush(self):
        self.slack.chat.post_message('#errors', 'Messages detected', attachments=[
            {
                "title": "Download the errors list",
                "title_link": self.url + '/admin/osc/error/',
                "text": 'click title to see errors',
                "color": "#FF0000"
            }
        ], as_user=True)

    def error(self, process_name, module_name, function_name, message, actionable_info=None):
        self.num_errors += 1
        self.try_flush()

    def warning(self, process_name, module_name, function_name, message, actionable_info=None):
        self.num_errors += 1
        self.try_flush()

    def info(self, process_name, module_name, function_name, message, actionable_info=None):
        self.num_errors += 1
        self.try_flush()

    def try_flush(self):
        if self.num_errors >= self.flush_bucket:
            self.flush()


class DBErrorHandler:
    def __init__(self):
        pass

    def error(self, process_name, module_name, function_name, message, actionable_info=None):
        err = Error(date=timezone.now(),
                    process_name=process_name,
                    module_name=module_name,
                    function_name=function_name,
                    severity=Error.S_ERROR,
                    message=message,
                    actionable_info=actionable_info)
        err.save()

    def warning(self, process_name, module_name, function_name, message, actionable_info=None):
        warn = Error(date=timezone.now(),
                     process_name=process_name,
                     module_name=module_name,
                     function_name=function_name,
                     severity=Error.S_ERROR,
                     message=message,
                     actionable_info=actionable_info)
        warn.save()

    def flush(self):
        pass


# Error handler
class CompositeErrorHandler:

    error_handlers = None

    def __init__(self, error_handlers):
        self.error_handlers = error_handlers

    def error(self, process_name, module_name, function_name, message, actionable_info=None):
        for handler in self.error_handlers:
            handler.error(process_name, module_name, function_name, message, actionable_info)

    def warning(self, process_name, module_name, function_name, message, actionable_info=None):
        for handler in self.error_handlers:
            handler.warning(process_name, module_name, function_name, message, actionable_info)

    def flush(self):
        for handler in self.error_handlers:
            handler.flush()

error_handler = CompositeErrorHandler([DBErrorHandler(),
                                       SlackErrorHandler(config.get('slack', 'token'),
                                                         config.getint('slack', 'flush_bucket'),
                                                         config.get('web', 'url'))])


def flush_handlers():
    error_handler.flush()


atexit.register(flush_handlers)
