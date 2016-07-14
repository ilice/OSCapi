import datetime
import os


class ErrorHandler:

    error_file = None

    def __init__(self, error_dir):
        self.error_file = os.path.join(error_dir, 'errors.log')

        if not os.path.exists(error_dir):
            os.makedirs(error_dir)

    def error(self, module_name, function_name, message):
        with open(self.error_file, 'w') as f:
            f.write('\n ++++++++++++++  ERROR  ++++++++++++\n')
            f.write('\t DATE: \t' + str(datetime.datetime.now()) + '\n')
            f.write('\t MODULE_NAME: \t' + module_name + '\n')
            f.write('\t FUNCTION_NAME: \t' + function_name + '\n')
            f.write('\t MESSAGE: \t' + message + '\n')
            f.write(' +++++++++++++++++++++++++++++++++++\n')

    def warning(self, module_name, function_name, message):
        with open(self.error_file, 'w') as f:
            f.write('\n +++++++++++++  WARNING  +++++++++++\n')
            f.write('\t DATE: \t' + str(datetime.datetime.now()) + '\n')
            f.write('\t MODULE_NAME: \t' + module_name + '\n')
            f.write('\t FUNCTION_NAME: \t' + function_name + '\n')
            f.write('\t MESSAGE: \t' + message + '\n')
            f.write(' +++++++++++++++++++++++++++++++++++\n')

    def flush(self):
        pass


if __name__ == '__main__':
    error_handler = ErrorHandler()

    error_handler.error('sigpac', 'Error de Conexion', "La mierda del CPD se ha caido")

    error_handler.warning('sigpac', 'Error de Conexion', "La mierda del CPD se ha caido")
