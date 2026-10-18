import os
import json
import csv
import xml.etree.ElementTree as ET

historias = {}


def comprobar_existencia_exportaciones():
    if os.path.exists("sistema_uci") == False:
        os.mkdir("sistema_uci")
    if os.path.exists("sistema_uci/exportaciones_json") == False:
        os.mkdir("sistema_uci/exportaciones_json")
    if os.path.exists("sistema_uci/exportaciones_csv") == False:
        os.mkdir("sistema_uci/exportaciones_csv")


def mostrar_menu():
    print("\nBIENVENIDX AL SISTEMA UCI")
    print("1. Cargar y procesar informacion de los pacientes")
    print("2. Consultar historias clinicas cargadas")
    print("3. Exportar historias clinicas a JSON")
    print("4. Exportar signos vitales a CSV")
    print("5. Salir\n")

def leer_hl7(nombre_archivo):
    paciente = {}
    with open(nombre_archivo, "r") as archivo:
        for linea in archivo:
            campos = linea.strip().split("|")
            if campos[0] == "PID":
                paciente["identificacion"] = campos[3]
                paciente["nombre"] = campos[5]
                paciente["fecha_nacimiento"] = campos[7]
                paciente["sexo"] = campos[8]
            elif campos[0] == "PV1":
                paciente["ubicacion"] = campos[3]
    return paciente


def leer_signos(nombre_archivo):
    signos = []
    arbol = ET.parse(nombre_archivo)
    raiz = arbol.getroot()
    for elemento in raiz.iter():
        if elemento.tag.split("}")[-1] == "sign":
            signo = {
                "nombre": elemento.attrib["name"],
                "valor": elemento.attrib["value"],
                "unidad": elemento.attrib["unit"]
            }
            signos.append(signo)
    return signos


def leer_diagnostico(nombre_archivo):
    diagnostico = {}
    arbol = ET.parse(nombre_archivo)
    raiz = arbol.getroot()
    for elemento in raiz.iter():
        etiqueta = elemento.tag.split("}")[-1]
        if etiqueta == "id":
            diagnostico["id"] = elemento.attrib["value"]
        elif etiqueta == "patientId":
            diagnostico["paciente"] = elemento.text
        elif etiqueta == "category":
            diagnostico["categoria"] = elemento.text
        elif etiqueta == "conclusion":
            diagnostico["conclusion"] = elemento.text
        elif etiqueta == "physician":
            diagnostico["medico"] = elemento.text
    return diagnostico


def leer_telemetria(nombre_archivo):
    registros = []
    with open(nombre_archivo, "r") as archivo:
        for linea in archivo:
            campos = linea.strip().split("|")
            if len(campos) == 5:
                registro = {
                    "fecha_hora": campos[0],
                    "paciente": campos[1],
                    "sensor": campos[2],
                    "valor": campos[3],
                    "estado": campos[4]
                }
                registros.append(registro)
    return registros


def cargar_pacientes():
    carpeta = "pacientes_p3"
    if os.path.exists(carpeta) == False:
        print("No se encontro la carpeta pacientes_p3.")
        return

    archivos = os.listdir(carpeta)

    historias.clear()

    for numero in range(1, 4):
        archivo_hl7 = ""
        archivo_signos = ""
        archivo_diagnostico = ""
        archivo_telemetria = ""

        for nombre in archivos:
            if nombre == f"paciente{numero}_hl7.txt":
                archivo_hl7 = f"{carpeta}/{nombre}"
            elif nombre == f"signos_vitales_fhir_{numero}.xml":
                archivo_signos = f"{carpeta}/{nombre}"
            elif nombre == f"expediente_diagnostico_fhir_{numero}.xml":
                archivo_diagnostico = f"{carpeta}/{nombre}"
            elif nombre == f"log_telemetria_{numero}.txt":
                archivo_telemetria = f"{carpeta}/{nombre}"

        if archivo_hl7 == "" or archivo_signos == "" or archivo_diagnostico == "" or archivo_telemetria == "":
            print(f"Faltan archivos del paciente {numero}")
        else:
            paciente = leer_hl7(archivo_hl7)
            signos = leer_signos(archivo_signos)
            diagnostico = leer_diagnostico(archivo_diagnostico)
            telemetria = leer_telemetria(archivo_telemetria)

            identificacion = paciente["identificacion"]
            historias[identificacion] = {
                "informacion_personal": paciente,
                "signos_vitales": signos,
                "diagnostico": diagnostico,
                "telemetria": telemetria
            }
            print(f"Paciente cargado: {identificacion}")

    print(f"Total de pacientes cargados: {len(historias)}")


def consultar_historias():
    if len(historias) == 0:
        print("Primero cargue y procese los pacientes...")
        return

    for identificacion in historias:
        historia = historias[identificacion]
        print("\n------------------------------")
        print(f"PACIENTE: {identificacion}")
        print("\nDATOS PERSONALES")
        for campo in historia["informacion_personal"]:
            print(f"{campo}: {historia['informacion_personal'][campo]}")
        print("\nSIGNOS VITALES")
        for signo in historia["signos_vitales"]:
            print(f"{signo['nombre']}: {signo['valor']} {signo['unidad']}")
        print("\nDIAGNOSTICO")
        for campo in historia["diagnostico"]:
            print(f"{campo}: {historia['diagnostico'][campo]}")
        print("\nTELEMETRIA")
        for registro in historia["telemetria"]:
            print(f"{registro['fecha_hora']} | {registro['sensor']} | {registro['valor']} | {registro['estado']}")


def exportar_json():
    if len(historias) == 0:
        print("Primero cargue y procese los pacientes...")
        return

    comprobar_existencia_exportaciones()

    for identificacion in historias:
        nombre_archivo = f"sistema_uci/exportaciones_json/{identificacion}.json"
        with open(nombre_archivo, "w", encoding="utf-8") as archivo:
            json.dump(historias[identificacion], archivo, indent=4, ensure_ascii=False)
        print(f"Archivo creado: {nombre_archivo}")


def exportar_csv():
    if len(historias) == 0:
        print("Primero cargue y procese a los pacientes...")
        return

    comprobar_existencia_exportaciones()
    nombre_archivo = "sistema_uci/exportaciones_csv/signos_vitales.csv"
    with open(nombre_archivo, "w", newline="", encoding="utf-8-sig") as archivo:
        escritor = csv.writer(archivo)
        encabezados = ["Paciente", "Nombre", "Frecuencia Cardiaca (bpm)",
                       "Presion Arterial Sistolica (mmHg)",
                       "Presion Arterial Diastolica (mmHg)", "Saturacion Oxigeno (%)"]
        escritor.writerow(encabezados)

        for identificacion in historias:
            historia = historias[identificacion]
            frecuencia = ""
            sistolica = ""
            diastolica = ""
            saturacion = ""

            for signo in historia["signos_vitales"]:
                if signo["nombre"] == "Frecuencia Cardiaca":
                    frecuencia = signo["valor"]
                elif signo["nombre"] == "Presion Arterial Sistolica":
                    sistolica = signo["valor"]
                elif signo["nombre"] == "Presion Arterial Diastolica":
                    diastolica = signo["valor"]
                elif signo["nombre"] == "Saturacion Oxigeno":
                    saturacion = signo["valor"]

            nombre = historia["informacion_personal"]["nombre"]
            fila = [identificacion, nombre, frecuencia, sistolica, diastolica, saturacion]
            escritor.writerow(fila)
    print(f"Archivo creado: {nombre_archivo}")
