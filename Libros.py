#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys
from config.LibrosConfig import libros
from Modulos.Core.Web import Web

def main(argv):
    pagina = Web(libros["url"])
    pagina.conectar()

    paginasLibros = []

    descargasEnPagina = pagina.driver.find_elements_by_class_name("down")

    numeroPagina = 1

    

    for paginaDescarga in descargasEnPagina:
        paginasLibros.append(paginaDescarga.get_attribute("href"))
    
    pagina.desconectar()

if __name__ == "__main__":
	main(sys.argv[1:])