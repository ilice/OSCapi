from slacker import Slacker
from osc.models import Error
from django.utils import timezone
import datetime

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
