from slacker import Slacker
import datetime
import os


class ErrorHandler:

    slack = None
    errors_dir = None
    url = None

    error_buffer = {'error': [], 'warning': []}
    flush_bucket = None

    def __init__(self, token, flush_bucket, errors_dir, url):
        self.slack = Slacker(token)
        self.errors_dir = errors_dir
        self.url = url
        self.flush_bucket = flush_bucket

    def flush(self):
        if len(self.error_buffer['error']) == 0 and len(self.error_buffer['warning']) == 0 :
            return

        if not os.path.exists(self.errors_dir):
            os.makedirs(self.errors_dir)

        current_time = datetime.datetime.now()

        error_file_name = 'errors_' + current_time.strftime('%Y%m%d%H%M') + '.txt'

        tmp_file_path = os.path.join(self.errors_dir, error_file_name)

        with open(tmp_file_path, 'w') as f:
            f.write('================================================\n')
            f.write('===============  ERRORS ========================\n')
            f.write('================================================\n')

            for error in self.error_buffer['error']:
                f.write('\n +++++++++++++++++++++++++++++++++++' + '\n')
                f.write('\t DATE: \t' + str(error['date']) + '\n')
                f.write('\t MODULE_NAME: \t' + error['module_name'] + '\n')
                f.write('\t FUNCTION_NAME: \t' + error['function_name'] + '\n')
                f.write('\t MESSAGE: \t' + error['message'] + '\n')
                f.write(' +++++++++++++++++++++++++++++++++++' + '\n')

                f.write('\n\n\n\n')
                f.write('================================================\n')
                f.write('===============  WARNINGS ======================\n')
                f.write('================================================\n')

                for warning in self.error_buffer['warning']:
                    f.write('\n +++++++++++++++++++++++++++++++++++' + '\n')
                    f.write('\t DATE: \t' + str(warning['date']) + '\n')
                    f.write('\t MODULE_NAME: \t' + warning['module_name'] + '\n')
                    f.write('\t FUNCTION_NAME: \t' + warning['function_name'] + '\n')
                    f.write('\t MESSAGE: \t' + warning['message'] + '\n')
                    f.write(' +++++++++++++++++++++++++++++++++++' + '\n')

        self.slack.chat.post_message('#errors', 'Errors detected', attachments=[
            {
                "title": "Download the errors list",
                "title_link": self.url + '/static/' + error_file_name,
                "text": 'click title to download errors file',
                "color": "#FF0000"
            }
        ], as_user=True)

        self.error_buffer['error'] = []
        self.error_buffer['warning'] = []

    def error(self, module_name, function_name, message):
        self.error_buffer['error'].append({'date': datetime.datetime.now(),
                                           'module_name': module_name,
                                           'function_name': function_name,
                                           'message': message})

        self.try_flush()

    def warning(self, module_name, function_name, message):
        self.error_buffer['warning'].append({'date': datetime.datetime.now(),
                                             'module_name': module_name,
                                             'function_name': function_name,
                                             'message': message})

        self.try_flush()

    def try_flush(self):
        if len(self.error_buffer['error']) + len(self.error_buffer['warning']) >= self.flush_bucket:
            self.flush()

if __name__ == '__main__':
    error_handler = ErrorHandler()

    error_handler.error('sigpac', 'Error de Conexion', "La mierda del CPD se ha caido")

    error_handler.warning('sigpac', 'Error de Conexion', "La mierda del CPD se ha caido")
