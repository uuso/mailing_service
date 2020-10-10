import os
from datetime import datetime
import logging
import smtplib
from pathlib import Path
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders


handler = logging.FileHandler(filename='debug.log')
shandler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
shandler.setLevel(logging.DEBUG)
formatter = logging.Formatter("%(asctime)s\t%(levelname)s\t%(funcName)s\t%(message)s")
handler.setFormatter(formatter)
shandler.setFormatter(formatter)

logger = logging.getLogger("debug-filelog")
logger.addHandler(handler)
logger.addHandler(shandler)
logger.setLevel(logging.DEBUG)



from config import mailcfg



def items_in_folder(folder):
    import glob
    return glob.glob(folder + '/**/*', recursive=True)


def transliterate_cyrillic_paths(paths):
    """Rename cyrillic files.
    Warn: it transliterate all the string in 'paths' variable, not filename only.
    """
    logger.debug("Поступили на транслитерацию пути:")
    symbols = (u"абвгдеёжзийклмнопрстуфхцчшщъыьэюяАБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ",
            u"abvgdeejzijklmnoprstufhzcss_y_euaABVGDEEJZIJKLMNOPRSTUFHZCSS_Y_EUA")
    tr = {ord(a):ord(b) for a, b in zip(*symbols)}
    for f in paths:
        logger.debug(f)
        os.rename(f, f.translate(tr))



def send_email(mailcfg, subject, attachments):
    """ Send email with credentials from mailcfg dict. Returns error or None
    """
    logger.debug(
        'Подготовка письма для %s с количеством вложений: %d.' % (mailcfg['TO'], len(attachments)))
    
    msg = MIMEMultipart()

    msg['From'] = mailcfg['FROM']
    msg['To'] = mailcfg['TO']
    msg['Subject'] = subject

    msg.attach(MIMEText("File uploading started at %s" % datetime.now()))


    # # send pic:
    # with open("email_practice.png", 'rb') as file:
    # 	msg.attach(MIMEImage(file.read()))
    # with smtplib.SMTP_SSL(mailcfg.SERVER, mailcfg.PORT) as smtp:
    # 	smtp.login(mailcfg.USERNAME, mailcfg.PASSWORD)
    # 	smtp.send_message(msg)
    # exit()

    # send attachments:
    for path in attachments:
        part = MIMEBase('application', "octet-stream")
        logger.debug('Начало загрузки файла по пути: %s' % path)
        try:
            with open(path, 'rb') as file:
                part.set_payload(file.read())
            logger.debug('Загружен.')
            encoders.encode_base64(part)
            logger.debug('Закодирован base64.')
        except Exception as ex:
            logger.error(type(ex).__name__ + str(ex))
        part.add_header('Content-Disposition',
                        'attachment; filename="{}"'.format(Path(path).name))
        msg.attach(part)

    logger.debug('Начало соединения с сервером %s.' % mailcfg['SERVER'])
    try:
        with smtplib.SMTP_SSL(mailcfg['SERVER'], mailcfg['PORT']) as smtp:
            smtp.login(mailcfg['USERNAME'], mailcfg['PASSWORD'])
            logger.debug('Авторизуемся как %s.' % mailcfg['USERNAME'])
            smtp.sendmail(mailcfg['FROM'], mailcfg['TO'], msg.as_string())
        logger.debug('Отправлено успешно.')
        return None
    # except SMTPSenderRefused as ex:
    except Exception as ex:
        print(type(ex).__name__ + str(ex))
        logger.error(type(ex).__name__ + str(ex))
        return ex

def clear_folder(folder):
    empty_folders = []

    for f in items_in_folder(folder):
        try:
            os.remove(f)
            logger.debug('Удалён файл %s.' % f)
    
        except IsADirectoryError as ex:
            empty_folders.append(f)            
            print(type(ex).__name__ + str(ex))
            logger.error(type(ex).__name__ + str(ex))
    
    
    for f in empty_folders:
        try:
            os.rmdir(f)
            logger.debug('Удалена папка %s.' % f)
        except Exception as ex:            
            print(type(ex).__name__ + str(ex))
            logger.error(type(ex).__name__ + str(ex))


def mailing_process():
    files = items_in_folder(mailcfg['ATTACHFOLDER'])
    transliterate_cyrillic_paths(files)
    # loads changed names
    files = items_in_folder(mailcfg['ATTACHFOLDER'])

    fail = send_email(mailcfg=mailcfg, subject='Uploading done.', attachments=files)

    if not fail:
        clear_folder(mailcfg['ATTACHFOLDER'])




if __name__ == "__main__":
    import time
    while True:
        time.sleep(int(mailcfg['DELAY']))
        logger.debug('Проверка наличия файлов для отправки...')
        if len(items_in_folder(mailcfg['ATTACHFOLDER'])):
            logger.debug('Найдены файлы в папке рассылки:')
            for a in items_in_folder(mailcfg['ATTACHFOLDER']):
                logger.debug(a)
            if any(['....' in fp for fp in items_in_folder(mailcfg['ATTACHFOLDER'])]):
                logger.debug('Найдены контрольный файл с "...." в названии! Запущен процесс отправки.')
                mailing_process()

    
