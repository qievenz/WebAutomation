#!/usr/bin/env python
# -*- coding: utf-8 -*-
import time
import sys
import random
from Modulos.Core.Web import Web
from config.WebConfig1 import web1
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
log = logging.getLogger(__name__)

def main(argv):
    usuario = web1["usuario"]
    password = web1["password"]
    url = web1["url"]
	#pagina = Web(url=urlpage, argumentos='headless')
    pagina = Web(url=url)
    pagina.conectar()
    #Loguear
    pagina.elemento(accion="click", element_xpath="/html/body/div[1]/div[2]/div/div/div/div/button")
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div[2]/div/div[2]/div/div[2]/form/div/div[2]/input")
    pagina.elemento(accion="send_keys",keys=usuario, element_xpath="/html/body/div[5]/div[1]/div/div[2]/div/div[2]/div/div[2]/form/div/div[2]/input")
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div[2]/div/div[2]/div/div[2]/form/div/div[3]/input")
    pagina.elemento(accion="send_keys",keys=password, element_xpath="/html/body/div[5]/div[1]/div/div[2]/div/div[2]/div/div[2]/form/div/div[3]/input")
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div[2]/div/div[2]/div/div[2]/form/div/div[5]/button")
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div[2]/div/div[2]/div/div[3]/form/div/div/button[1]")
    tam_container_inicial = len(pagina.elemento(accion="text", element_xpath="/html/body/div[5]/div[1]/div/div/div/div[1]/ol"))
    #Filtros
    #Filtro por ubicacion
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div/div/div[3]/div/div[1]/span[1]")
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div[1]/div/input")
    #   Destildar personas en linea
    solo_online = pagina.elemento(accion="get_attribute", attribute="data-checked", element_xpath="/html/body/div[5]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div[5]/div")
    if solo_online:
        #pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div/div/div[3]/div/div[2]/div/div/div/div[5]/div/label")
        pass
    #OK
    pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div/div/div[3]/div/div[2]/button")
    #pagina.elemento(accion="click", element_xpath="")
    time.sleep(3)
    last_height = pagina.execute_script(script="return document.body.scrollHeight")
    i = 1
    print(time.strftime("%H:%M:%S"))
    while True:
        print(i)
        try:
            posicion = "Conocer"
            miembro = "/html/body/div[5]/div[1]/div/div/div/div[1]/ol/li[" + str(i) + "]"
            pagina.elemento(accion="click", element_xpath=miembro)
            try:
                posicion = "Perfil"
                pagina.elemento(accion="click", element_xpath="/html/body/div[5]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[5]/div/div[3]/a[3]")
                nombre = pagina.elemento(accion="text", element_xpath="/html/body/div[5]/div[1]/div/div[2]/div[1]/div[1]/div/div/div[5]/div/div[1]/h4")
                #print(nombre)
                time.sleep(random.randrange(3,10))
                posicion = "Atras"
                pagina.elemento(accion="click", element_xpath="/html/body/div[1]/div/div/div[1]")
            except:
                print(posicion)
        except:
            print(posicion)
            i = i - 1
            pagina.execute_script(script="window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(1)
            new_height = pagina.execute_script(script="return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        i = i+1
    
if __name__ == "__main__":
	main(sys.argv[1:])