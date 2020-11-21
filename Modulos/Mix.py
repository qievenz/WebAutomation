#!/usr/bin/env python
# -*- coding: utf-8 -*-
import requests
import time
from os import path, rename, listdir, makedirs
from .Core import Web
from selenium.common.exceptions import TimeoutException
import smtplib
import logging.config
log = logging.getLogger(__name__)
logging.config.fileConfig('logger.ini', disable_existing_loggers=False)

def descargarArchivosConNavegador(url, xpath_download='', xpath_next='', path_folder=''):
    pagina = Web(url, argumentos='headless')
    pagina.conectar()
    src = pagina.elemento(element_xpath=xpath_download,accion='get_attribute',attribute='src')
    src_ant = ''
    
    try:
        while src != src_ant:
            nombre = src[src.rfind('/')+1:]
            
            if (not path.exists(path.join(path_folder, nombre))):
                descargarArchivo(src, path.join(path_folder, nombre))

            if xpath_next == '':
                pagina.elemento(element_xpath=xpath_download,accion='click')
            else:
                pagina.elemento(element_xpath=xpath_next,accion='click')

            time.sleep(3)
            src_ant = src
            src = pagina.elemento(element_xpath=xpath_download,accion='get_attribute',attribute='src')
    except TimeoutException:
        print("Fin o error " + url)
    
    pagina.desconectar()

def descargarArchivo(src, path_dst):
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}
    r = requests.get(src, headers=headers)
    
    if r.status_code == 200:
        with open(path_dst, 'wb') as outfile:
            outfile.write(r.content)
            
    return r.status_code

def cambiarExtensionTodosArchivosEnRuta(ruta_destino='', extensionNueva=''):
    for count, filename in enumerate(listdir(ruta_destino)):
        src = path.join(ruta_destino, filename)
        dst = path.join(ruta_destino, path.splitext(filename)[0] + '.' + extensionNueva.replace('.', ''))
        rename(src, dst)

def enviarEmail(userLogin, passwordLogin, userFrom, userTo, subject, body, smtp, port):
	message = "\r\n".join([
        "From: %s",
        "To: %s",
        "Subject: %s",
        "",
        "%s"
        ]) % (userFrom, userTo, subject, body)

	try:
		server = smtplib.SMTP(smtp, port)
		server.ehlo()
		server.starttls()
		server.login(userLogin, passwordLogin)
		server.sendmail(userFrom, userTo, message)
		server.close()
	except Exception:
		log.error("Failed to send mail", exc_info=True)