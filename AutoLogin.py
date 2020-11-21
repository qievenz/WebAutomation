#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from config.AutoLoginConfig import biblioteca, web
from Modulos.Core.Web import Web
from datetime import datetime
import smtplib
import logging.config
import time
log = logging.getLogger(__name__)
logging.config.fileConfig('.logger.ini', disable_existing_loggers=False)


def abrir_url(url):
    pass

def loginBiblioteca(url, user, password):
    biblioteca = Web.Web(url=url)
    biblioteca.conectar()
    
    if biblioteca.elemento(accion='text', element_xpath='/html/body/div[2]/div[3]/div/div/p[1]'):
        log.info('Se realiza la autenticacion en la web')
        biblioteca.elemento(accion='click', element_xpath='/html/body/div[2]/div[1]/div[2]/div/div/a/span')
        biblioteca.elemento(accion='send_keys', keys=(user), element_xpath='//*[@id="username"]')
        biblioteca.elemento(accion='send_keys', keys=(password), element_xpath='//*[@id="password"]')
        biblioteca.elemento(accion='click', element_xpath='//*[@id="regularsubmit"]')
        time.sleep(5)
        biblioteca.driver.get(url)
    
    fecha_fin = biblioteca.elemento(accion='text', element_xpath='//*[@id="tblPrestamos"]/tbody/tr[2]/td[5]')

    biblioteca.driver.close()

def loginWeb(url, rutaArchivoCredenciales):
    pagina = Web.Web(url=url)
    pagina.conectar()
    #Recorrer archivo de user
    archivo = open(rutaArchivoCredenciales, "r")
    for linea in archivo:
        linea = linea.rstrip()
        user,passwd = linea.split(":")
        pagina.elemento(accion='send_keys', keys=(user), element_xpath='//*[@id="login_username"]')
        pagina.elemento(accion='send_keys', keys=(passwd), element_xpath='//*[@id="login_password"]')
        pagina.click("Imagenes/nosoyunrobot_1.png")
        time.sleep(5)
        pagina.elemento(accion='click', element_xpath='//*[@id="login-form"]/div[1]/div/div[3]/div[1]/button')

def main(argv):
    loginBiblioteca(biblioteca["url"], biblioteca["user"], biblioteca["password"])
    loginWeb(web["url"], web["rutaArchivoCredenciales"])
    pass

if __name__ == "__main__":
    main(sys.argv)