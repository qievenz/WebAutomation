#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from hyper.contrib import HTTP20Adapter
import requests
from os import path
import json
from config.Alumni import URL, AUTH, RUTA

def get_response_stream(url):
    sessions=requests.session()
    sessions.mount(URL["cdn"], HTTP20Adapter())
    return sessions.get(url, stream=True)

def get_response_auth(url, token):
    sessions=requests.session()
    return sessions.get(url, headers = {'x-alumni-token': token})

def obtener_lista_url_ts(url_m3u8):
    lst_url_ts = []
    response = requests.get(url_m3u8)
    lst_ts = [k for k in response.content.decode("utf-8").split("\n") if ".ts" in k]
    url_reemp = obtener_url_m3u8_reemplazable_ts(url_m3u8)

    for ts in lst_ts:
        lst_url_ts.append(url_reemp.replace("{archivo}", ts))
    
    return lst_url_ts

def obtener_url_m3u8_reemplazable_ts(url_m3u8):
    primer = ""
    lst_url = url_m3u8.split("/")[-1]
    
    for letra in lst_url:
        if letra != "?":
            primer += letra
        else:
            break
    
    return url_m3u8.replace(primer, "{archivo}")

def obtener_lst_id_clases(id_calendar, token):
    lst_id_clases = []
    response = get_response_auth(f"{URL['calendar']}={id_calendar}", token)
    json_response = json.loads(response.text)
    
    for item in json_response:
        try:
            lst_id_clases.append(item["recording"]["parts"][0]["id"])
        except ValueError:
            pass
        
    
    return lst_id_clases

def obtener_url_m3u8(id_clase, token):
    response = get_response_auth(f"{URL['recording']}={id_clase}", token)
    json_response = json.loads(response.text)
    return json_response["uri"]

def descargar_ts(url_ts, nombre_archivo):
    try:
        ts_x = get_response_stream(url_ts)
        ruta_archivo = path.join(RUTA["descargas"], str(nombre_archivo) + ".ts")
        
        if ts_x.status_code == 200:
            with open(ruta_archivo,'ab') as f:
                for chunk in ts_x.iter_content(chunk_size=1024):
                    if chunk:
                        f.write(chunk)
        else:
            print(ts_x.status_code)

    except Exception:
        raise

def login():
    payload = {'username': AUTH["username"], 'password': AUTH["password"]}
    url_login = URL["login"]
    response = requests.post(url_login, data=payload)
    
    if response.status_code == 200:
        json_response = json.loads(response.text)
        return json_response["token"]
    else:
        print("Error en login")
        return None

def main(argv):
    url_curso = argv[0]
    id = url_curso.split("/")[-1]
    token = login()
    lst_id_clases = obtener_lst_id_clases(id, token)
    clase = 1
    for id_clase in lst_id_clases:
        url_m3u8 = obtener_url_m3u8(id_clase, token)
        lst_url_ts = obtener_lista_url_ts(url_m3u8)
        for url_ts in lst_url_ts:
            descargar_ts(url_ts, clase)
        clase += 1


if __name__ == '__main__':
    main(sys.argv[1:])
