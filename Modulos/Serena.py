#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .Core import Web
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
import logging
log = logging.getLogger(__name__)

class Serena:
    def __init__(self, url='', user='', password='', **kwargs):
        if user and password:
            url = url.replace('<user>', user).replace('<password>', password)
        else:
            mensaje = 'No se ingreso usuario(%s) o password(%s)' % (user, password)
            log.error(mensaje)
            raise Exception(mensaje)
        self.__web = Web(url=url, **kwargs)
        self.__web.conectar()
        log_in_again = '//*[@id="MainTable"]/tbody/tr/td/table/tbody/tr[3]/td/b/a'
        try:
            self.__web.elemento(accion='click', element_xpath=log_in_again)
        except TimeoutException:
            pass
        self.solicitud_operatoria = _Solicitud_operatoria(self.__web)
        self.release_package = _Release_package(self.__web)
    
    def abrir_id(self, id):
        self.__web.elemento(accion='click', element_xpath='//*[@id="search-icon-btn"]')
        self.__web.elemento(accion='click', element_xpath='//*[@id="inGlobalSearchBox"]/div[1]/div/a[1]')
        self.__web.elemento(accion='send_keys', keys=(id), element_xpath='//*[@id="prependedDropdownButton"]')
        self.__web.elemento(accion='click', element_xpath='//*[@id="btnSearchSubmit"]')
        self.__web.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
        self.__web.elemento(accion='click', element_xpath='//*[@id="searchList"]')
        return id

class _Release_package:
    def __init__(self, driver, id=''):
        self.driver = driver
        self.__frame_xpath = '//*[@id="issuedetails-frame"]'
        self.id = id

    def nuevo(self, titulo, descripcion, sigla, aplicacion, lider_tecnico, lider_funcional, fecha, hora='18:00:00'):
        #Nuevo -> Release Package
        self.driver.elemento(accion='click', element_xpath='//*[@id="newRequestNewButton"]')
        self.driver.elemento(accion='click', element_xpath='//*[@id="newRequestMenu"]/div[1]/a[3]')
        self.driver.elemento(accion='select', opcion='All Projects', element_xpath='//*[@id="submit_projects_project_tree_container"]/div/div[3]/select')
        self.driver.elemento(accion='click', element_xpath='//*[@id="node-SBM_PROJECT-project_17"]/ins')
        self.driver.elemento(accion='click', element_xpath='//*[@id="node-SBM_PROJECT-project_18"]')
        #Title
        self.driver.elemento(accion='send_keys', keys=(titulo), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F123"]')    
        #Description
        self.driver.elemento(accion='send_keys', keys=(descripcion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F464"]')    
        #Cantidad de siglas
        #cant_siglas = int(self.driver.elemento(accion='text', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="e10e5515-0bbc-45b4-8353-a4efcd52164f.footer"]/div[1]/a[3]')[4:])    
        #Mostrar todas las sigla
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="e10e5515-0bbc-45b4-8353-a4efcd52164f.footer"]/div[1]/a[3]')
        #Seleccionar sigla
        self.driver.elemento(accion='check_grid', opcion=sigla, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="e10e5515-0bbc-45b4-8353-a4efcd52164f"]/table/tbody/tr[2]/td[2]', element_check='//*[@id="e10e5515-0bbc-45b4-8353-a4efcd52164f"]/table/tbody/tr[2]/td[1]/input', posicion_indice=64)
        #Seleccionar aplicacion
        self.driver.elemento(accion='check_grid', opcion=aplicacion, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="5890af12-553e-43dd-a920-de00e7e024b8"]/table/tbody/tr[2]/td[2]', element_check='//*[@id="5890af12-553e-43dd-a920-de00e7e024b8"]/table/tbody/tr[2]/td[1]/input', posicion_indice=64)
        #Seleccionar lider tecnico
        self.driver.elemento(accion='check_grid', opcion=lider_tecnico, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="2f8e0774-75a0-4281-8958-586ea5d86c19"]/table/tbody/tr[2]/td[2]', element_check='//*[@id="2f8e0774-75a0-4281-8958-586ea5d86c19"]/table/tbody/tr[2]/td[1]/input', posicion_indice=64)
        #Seleccionar lider funcional
        self.driver.elemento(accion='check_grid', opcion=lider_funcional, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="1b327268-0167-4fac-8402-08cf669b3a5f"]/table/tbody/tr[2]/td[2]', element_check='//*[@id="1b327268-0167-4fac-8402-08cf669b3a5f"]/table/tbody/tr[2]/td[1]/input', posicion_indice=64)
        #Fecha de ejecucion
        self.driver.elemento(accion='send_keys', keys=(fecha), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1323"]')    
        #Hora de ejecucion
        self.driver.elemento(accion='send_keys', keys=(hora), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1324"]')    
        #Seleccionar Release type
        self.driver.elemento(accion='select', opcion='DirectoProd', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F481"]')
        #Seleccionar Deployment path
        self.driver.elemento(accion='select', opcion='PROD', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="4af9c250-6008-402f-947c-d416a9e39ab5"]')
        #Submit
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="SubmitButton"]')
        #TODO:Devolver nro de RP 
        self.id = self.driver.elemento(accion='text', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F453"]')
        log.debug('Se genero el RP nro: %s' % self.id)
        return self.id
    #TODO:Add deployment task
    def agregar_tarea(self, tipo_tarea, titulo, baseline='', descripcion='', items='', application_process='', component_version='', action=''):
        if not self.id:
            mensaje = 'El RP debe estar abierto'
            log.error(mensaje)
            raise Exception(mensaje)
        self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
        #Pestaña Deployment tasks
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="a_0-cf205a0b-27f5-4e1e-bf67-ee079f09df48"]')
        #Edit Deployment Tasks
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="EditTaskCollButton"]')
        #Agregar tarea
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-appTaskCollection"]/div[5]/div[6]/span/div[1]/a/span')
        if tipo_tarea.lower() == 'automatica':
            #Validar campos obligatorios para carga automatica
            if not application_process:
                mensaje = 'No se ingreso el campo application_process.'
                log.error(mensaje)
                raise Exception(mensaje)
            elif not component_version:
                mensaje = 'No se ingreso el campo component_version.'
                log.error(mensaje)
                raise Exception(mensaje)
            #Seleccionar tipo de tarea automatica
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-appTaskCollection"]/div[5]/div[6]/span/div[1]/ul/li[1]')
            self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
            #Cargar titulo y descripcion
            self.driver.elemento(accion='send_keys', keys=(titulo), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/table/tbody/tr[1]/td/input')
            self.driver.elemento(accion='send_keys', keys=(descripcion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/table/tbody/tr[2]/td/textarea')
            #Select Application Process
            self.driver.elemento(accion='select', opcion=application_process, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/div[4]/div[3]/div/div/select')
            #Seleccionar Component Version
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/div[4]/div[5]/div/div/div/span[2]/div')
            #Seleccionar por baseline
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/div[4]/div[5]/div/div/div/span[2]/ul/li[4]')
            #Find items
            #'//*[@id="ng-deploymentUnitAddView"]/div[2]/div[2]/div/div[1]/button'
            #Filter
            #'//*[@id="ng-deploymentUnitAddView"]/div[2]/div[3]/div[3]/div[1]/div/input'
            #TODO:Click baseline
        
            #Texto de la tabla
            #'//*[@id="1558124694737-grid-container"]/div[2]/div/div[1]'
            #Checkbox correspondiente a ese texto
            #'//*[@id="1558124694737-grid-container"]/div[2]/div/div[1]/div/div/div/div/div/table/tbody/tr/td[2]/input'
            
            #Add
        elif tipo_tarea.lower() == 'changeman':
            #Seleccionar tipo de tarea Changeman ZMF
            if not action:
                mensaje = 'No se ingreso el campo action.'
                log.error(mensaje)
                raise Exception(mensaje)
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-appTaskCollection"]/div[5]/div[6]/span/div[1]/ul/li[2]')
            self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
            #Cargar titulo y descripcion
            self.driver.elemento(accion='send_keys', keys=(titulo), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/table/tbody/tr[1]/td/input')
            self.driver.elemento(accion='send_keys', keys=(descripcion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/table/tbody/tr[2]/td/textarea')
            #TODO:Select
        elif tipo_tarea.lower() == 'manual':
            #Seleccionar tipo de tarea manual
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-appTaskCollection"]/div[5]/div[6]/span/div[1]/ul/li[3]')
            self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
            #Cargar titulo y descripcion
            self.driver.elemento(accion='send_keys', keys=(titulo), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/table/tbody/tr[1]/td/input')
            self.driver.elemento(accion='send_keys', keys=(descripcion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/table/tbody/tr[2]/td/textarea')
            #Save
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ng-app"]/body/form/div[5]/button[1]')
            self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
        #Close
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="CloseButton"]')
        self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))

    def enviar(self):
        #Verificar si se cargaron las deployment task
        if not self.driver.esperar_alerta(element_xpath='//*[@id="WarningMessage"]', alerta='Debe crear las deployment tasks para poder avanzar.'):
            self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="PrimaryTransitionButton"]')
            self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
    
class _Solicitud_operatoria:
    def __init__(self, driver, id=''):
        self.driver = driver
        self.__frame_xpath = '//*[@id="issuedetails-frame"] //*[@id="frame_view"]'
        self.id = id

    def nuevo(self, sigla, aplicacion, aprobador, tipo_solicitud, plataforma, interno, observacion='', solicitud_realizada='No', circuito_urgente='No'):
        #Nuevo -> Solicitud operatoria 
        self.driver.elemento(accion='click', element_xpath='//*[@id="newRequestNewButton"]')
        self.driver.elemento(accion='click', element_xpath='//*[@id="newRequestMenu"]/div[1]/a[3]')
        self.driver.elemento(accion='select', opcion='All Projects', element_xpath='//*[@id="submit_projects_project_tree_container"]/div/div[3]/select')
        self.driver.elemento(accion='click', element_xpath='//*[@id="node-SBM_PROJECT-project_31-link"]')
        #Completar formulario
        #Mostrar todas las sigla
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="86ef97cf-cdd3-431f-975c-4847f76ac8ae.footer"]/div/span/a[4]')
        #Seleccionar sigla
        self.driver.elemento(accion='check_grid', opcion=sigla, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="86ef97cf-cdd3-431f-975c-4847f76ac8ae_relationalReport"]')
        #Seleccionar aplicacion
        self.driver.elemento(accion='check_grid', opcion=aplicacion, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ab35db47-26cb-4456-8207-cbc9866ee798_relationalReport"]')
        #Seleccionar aprobador
        self.driver.elemento(accion='check_grid', opcion=aprobador, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="720311a5-d5fc-461d-acaf-63722a339c57_relationalReport"]')
        #Tipo de solicitud
        self.driver.elemento(accion='select', opcion=tipo_solicitud, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F970"]')
        #Plataforma
        self.driver.elemento(accion='select', opcion=plataforma, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F971"]')
        #Interno
        self.driver.elemento(accion='send_keys', keys=(interno), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F975"]')    
        #Observacion
        self.driver.elemento(accion='send_keys', keys=(observacion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F977"]')    
        #Solicitud realizada
        self.driver.elemento(accion='select', opcion=solicitud_realizada, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F976"]')
        #Circuito urgente
        self.driver.elemento(accion='select', opcion=circuito_urgente, frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F954"]')
        #Siguiente
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="Button"]')
        #Devolver nro de RP 
        self.id = self.driver.elemento(accion='text', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F952"]')
        log.debug('Se genero la solcitud nro: %s' % self.id)
        
    def agregar_pedido(self, nombre, planificacion='No modificar', funcion='No modificar', prerequisito='No modificar', postrequisito='No modificar', accion_cancela='No modificar', shell_dts='No modificar', path='No modificar', servidor='No modificar', observacion=''):
        if not self.id:
            mensaje = 'La solicitud debe estar abierta'
            log.error(mensaje)
            raise Exception(mensaje)
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath.split(' ')[0], element_xpath='//*[@id="ButtonAgregaPedido"]')
        self.driver.wait.until(EC.invisibility_of_element_located((By.ID, 'ajaxloader')))
        self.driver.elemento(accion='send_keys', keys=(nombre), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1000"]')
        self.driver.elemento(accion='send_keys', keys=(planificacion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1035"]')
        self.driver.elemento(accion='send_keys', keys=(funcion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1001"]')
        self.driver.elemento(accion='send_keys', keys=(prerequisito), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1005"]')
        self.driver.elemento(accion='send_keys', keys=(postrequisito), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1006"]')
        self.driver.elemento(accion='send_keys', keys=(observacion), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1007"]')
        self.driver.elemento(accion='send_keys', keys=(accion_cancela), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1008"]')
        self.driver.elemento(accion='send_keys', keys=(shell_dts), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1013"]')
        self.driver.elemento(accion='send_keys', keys=(path), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1017"]')
        self.driver.elemento(accion='send_keys', keys=(servidor), frame_xpath=self.__frame_xpath, element_xpath='//*[@id="F1018"]')
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ButtonGuardar"]')

    def enviar(self):
        self.driver.elemento(accion='click', frame_xpath=self.__frame_xpath, element_xpath='//*[@id="ButtonEnviar"]')

def main():
    pass
if __name__ == "__main__":
    main()