import os

ROOT_PATH = os.path.realpath(os.path.join(os.path.dirname(__file__)))

ROOT_FILE_CONFIG = os.path.join(ROOT_PATH, 'server_conf.ini')

ROOT_DIR_TEMPLATE = os.path.join(ROOT_PATH, 'templates')
ROOT_DIR_STATIC = os.path.join(ROOT_PATH, 'static')

ROOT_DIR_LECTURA = os.path.join(ROOT_DIR_STATIC, 'lectura')

ROOT_DIR_REPORTE = os.path.join(ROOT_DIR_STATIC, 'reportes/')
