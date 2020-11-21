#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from Modulos.Core.Web import Web
from Modulos.Mix import enviarEmail
from config.RenovarPrestamoBiblioteca import biblioteca, email
from datetime import datetime
import smtplib
import logging.config
import time
log = logging.getLogger(__name__)
logging.config.fileConfig('logger.ini', disable_existing_loggers=False)

def diferencia_dias(AAAAMMDD_1, AAAAMMDD_2):
    resultado = 0
    AAAAMMDD_1 = datetime.strptime(AAAAMMDD_1, "%Y%m%d")
    AAAAMMDD_2 = datetime.strptime(AAAAMMDD_2, "%Y%m%d")
    if AAAAMMDD_2 > AAAAMMDD_1:
        resultado = abs((AAAAMMDD_2 - AAAAMMDD_1).days)
    else:
        resultado = abs((AAAAMMDD_1 - AAAAMMDD_2).days)
    log.debug('AAAAMMDD_1: %s, AAAAMMDD_2: %s, diferencia_dias: %s' % (AAAAMMDD_1, AAAAMMDD_2,resultado))
    return resultado

def dias_hasta_renovacion(fecha_fin):
    fecha_fin = fecha_fin[6:] + fecha_fin[3:5] + fecha_fin[:2] #AAAAMMDD
    hoy = datetime.now().strftime('%Y') + datetime.now().strftime('%m') + datetime.now().strftime('%d')
    return diferencia_dias(hoy, fecha_fin)

def renovar_prestamo(url, user, password):
    biblioteca = Web.Web(url=url)
    biblioteca.conectar()
    
    if biblioteca.elemento(accion='text', element_xpath='/html/body/div[2]/div[3]/div/div/p[1]'):# == u'¡Bienvenido al Sistema OPAC de Biblioteca de la UTN-FRBA!':
        log.info('Se realiza la autenticacion en la web')
        biblioteca.elemento(accion='click', element_xpath='/html/body/div[2]/div[1]/div[2]/div/div/a/span')
        biblioteca.elemento(accion='send_keys', keys=(user), element_xpath='//*[@id="username"]')
        biblioteca.elemento(accion='send_keys', keys=(password), element_xpath='//*[@id="password"]')
        biblioteca.elemento(accion='click', element_xpath='//*[@id="regularsubmit"]')
        time.sleep(5)
        biblioteca.driver.get(url)
    
    fecha_fin = biblioteca.elemento(accion='text', element_xpath='//*[@id="tblPrestamos"]/tbody/tr[2]/td[5]')
    dias_renovacion = dias_hasta_renovacion(fecha_fin)
    
    if dias_renovacion < 3:
        biblioteca.elemento(accion='click', element_xpath='//*[@id="tblPrestamos"]/tbody/tr[2]/td[7]')
        if biblioteca.elemento(accion='text', element_xpath='//*[@id="modalRenovarPrestamo"]/div[1]/h1') == 'Renovar Préstamo':
            biblioteca.elemento(accion='click', element_xpath='//*[@id="btnRenovarPrestamo"]')
            fecha_fin = biblioteca.elemento(accion='text', element_xpath='//*[@id="tblPrestamos"]/tbody/tr[2]/td[5]')
            dias_renovacion = dias_hasta_renovacion(fecha_fin)
            log.info('Se renueva el prestamo. Fecha de fin: %s' % fecha_fin)
        else:
            log.info('La renovacion no esta habilitada. Fecha de fin: %s' % fecha_fin)
    log.info('Dias hasta renovacion: %s' % dias_renovacion)

    if dias_renovacion == 0:
        #Enviar mail para realizarlo manualmente
        enviarEmail(email["userLogin"], email["passwordLogin"], "tu pc", email["userTo"], "La renovacion automatica no se realizó", ("Realizarlo manualmente: %s" % url), email["smtp"], email["port"])

    biblioteca.driver.close()
    return dias_renovacion

def main(argv):
    try:
        user = argv[1]
        password = argv[2]
    except:
        user = biblioteca["user"]
        password = biblioteca["password"]
    renovar_prestamo(biblioteca["url"], user, password)

if __name__ == "__main__":
    main(sys.argv)