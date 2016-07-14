from slacker import Slacker
import datetime
import os


class ErrorHandler:

    slack = None
    tmp_dir = None

    error_buffer = {'error': [], 'warning': []}
    flush_bucket = None

    def __init__(self, token, flush_bucket, tmp_dir):
        self.slack = Slacker(token)
        self.tmp_dir = tmp_dir
        self.flush_bucket = flush_bucket

    def flush(self):
        if len(self.error_buffer['error']) == 0 and len(self.error_buffer['warning']) == 0 :
            return

        if not os.path.exists(self.tmp_dir):
            os.makedirs(self.tmp_dir)

        current_time = datetime.datetime.now().time()

        tmp_file_path = os.path.join(self.tmp_dir, 'errors_' + current_time.strftime('%Y%m%d%H%M') + '.txt')

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

        self.slack.chat.post_message('#errors', 'Flushing handlers', attachments=[
            {
                "title": "ERRORS",
                "text": len(self.error_buffer['error']),
                "color": "#FF0000"
            },
            {
                "title": "WARNINGS",
                "text": len(self.error_buffer['warning']),
                "color": "#FFFF00"
            }
        ], as_user=True)

        self.slack.files.upload(tmp_file_path, title='Error List', channels=['#errors'])

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
