#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .Core import Web
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
import time
from os import path
import logging
log = logging.getLogger(__name__)

#Pasarle las imagenes que va a buscar en un objeto
class Imagen:
    __ruta = './Imagenes/'
    next = [__ruta + 'Next_1.png', __ruta + 'Next_2.png']
    chrome_dimension = __ruta + 'Abrir_Dimensions_1.png'
    item_relate_request = __ruta + 'Relate_to_request.png'
    item_deliver = [__ruta + 'Deliver_1.png', __ruta + 'Deliver_2.png']
    #TODO:Siguiente
    siguiente = __ruta + ''
    close = [__ruta + 'Close_1.png', __ruta + 'Close_1.png']
    deliver_ok = __ruta + 'Deliver_ok.png'

class Dimension:
    def __init__(self, url='', user='', password='', **kwargs):
        if user and password:
            url = url.replace('<user>', user).replace('<password>', password)
        else:
            mensaje = 'No se ingreso usuario(%s) o password(%s)' % (user, password)
            log.error(mensaje)
            raise Exception(mensaje)
        self.__web = Web(url=url, **kwargs)
        self.__web.conectar()
        #Log in
        #TODO:Verificar si estoy logueado
        if self.__web.elemento(accion='text', element_xpath='//*[@id="form"]/tbody/tr[1]/th') == 'Your user name and password have been validated with SSO':
            self.__web.elemento(accion='select', opcion='PRODUCCION', element_xpath='//*[@id="definitionMenu"]')
            self.__web.elemento(accion='click', element_xpath='//*[@id="loginButton"]')
        else:
            try:
                self.__web.elemento(accion='click', frame_xpath='//*[@id="toolbars"]', element_xpath='//*[@id="td_Log_out"]/a/span')
            except TimeoutException:
                pass
            except NoSuchElementException:
                pass            
        
    def setear_stream(self, stream):
        #Change
        self.__web.elemento(accion='click', frame_xpath='//*[@id="statusquo"]', element_xpath='//*[@id="projectChangeButton"]/a')
        self.__esperar_ventana()
        #Cambiar handle
        child_handle = self.__web.driver.current_window_handle
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Set current
            self.__web.elemento(accion='click', element_xpath='/html/body/form/table/tbody/tr[2]/td[2]/input[2]')
            #Select
            self.__web.elemento(accion='select', opcion=stream, element_xpath='/html/body/form/table/tbody/tr[3]/td[2]/select[2]')
            #Ok
            self.__web.elemento(accion='click', element_xpath='//*[@id="td_OK"]/a/span')
            self.__esperar_ventana()
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
        else:
            mensaje = 'No se encontro el boton'
            log.error(mensaje)
            raise Exception(mensaje)

    def setear_work_area(self, work_area):
        #Work Area
        self.__web.elemento(accion='click', frame_xpath='//*[@id="statusquo"]', element_xpath='//*[@id="workAreaChangeButton"]/a')
        self.__esperar_ventana()
        #Cambiar handle
        child_handle = self.__web.driver.current_window_handle
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Set work_area
            self.__web.elemento(accion='send_keys', keys=(work_area), element_xpath='/html/body/form[1]/table/tbody/tr[2]/td[2]/input')
            #Ok
            self.__web.elemento(accion='click', element_xpath='//*[@id="td_OK"]/a/span')
            self.__esperar_ventana()
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
        else:
            mensaje = 'No se encontro el boton'
            log.error(mensaje)
            raise Exception(mensaje)
    
    def setear_product(self, product):
        self.__web.elemento(accion='click', frame_xpath='//*[@id="statusquo"]', element_xpath='//*[@id="productChangeButton"]/a')
        self.__esperar_ventana()
        #Cambiar handle
        child_handle = self.__web.driver.current_window_handle
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Product name
            self.__web.elemento(accion='select', opcion=product, element_xpath='/html/body/form/table/tbody/tr[2]/td[2]/select')
            #Ok
            self.__web.elemento(accion='click', element_xpath='//*[@id="td_OK"]/a/span')
            self.__esperar_ventana()
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
        else:
            mensaje = 'No se encontro el boton'
            log.error(mensaje)
            raise Exception(mensaje)

    def crear_request(self, titulo, descripcion=''):
        resultado = ''
        #Guardar ventana actual
        child_handle =  self.__web.driver.current_window_handle
        #Click en pestaña request -> Nuevo -> Actividad
        self.__web.elemento(accion='click', frame_xpath='//*[@id="tabs"]', element_xpath='//*[@id="issue_tabs"]/a')
        #Esperar que se haya cargado la pestaña
        time.sleep(2)
        self.__web.elemento(accion='click', frame_xpath='//*[@id="toolbars"]', element_xpath='//*[@id="new_changedocToolButton"]')
        self.__web.elemento(accion='click', element_xpath='//*[@id="popupitem_0"]')
        self.__esperar_ventana()
        #Cambiar a la ventana de actividad
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Cargar titulo
            self.__web.elemento(accion='send_keys', keys=(titulo), frame_xpath='//*[@id="main"]', element_xpath='/html/body/form/table/tbody/tr[1]/td[2]/input')
            #Cargar descripcion
            self.__web.elemento(accion='send_keys', keys=(descripcion), frame_xpath='//*[@id="main"]', element_xpath='/html/body/form/table/tbody/tr[2]/td[2]/textarea')
            #Submit
            self.__web.elemento(accion='click', frame_xpath='//*[@id="titles"]', element_xpath='/html/body/form[1]/table/tbody/tr/td[2]/table/tbody/tr[3]/td/table/tbody/tr/td[2]/a/span')
            #Obtener actividad
            self.__web.elemento(accion='click', frame_xpath='//*[@id="main"]', element_xpath='//*[@id="showDetails"]')
            actividad = self.__web.elemento(accion='text', frame_xpath='//*[@id="main"]', element_xpath='//*[@id="detailsContent"]/table/tbody/tr/td[2]')
            resultado = actividad.split(' ')[3]
            self.__web.driver.close() 
            self.__esperar_ventana()
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
        return resultado

    def subir_item(self, actividad):
        log.debug('subir_item: %s', actividad)
        resultado = False
        #Guardar ventana actual
        child_handle =  self.__web.driver.current_window_handle
        #Click en pestaña item -> Deliver
        self.__web.elemento(accion='click', frame_xpath='//*[@id="tabs"]', element_xpath='//*[@id="version_tabs"]/a')
        self.__web.elemento(accion='click', frame_xpath='//*[@id="toolbars"]', element_xpath='//*[@id="deliverToolButton"]')
        #Aceptar abrir dimensions)
        self.__web.click(Imagen.chrome_dimension)
        #Dejar todo como esta y dar next
        self.__web.click(Imagen.next)
        #Relate to request
        self.__web.click(Imagen.item_relate_request)
        self.__web.send_keys(actividad)
        self.__web.click(Imagen.next)
        #Deliver
        self.__web.click(Imagen.item_deliver)
        #TODO:Validar deliver
        #TODO:Siguiente
        self.__web.click(Imagen.siguiente)
        #Cerrar
        if self.__web.click(Imagen.deliver_ok):
            self.__web.click(Imagen.close)
            resultado = True
        return resultado 
        
    def crear_baseline(self):
        #Click en pestaña baseline -> New -> Baseline
        self.__web.elemento(accion='click', frame_xpath='//*[@id="tabs"]', element_xpath='//*[@id="baseline_tabs"]/a')
        pass
    
    #Esperar que se abra la ventana          
    def __esperar_ventana(self):
        intentos = 3
        while len(self.__web.driver.window_handles) == len(self.__web.handles) and intentos > 0:
            time.sleep(self.__web.timeout/intentos)
            intentos += 1

def main():
    pass
if __name__ == "__main__":
    main()