#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from Modulos.Core.Web import Web
from config.ZonaProp import config


def main(argv):
    usuario = config["usuario"]
    password = config["password"]
    url = config["url"]

if __name__ == "__main__":
    main(sys.argv[1:])