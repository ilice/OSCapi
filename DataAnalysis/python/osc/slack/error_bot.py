from slacker import Slacker


class ErrorHandler:

    slack = None

    def __init__(self, token):
        self.slack = Slacker(token)
        pass

    def error(self, module_name, function_name, message):
        self.slack.chat.post_message('#errors', 'ERROR: ' + module_name, attachments=[
            {
                "title": "Function: " + function_name,
                "text": message,
                "color": "#FF0000"
            }
        ], as_user=True, )

    def warning(self, module_name, function_name, message):
        self.slack.chat.post_message('#errors', 'Warning: ' + module_name, attachments=[
            {
                "title": "Function: " + function_name,
                "text": message,
                "color": "#FFFF00"
            }
        ], as_user=True, )

if __name__ == '__main__':
    error_handler = ErrorHandler()

    error_handler.error('sigpac', 'Error de Conexion', "La mierda del CPD se ha caido")

    error_handler.warning('sigpac', 'Error de Conexion', "La mierda del CPD se ha caido")
