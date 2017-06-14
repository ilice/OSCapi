# -*- coding: utf-8 -*-

import atexit
from django.utils import timezone
from slacker import Slacker
from time import time

from osc.models import Error


from django.conf import settings

from osc.exceptions import OSCException

__all__ = ['error_managed']


class error_managed(object):
    def __init__(self, default_answer=None, inhibit_exception=False):
        self.default_answer = default_answer
        self.inhibit_exception = inhibit_exception

    def __call__(self, f):
        def wrapper(*args, **kwargs):
            try:
                return f(*args, **kwargs)
            except Exception as e:
                self.handle_exception(e, f)
                return self.default_answer
        return wrapper

    def handle_exception(self, e, f):
        if not hasattr(e, 'osc_handled'):
            actionable_info = e.actionable_info \
                if isinstance(e, OSCException) else None
            service = e.service if isinstance(e, OSCException) else 'UNKNOWN'

            error_handler.error(service,
                                f.__module__,
                                f.__name__,
                                str(type(e)) + ': ' + str(e),
                                actionable_info)

            # State the exception as handled, so that we don't print errors
            # again
            e.osc_handled = True

        if not self.inhibit_exception:
            raise e


class SlackErrorHandler(object):

    slack = None
    url = None
    process_name = None
    module_name = None
    function_name = None
    actionable_info = None
    message = 'Error detected'
    type = 'good'

    def __init__(self, token, flush_bucket, url):
        self.slack = Slacker(token)
        self.url = url
        self.flush_bucket = flush_bucket
        self.num_errors = 0

    def flush(self):
        try:
            if self.num_errors > 0 & self.flush_bucket > 1:
                self.slack.chat.post_message(
                    '#ooops',
                    'Several errors detected',
                    attachments=[{
                        "title": "Please, check the list of errors",
                        "title_link": self.url + '/admin/osc/error/',
                        "text": 'click title to see errors details',
                        "color": "#FF0000"
                    }],
                    as_user=True)
            elif self.num_errors > 0:
                self.slack.chat.post_message(
                    '#ooops',
                    self.message,
                    attachments=[{
                        "author_name": "OSCar bot",
                        "author_link": "https://github.com/ilice/OSCapi",
                        "author_icon": "https://raw.githubusercontent.com/"
                                       "wiki/teanocrata/OpenSmartCountry/"
                                       "resources/cacharrito.png",
                        "title": "OSC API " + self.type,
                        "title_link": self.url + '/admin/osc/error/',
                        "text": "Something went wrong: Ctrl + Z! Ctrl + Z!!",
                        "fields": [
                            {
                                "title": "Process name",
                                "value": self.process_name
                            },
                            {
                                "title": "Module name",
                                "value": self.module_name
                            },
                            {
                                "title": "Function name",
                                "value": self.function_name
                            },
                            {
                                "title": "Message",
                                "value": self.message
                            },
                            {
                                "title": "Actionable info",
                                "value": self.actionable_info
                            }
                        ],
                        "image_url": "https://opensmartcountry.com",
                        "footer": "OSC API",
                        "footer_icon": "https://raw.githubusercontent.com/"
                                       "wiki/teanocrata/OpenSmartCountry/"
                                       "resources/"
                                       "OpenSmartCountry_gif_animado.gif",
                        "ts": time(),
                        "color": self.type
                    }],
                    as_user=True
                )
        except Exception:
            pass

    def error(self,
              process_name,
              module_name,
              function_name,
              message,
              actionable_info=None):
        self.process_name = process_name
        self.module_name = module_name
        self.function_name = function_name
        self.message = message
        self.actionable_info = actionable_info
        self.type = "danger"
        self.num_errors += 1
        self.try_flush()

    def warning(self,
                process_name,
                module_name,
                function_name,
                message,
                actionable_info=None):
        self.process_name = process_name
        self.module_name = module_name
        self.function_name = function_name
        self.message = message
        self.actionable_info = actionable_info
        self.type = "warning"
        self.num_errors += 1
        self.try_flush()

    def info(self,
             process_name,
             module_name,
             function_name,
             message,
             actionable_info=None):
        self.process_name = process_name
        self.module_name = module_name
        self.function_name = function_name
        self.message = message
        self.actionable_info = actionable_info
        self.type = "good"
        self.num_errors += 1
        self.try_flush()

    def try_flush(self):
        if self.num_errors >= self.flush_bucket:
            self.flush()


class DBErrorHandler(object):
    def __init__(self):
        pass

    def error(self,
              process_name,
              module_name,
              function_name,
              message,
              actionable_info=None):
        err = Error(date=timezone.now(),
                    process_name=process_name,
                    module_name=module_name,
                    function_name=function_name,
                    severity=Error.S_ERROR,
                    message=message,
                    actionable_info=actionable_info)
        err.save()

    def warning(self,
                process_name,
                module_name,
                function_name,
                message,
                actionable_info=None):
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
class CompositeErrorHandler(object):

    error_handlers = None

    def __init__(self, error_handlers):
        self.error_handlers = []
        for error_handler in error_handlers:
            if error_handler == 'DBErrorHandler':
                self.error_handlers.append(DBErrorHandler())
            elif error_handler == 'SlackErrorHandler':
                self.error_handlers.append(SlackErrorHandler(
                    settings.SLACK['token'],
                    settings.SLACK['flush_bucket'],
                    settings.WEB['url']))
            else:
                raise Exception('Bad error handler configuration. '
                                'Check app_settings.py.')

    def error(self,
              process_name,
              module_name,
              function_name,
              message,
              actionable_info=None):
        for handler in self.error_handlers:
            handler.error(process_name,
                          module_name,
                          function_name,
                          message,
                          actionable_info)

    def warning(self,
                process_name,
                module_name,
                function_name,
                message,
                actionable_info=None):
        for handler in self.error_handlers:
            handler.warning(process_name,
                            module_name,
                            function_name,
                            message,
                            actionable_info)

    def flush(self):
        for handler in self.error_handlers:
            handler.flush()

error_handler = CompositeErrorHandler(settings.ERROR_HANDLER)


def flush_handlers():
    error_handler.flush()


atexit.register(flush_handlers)
