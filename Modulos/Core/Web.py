#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoSuchWindowException
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException
from selenium.common.exceptions import ElementNotVisibleException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from webdriver_manager.chrome import ChromeDriverManager
from pyscreeze import ImageNotFoundException
import pyautogui
import logging
log = logging.getLogger(__name__)

class Web:
    def __init__(self, url, timeout=10, ruta_descarga='C:\\temp', **kwargs):
        self.url = url
        self.argumentos = kwargs.get('argumentos')
        self.driver = None
        self.handles = None
        self.wait = None
        self.timeout = timeout
        self.ruta_descarga = ruta_descarga

    def conectar(self):
        headless = False
        log.info('conectar a %s' % self.url)
        chrome_options = Options()
        prefs = {
                "download.default_directory": self.ruta_descarga,
                "download.prompt_for_download": False,
                "download.directory_upgrade": True
                }
        if self.argumentos:
            for argumento in self.argumentos.split(' '):
                log.debug('Agregar argumento de opcion: %s' % argumento)
                chrome_options.add_argument(argumento)
                if argumento in ['headless', '--headless']: #Implementacion para descargar en headless
                    headless = True
        #Cargar argumentos por parametro y opciones experimentales
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_experimental_option('prefs', prefs)
        #Crear driver
        try:
            self.driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=chrome_options)
        except WebDriverException:
            log.error('Fallo al iniciar driver')
            raise WebDriverException
        if headless:
            self.driver.command_executor._commands["send_command"] = ("POST", '/session/$sessionId/chromium/send_command')
            params = {'cmd': 'Page.setDownloadBehavior', 'params': {'behavior': 'allow', 'downloadPath': self.ruta_descarga}}
            command_result = self.driver.execute("send_command", params)
            for key in command_result:
                log.debug("command_result:" + key + ":" + str(command_result[key]))
        #Realizar conexion
        self.driver.get(self.url)
        self.handles = self.driver.window_handles
        self.wait = WebDriverWait(self.driver, self.timeout)

    def desconectar(self):
        self.driver.quit()
    
    def __cambiar_frame(self, frame_xpath):
        for frame in frame_xpath.split(' '):
            try:    #Esperar a que el frame este cargado
                self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.XPATH, frame)))
            except NoSuchElementException:
                mensaje = 'No se encontro el frame: %s' % frame
                log.error(mensaje)
                raise Exception(mensaje)
            except TimeoutException:
                mensaje = 'Timeout: %s - Elemento: %s' % (self.timeout, frame)
                log.error(mensaje)
                #raise TimeoutException

    def elemento(self, element_xpath, frame_xpath='', accion='', **kwargs):
        log.debug('elemento(element_xpath=%s, frame_xpath=%s, accion=%s)' % (element_xpath, frame_xpath, accion))
        resultado = None
        #Cambiar de frame
        if frame_xpath:
            self.__cambiar_frame(frame_xpath)
        #Elemento
        if accion == 'click':       #Boton
            try:    #Esperar a que el elemento este cargado
                elemento = self.wait.until(EC.element_to_be_clickable((By.XPATH, element_xpath)))
                elemento.click()
            except NoSuchElementException:
                mensaje = 'No se encontro el elemento en la pagina actual: %s' % element_xpath
                log.warning(mensaje)
                resultado = False
            except ElementClickInterceptedException:
                self.driver.execute_script("arguments[0].click();", elemento)
            resultado = True
        elif accion == 'text':      #Textbox
            try:    #Esperar a que el elemento este cargado
                elemento = self.wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))
                resultado = elemento.text
            except NoSuchElementException:
                mensaje = 'No se encontro el elemento en la pagina actual: %s' % element_xpath
                log.warning(mensaje)
                raise Exception(mensaje)
            except TimeoutException:
                log.warning('Es posible que no haya texto para mostrar: %s' % element_xpath)
                resultado = ''
        elif accion == 'send_keys':
            try:    #Esperar a que el elemento este cargado
                elemento = self.wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))
            except NoSuchElementException:
                mensaje = 'No se encontro el elemento en la pagina actual: %s' % element_xpath
                log.warning(mensaje)
                raise Exception(mensaje)
            elemento.clear()
            elemento.send_keys(Keys.CONTROL, 'a')
            elemento.send_keys(kwargs.get('keys'))
            resultado = True
        elif accion == 'select':    #Combobox
            try:    #Esperar a que el elemento este cargado
                elemento = self.wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))
            except NoSuchElementException:
                mensaje = 'No se encontro el elemento en la pagina actual: %s' % element_xpath
                log.warning(mensaje)
                raise Exception(mensaje)
            select_element = Select(elemento)
            resultado = select_element.options
            try:
                select_element.select_by_visible_text(kwargs.get('opcion'))
            except ElementNotVisibleException:  #Logear todas las opciones posibles en caso de no encontrar la buscada
                log.error('No se encontro la opcion: %s\nOpciones posibles: %s' % (kwargs.get('opcion'), resultado))
        elif accion == 'get_attribute':
            try:    #Esperar a que el elemento este cargado
                elemento = self.wait.until(EC.visibility_of_element_located((By.XPATH, element_xpath)))
            except NoSuchElementException:
                mensaje = 'No se encontro el elemento en la pagina actual: %s' % element_xpath
                log.warning(mensaje)
                raise Exception(mensaje)
            resultado = elemento.get_attribute(kwargs.get('attribute'))
        elif accion == 'check_grid':    #Checkbox en grilla.
            opcion = kwargs.get('opcion')
            posicion_indice = kwargs.get('posicion_indice')
            element_check = kwargs.get('element_check')
            log.info('check_grid: opcion=%s, element_text=%s, element_check=%s, posicion_indice=%s' % (opcion, element_xpath, element_check, posicion_indice))
            self.__check_grid(opcion=opcion, element_text=element_xpath, element_check=element_check, posicion_indice=posicion_indice)
        #Salir
        try:
            self.driver.switch_to.default_content()
        except NoSuchWindowException:
            log.info('No se encontro una ventana para cerrar')
        log.debug('elemento return: %s' % resultado)
        return resultado

    def __check_grid(self, opcion, element_text, element_check, posicion_indice):
        indice_fila = int(element_text[posicion_indice-1:posicion_indice])
        while True: #Recorre hasta que encuentre el texto o se termine el tiempo
            element_text_xpath = element_text[:posicion_indice-1] + str(indice_fila) + element_text[posicion_indice:]
            log.debug('element_text_xpath: %s' % element_text_xpath)
            try:
                elemento = self.driver.find_element_by_xpath(element_text_xpath)
            except NoSuchElementException:
                log.Error('No se encontro el elemento: %s' % element_text_xpath)
            if opcion == elemento.text:
                #Haces click en el checkbox
                element_check_xpath = element_check[:posicion_indice-1] + str(indice_fila) + element_check[posicion_indice:]
                log.debug('element_check_xpath: %s' % element_check_xpath)
                try:
                    elemento = self.driver.find_element_by_xpath(element_check_xpath)
                except NoSuchElementException:
                    log.error('No se encontro el elemento: %s' % element_check_xpath)
                elemento.click()
                break
            else:
                indice_fila += 1
        return indice_fila

    def aceptar_alerta(self):
        try:
            self.wait.until(EC.alert_is_present())
            self.driver.switch_to_alert().accept()
        except NoSuchWindowException:
            log.info('No hay alerta')
            pass
        except TimeoutException:
            log.info('No hay alerta')
            pass
    
    def esperar_alerta(self, alerta, element_xpath, frame_xpath='', visible=True):
        log.info('Esperar señal: %s, en elemento: %s' % (alerta, element_xpath))
        intentos = 3
        alerta_actual = self.elemento(accion='text', frame_xpath=frame_xpath, element_xpath=element_xpath)[:len(alerta)]
        while alerta_actual != alerta and intentos > 0:
            time.sleep(self.timeout/intentos)
            alerta_actual = self.elemento(accion='text', frame_xpath=frame_xpath, element_xpath=element_xpath)[:len(alerta)]
            intentos -= 1
        if alerta_actual != alerta:
            log.warning('Se acabo el tiempo de espera para la señal: %s' % alerta)
            return False
        else:
            log.info('Señal recibida')
            return True
    
    #Buscar XPATH del elemento en los frames
    def __obtener_frames(self, xpath):
        lista = []
        resultado = ''
        #iframe
        for frame in self.driver.find_elements_by_tag_name('frame'):
            child_frame_name = frame.get_attribute('name')
            frame_xpath = '//frame[@name="{}"]'.format(child_frame_name)
            self.driver.switch_to_frame(self.driver.find_element_by_xpath(frame_xpath))
            busqueda = self.driver.find_elements_by_xpath(xpath)
            if len(busqueda) > 0:
                resultado = frame_xpath
                lista.append(resultado)
            else:
                for child_frame in self.driver.find_elements_by_tag_name('iframe'):
                    child_child_frame_name = child_frame.get_attribute('name')
                    child_frame_xpath = '//iframe[@name="{}"]'.format(child_child_frame_name)
                    self.driver.switch_to_frame(self.driver.find_element_by_xpath(child_frame_xpath))
                    busqueda = self.driver.find_elements_by_xpath(xpath)
                    if len(busqueda) > 0:
                        resultado = frame_xpath + '.' + child_frame_xpath
                        lista.append(resultado)
                    self.driver.switch_to.default_content()
            self.driver.switch_to.default_content()     
        return lista
    

#   Interaccion con imagenes en pantalla PyAutoGUI
    def click(self, imagen):
        log.info('click(imagen=%s)' % imagen)
        resultado = False
        pyautogui.PAUSE = 1
        pyautogui.FAILSAFE = True   #Hace que se fuerce la detencion si moves el puntero a la esq sup izq
        pyautogui.moveTo(10,10)
        if type(imagen) == list:
            for item in imagen:
                coordenadas = pyautogui.locateOnScreen(item)
                intentos = 3
                while coordenadas == None and intentos > 0:
                    time.sleep(self.timeout/3)  #Espera 1/3 del timeout
                    try:
                        coordenadas = pyautogui.locateOnScreen(item)
                    except ImageNotFoundException:
                        mensaje = 'No se encontro la imagen: %s' % item
                        log.warning(mensaje)
                    intentos -= 1
                if coordenadas:
                    ubicacion = pyautogui.center(coordenadas)
                    pyautogui.click(ubicacion)
                    resultado = True
                    break
                else: 
                    pass
            else:
                mensaje = 'No se encontraron las imagenes %s' % imagen
                log.error(mensaje)
                raise ImageNotFoundException
        elif type(imagen) == str:
            coordenadas = pyautogui.locateOnScreen(imagen)
            intentos = 3
            while not coordenadas and intentos > 0:
                time.sleep(self.timeout/3)  #Espera 1/3 del timeout
                coordenadas = pyautogui.locateOnScreen(imagen)
                intentos -= 1
            if intentos == 0 and not coordenadas:
                mensaje = 'No se encontro la imagen %s en el tiempo esperado' % imagen
                log.error(mensaje)
                raise ImageNotFoundException
            if coordenadas:
                ubicacion = pyautogui.center(coordenadas)
                pyautogui.click(ubicacion)
                resultado = True
        return resultado
    def send_keys(self, teclas, intervalo=0.2):
        log.info('send_keys(teclas=%s, intervalo=%s' % (teclas, intervalo))
        resultado = True
        pyautogui.typewrite(teclas, interval=intervalo)
        return resultado
    