#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from Modulos.Mix import descargarArchivosConNavegador
from Modulos.Mix import cambiarExtensionTodosArchivosEnRuta
from config.MangaConfig import dominios
from config.MangaConfig import mangas
from config.MangaConfig import RUTA_DESCARGA_DEFAULT
from os import path, rename, listdir, makedirs
from selenium.common.exceptions import TimeoutException
import time
from urllib.parse import urlparse

def descargarManga(nombreManga='', url=''):
    ruta_destino = path.join(RUTA_DESCARGA_DEFAULT, nombreManga)

    if not path.exists(ruta_destino):
        makedirs(ruta_destino)

    xPaths = obtenerXpathsConfig(url)

    descargarArchivosConNavegador(url, xPaths[0], xPaths[1], path_folder=ruta_destino)

    cambiarExtensionTodosArchivosEnRuta()

def obtenerXpathsConfig(url=""):
    dominio = '{uri.netloc}'.format(uri=urlparse(url))
    xpath_download = dominios[dominio][0]
    xpath_next = dominios[dominio][1]
    return [xpath_download, xpath_next]

def descargarConUrl(url='', path_folder=''):
    urlSplit = url.rsplit('/', 1)
    nro = int(urlSplit[1])
    status = 200
    while status != 404:
        url = path.join(urlSplit[0], nro)
        status = descargarArchivosConNavegador(url, path_folder)
        nro = nro + 1

def main(argv):
    for manga in mangas:
        try:
            descargarManga(manga, mangas[manga])
        except TimeoutException:
            print("Fin o error " + manga)

if __name__ == "__main__":
	main(sys.argv[1:])