import os
import logging
# USE python-dotenv if .env exists, else use envvars

logger = logging.getLogger("debug-filelog")

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')

if os.path.exists(dotenv_path):
    from dotenv import load_dotenv
    load_dotenv(dotenv_path)
    logger.warning('Начата загрузка переменных окружения из файла .env')
else:
    logger.warning('Отсутствует файл .env -- Начата загрузка переменных окружения из окружения.')



envs = list(
    map(str.upper, 
    ['from', 'to', 'username', 'password', 'server', 'port', 'ssl', 'attachfolder', 'delay']))


mailcfg = { env:os.getenv(f'MAIL_{env}') for env in envs}

if not all(mailcfg.values()):
    logging.error('Отсутствует часть переменных окружения.')
print(str(mailcfg))