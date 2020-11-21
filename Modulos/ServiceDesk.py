#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .Core import Web
from selenium.webdriver.common.keys import Keys
from xml.dom import minidom
import logging
import pickle
import time
from glob import glob
from os import path, remove
log = logging.getLogger(__name__)

class HD:
    def __init__(self, tipo='Incidente', HD_id='', Metodo_resolucion='', Codigo_resolucion='', Estado='',Asignatario='', Bandeja='', Resumen='', Descripcion='', Accion='', Comentario='', Area='', Problem=''):
        self.tipo = tipo
        self.HD_id = HD_id
        self.Estado = Estado
        self.Asignatario = Asignatario
        self.Bandeja = Bandeja
        self.Resumen = Resumen
        self.Descripcion = Descripcion
        self.Accion = Accion
        self.Comentario = Comentario
        self.Metodo_resolucion = Metodo_resolucion
        self.Codigo_resolucion = Codigo_resolucion
        self.Area = Area
        self.Problem = Problem
    
    def guardar(self, archivo):
        with open(archivo, "ab") as f:
            pickle.dump(self, f)
            
    def cargar(self, archivo):
        resultado = []
        with open(archivo, "rb") as f:
            while True:
                try:
                    hd = pickle.load(f)
                    resultado.append(hd)
                except EOFError:
                    break
        return resultado

class Propiedad_dep_remoto:
    def __init__(self, cuenta, dvc, dvs, sucursal, cuit, folio):
        self.cuenta = ((cuenta.replace('-', '')).replace(' ', '')).zfill(12)
        self.dvc = dvc.zfill(1)
        self.dvs = dvs.zfill(1)
        self.sucursal = sucursal.zfill(3)
        self.cuit = cuit.zfill(12)
        self.folio = folio.zfill(7)

class Service_Desk:
    def __init__(self, url='', user='', password='', **kwargs):
        if user and password:
            url = url.replace('<user>', user).replace('<password>', password)
        else:
            mensaje = 'No se ingreso usuario(%s) o password(%s)' % (user, password)
            log.error(mensaje)
            raise Exception(mensaje)
        self.__web = Web(url=url, **kwargs)
        self.__web.conectar()
    
    def exportar(self, tipo, bandeja, estado='Asignado'):
        #Borro descargas previas
        ruta_archivo = '%s/export*.xls' % self.__web.ruta_descarga
        for f in glob(ruta_archivo):
            remove(f)
        self.__web.elemento(accion='click', frame_xpath='//frame[@name="product"] //iframe[@name="tab_400001"] //frame[@name="menubar"]', element_xpath='//*[@id="mSearch"]')
        #Cargar tipo
        if tipo == 'Incidente':
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="product"]', element_xpath='//*[@id="trmSearch_1"]')
        elif tipo == 'Solicitud':
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="product"]', element_xpath='//*[@id="trmSearch_3"]')
        elif tipo == 'Problem':
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="product"]', element_xpath='//*[@id="trmSearch_2"]')
        #Cargar bandeja
        self.__web.elemento(accion='send_keys', keys=(bandeja), frame_xpath='//frame[@name="product"] //iframe[@name="tab_400001"] //frame[@name="role_main"] //frame[@name="cai_main"]', element_xpath='//*[@id="sf_0_3"]')
        #Cargar estado
        self.__web.elemento(accion='send_keys', keys=(estado), frame_xpath='//frame[@name="product"] //iframe[@name="tab_400001"] //frame[@name="role_main"] //frame[@name="cai_main"]', element_xpath='//*[@id="sf_0_4"]')
        #Click buscar 
        self.__web.elemento(accion='click', frame_xpath='//frame[@name="product"] //iframe[@name="tab_400001"] //frame[@name="role_main"] //frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn0"]')
        #Click exportar
        self.__web.elemento(accion='click', frame_xpath='//frame[@name="product"] //iframe[@name="tab_400001"] //frame[@name="role_main"] //frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn4"]')
        #Espero que se descargue
        while True:
            try:
                lista_archivos = glob(ruta_archivo)
                ultimo_archivo = max(lista_archivos, key=path.getctime)
                if path.isfile(ultimo_archivo):
                    log.debug('Archivo encontrado: %s' % ultimo_archivo)
                    break
                else: raise ValueError
            except ValueError:
                log.debug('Archivo no encontrado, se vuelve a intentar')
                time.sleep(1)
        return ultimo_archivo

    def leer_Exportado(self, rutaXLS):
        incidente = HD()
        listaIncidentes = []
        xmldoc = minidom.parse(rutaXLS)
        itemlist = xmldoc.getElementsByTagName('Row')
        fila_nro = 1
        for fila in itemlist:
            if (fila_nro > 1):  #Ignoro la primer fila ya que es la que tiene los titulos
                item = fila.getElementsByTagName('Cell')
                columna_nro = 1
                for celdas in item:
                    for celda in celdas.childNodes:
                        if (celda.localName == 'Data' and celda.childNodes.length != 0):
                            if columna_nro == 1:    #Nro de HD
                                incidente.HD_id = celda.childNodes[0].data
                            elif columna_nro == 2:  #Estado
                                incidente.Estado = celda.childNodes[0].data
                            elif columna_nro == 5:  #Bandeja
                                incidente.Bandeja = celda.childNodes[0].data
                            elif columna_nro == 10: #Resumen
                                incidente.Resumen = celda.childNodes[0].data
                            elif columna_nro == 12: #Asignatario
                                incidente.Asignatario = celda.childNodes[0].data
                            elif columna_nro == 14: #Area
                                incidente.Area = celda.childNodes[0].data
                    columna_nro = columna_nro + 1
                print(incidente.HD_id + ',' + incidente.Estado + ',' + incidente.Bandeja + ',' + incidente.Resumen)
                listaIncidentes.append(incidente)
                incidente = HD()
            fila_nro = fila_nro + 1
        listaIncidentes.sort(key=lambda x: x.HD_id)
        return listaIncidentes

    def consultar_hd(self, hd=HD()):
        """Devuelve la info del objeto HD.
        """
        resultado = hd
        child_handle = self.__abrir_hd(hd)
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Completar datos del objeto HD
            resultado.Estado = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_0_3_status"]')
            resultado.Bandeja = self.__web.elemento(accion='text', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_2_2"]')
            resultado.Asignatario = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_2_3"]')
            resultado.Resumen = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_7_0"]')
            resultado.Descripcion = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_8_0"]')
            resultado.Area = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_0_2"]')
            #Cerrar ventana
            self.__web.driver.close() 
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
        else:
            print('No se encontró: %s' % resultado.HD_id)
            resultado = -1
        return resultado
    
    def obtener_cuenta_dep_remoto(self, hd=HD()):
        child_handle = self.__abrir_hd(hd)
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Informacion adicional
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="accrdnHyprlnk1"]')
            #Propiedades
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="tabHyprlnk1_1"]')
            #Obtener campos
            cuenta = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_10_0"]')
            cuit = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_10_4"]')
            dvc = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_10_1"]')
            dvs = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_10_2"]')
            folio = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_10_5"]')
            sucursal = self.__web.elemento(accion='text',  frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_10_3"]')
            #Cerrar ventana
            self.__web.driver.close() 
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
            #Validar cuenta
            prop_dep_remoto = Propiedad_dep_remoto(cuenta=cuenta, cuit=cuit, dvc=dvc, dvs=dvs, folio=folio, sucursal=sucursal)
            try:
                int(prop_dep_remoto.cuenta)
                cuenta = prop_dep_remoto.cuenta
            except ValueError:
                cuenta = prop_dep_remoto.folio.zfill(7) + prop_dep_remoto.dvc + prop_dep_remoto.sucursal + prop_dep_remoto.dvs
            #Devolver cuenta
            return cuenta

    def registrar_actividad(self, actividad, hd=HD(), **kwargs):
        """Actualiza el HD en Service Desk. Los campos que no se informan como argumentos se dejan como estan en el objeto hd
        Cerrar por resuelto:
            registrar_actividad(hd_id='HD9999999', actividad='Cerrar', comentario='', asignatario='', metodo='', codigo'')
        Transferir a otra bandeja:
            registrar_actividad(hd_id='HD9999999', actividad='Transferir', bandeja='', comentario='')
        Registrar comentario:
            registrar_actividad(hd_id='HD9999999', actividad='Registrar comentario', comentario='')
        Cambiar estado: Si el asignatario no esta informado se borra el actual
            registrar_actividad(hd_id='HD9999999', actividad='Cambiar estado', asignatario='', comentario='')
        """
        resultado = hd
        child_handle = self.__abrir_hd(hd)
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Registrar accion en el hd
            if actividad == 'Cerrar':
                #Validar campos obligatorios
                self.__validar_completo(hd.Comentario, hd.Asignatario, hd.Metodo_resolucion, hd.Codigo_resolucion)
                hd.Estado = 'Resuelto'
                self.__editar(hd)
            elif actividad == 'Transferir':
                #Validar campos obligatorios
                self.__validar_completo(hd.Comentario, hd.Bandeja)
                self.__transferir(hd)
                pass
            elif actividad == 'Registrar comentario':
                #Validar campos obligatorios
                self.__validar_completo(hd.Comentario)
                self.__registrar_comentario(comentario=hd.Comentario, interno=kwargs.get('interno'))
            elif actividad == 'Editar':
                #Validar campos obligatorios
                #self.__validar_completo(hd.Estado)
                #comentario = '' if hd.Comentario == None else hd.Comentario
                #Si el asignatario no esta informdo o se informa vacio, se borra el actual
                #asignatario = '' if not hd.Asignatario else hd.Asignatario
                self.__editar(hd=hd)
            #Cerrar ventana del HD
            self.__web.driver.close() 
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
            resultado = 1
        else:
            log.error('No se encontró: %s' % hd.hd_id)
        return resultado
    
    def __abrir_hd(self, hd=HD()):
        #Guardar ventana prncipal
        child_handle = self.__web.driver.current_window_handle
        #Seleccionar el tipo
        self.__web.elemento(accion='select', opcion=hd.tipo, frame_xpath='//frame[@name="gobtn"]', element_xpath='//*[@id="ticket_type"]')#Tipo de HD
        #Abrir ventana del HD
        self.__web.elemento(accion='send_keys', frame_xpath='//frame[@name="gobtn"]', element_xpath='//*[@id="gobtnDiv"]/form/table/tbody/tr/td[3]/input', keys=(hd.HD_id, Keys.ENTER))
        time.sleep(3)
        return child_handle
    
    def __validar_completo(self, *args):
        for arg in args:
            if not arg:
                mensaje = 'El campo debe estar completo'
                raise Exception(mensaje)
    
    def __transferir(self, hd):
        #Borrar asignado y setear estado asigndo
        hd.Estado = 'Asignado'
        hd.Asignatario = ''
        self.__editar(hd)
        #TODO:Abrir ventana actividades -> transferir
        pass

    def __registrar_comentario(self, comentario, interno=True):
        #Guardar ventana prncipal
        child_handle = self.__web.driver.current_window_handle
        #Abrir ventana actividades -> registrar comentario
        self.__web.elemento(accion='click', frame_xpath='//frame[@name="menubar"]', element_xpath='//*[@id="mActivities"]')
        self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="amActivities_4"]')
        if len(self.__web.driver.window_handles) > len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Insertar comentario
            self.__web.elemento(accion='send_keys', keys=(comentario), frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_3_0"]')
            #Verificar marca de interno
            interno_actual = self.__web.elemento(accion='get_attribute', attribute='checked', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_1_2"]')
            interno_actual = True if interno_actual == 'true' else False
            if interno != interno_actual:
                #Modificar marca
                self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_1_2"]')
            #Guardar cierra la ventana
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn0"]')
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles
    
    def __editar(self, hd):
        log.info('Editar %s' % hd.HD_id)
        #Guardar ventana prncipal
        child_handle = self.__web.driver.current_window_handle 
        #Abrir ventana editar
        self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn0"]')
        if len(self.__web.driver.window_handles) == len(self.__web.handles):
            self.__web.handles = self.__web.driver.window_handles
            self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
            #Realizar cambios
            self.__web.elemento(accion='send_keys', keys=(hd.Asignatario), frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_2_3"]')#Asignatario
            #Relacionar al problem
            if not self.__web.elemento(accion='text', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_4_0"]'):
                self.__web.elemento(accion='send_keys', keys=(hd.Problem), frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_4_0"]')
                time.sleep(3)
                self.__web.elemento(accion='send_keys', keys=(hd.Problem, Keys.ARROW_DOWN, Keys.RETURN), frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_4_0"]')
            if hd.tipo == 'Incidente':
                self.__web.elemento(accion='select', opcion=hd.Estado, frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_0_3"]')#Estado
                self.__web.elemento(accion='select', opcion=hd.Metodo_resolucion, frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_4_2"]')#Metodo de resolucion
                self.__web.elemento(accion='select', opcion=hd.Codigo_resolucion, frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_5_2"]')#Codigo de resolucion
                if hd.Comentario and hd.Estado != 'Resuelto':
                    self.__registrar_comentario(comentario=hd.Comentario)
            elif hd.tipo == 'Solicitud':
                self.__web.elemento(accion='send_keys', keys=(hd.Estado), frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_0_3"]')#Estado
                self.__web.elemento(accion='select', opcion=hd.Metodo_resolucion, frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_3_2"]')#Metodo de resolucion
                self.__web.elemento(accion='select', opcion=hd.Codigo_resolucion, frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_4_2"]')#Codigo de resolucion
            #Guardar cierra la ventana 
            self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn0"]')
            #Validar si se cierra con resuelto
            if hd.Estado == 'Resuelto':
                intentos = 3
                #Esperar ventana de comentario
                while intentos > 0 and len(self.__web.driver.window_handles) == len(self.__web.handles):
                    time.sleep(self.__web.timeout/intentos)
                    intentos -= 1
                #Si fue resuelto abre la ventana para registrar el comentario de resolucion
                if len(self.__web.driver.window_handles) > len(self.__web.handles):
                    child_child_handle = self.__web.driver.current_window_handle
                    self.__web.handles = self.__web.driver.window_handles
                    self.__web.driver.switch_to_window(self.__web.handles[len(self.__web.handles)-1])
                    #TODO:Esperar señal
                    self.__esperar_alerta('Para cambiar el estado a Resuelto debe introducir un comentario')
                    #Insertar comentario
                    self.__web.elemento(accion='send_keys', keys=(hd.Comentario) , frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="df_4_0"]') 
                    #Guardar comentario
                    self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn0"]')
                    #Check alerta chrome
                    self.__web.aceptar_alerta()
                    self.__web.driver.switch_to_window(child_child_handle)
                    self.__esperar_alerta('Este registro tiene')
                    #Guardar
                    self.__web.elemento(accion='click', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="imgBtn0"]')
                    self.__esperar_alerta('Se ha guardado correctamente')
                else:
                    mensaje = 'Se supero el tiempo de espera para la ventana del comentario'
                    log.error(mensaje)
                    raise Exception(mensaje)
            self.__web.driver.switch_to_window(child_handle)
            self.__web.handles = self.__web.driver.window_handles

    def __esperar_alerta(self, alerta):
        log.info('Esperar señal: %s' % alerta)
        intentos = 3
        alerta_actual = self.__web.elemento(accion='text', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="alertmsgText"]')[:len(alerta)]
        while alerta_actual != alerta and intentos > 0:
            time.sleep(self.__web.timeout/intentos)
            alerta_actual = self.__web.elemento(accion='text', frame_xpath='//frame[@name="cai_main"]', element_xpath='//*[@id="alertmsgText"]')[:len(alerta)]
            intentos -= 1
        if alerta_actual != alerta:
            log.error('Se acabo el tiempo de espera para la señal: %s' % alerta)
            return False
        else:
            log.info('Señal recibida')
            return True

def main():
    pass
if __name__ == "__main__":
    main()