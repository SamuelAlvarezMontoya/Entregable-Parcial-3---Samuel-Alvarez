from funciones import *

comprobar_existencia_exportaciones()

while True:
    mostrar_menu()
    opcion = input("Ingrese la opcion: ")

    if opcion == "1":
        cargar_pacientes()
    elif opcion == "2":
        consultar_historias()
    elif opcion == "3":
        exportar_json()
    elif opcion == "4":
        exportar_csv()
    elif opcion == "5":
        print("Saliendo del sistema...")
        break
    else:
        print("Opcion no valida.")
