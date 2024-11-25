import socket
import json
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class Client:
    def __init__(self, host='localhost', port=33056):
        self.host = host
        self.port = port
        self.socket = None

    def connect(self):
        try:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((self.host, self.port))
            logging.info("Conectado al servidor exitosamente")
        except Exception as e:
            logging.error(f"Error conectando al servidor: {e}")
            raise

    def send_request(self, operation, data):
        if not self.socket:
            self.connect()

        request = {
            'operation': operation,
            'data': data
        }

        try:
            self.socket.send(json.dumps(request).encode('utf-8'))
            response = self.socket.recv(4096).decode('utf-8')
            return json.loads(response)
        except Exception as e:
            logging.error(f"Error en la comunicación: {e}")
            return {'status': 'error', 'message': str(e)}

    def insert_employee(self):
        print("\n=== Insertar Nuevo Empleado ===")
        data = {
            'primer_nombre': input("Primer nombre: "),
            'segundo_nombre': input("Segundo nombre (opcional): ") or None,
            'primer_apellido': input("Primer apellido: "),
            'segundo_apellido': input("Segundo apellido (opcional): ") or None,
            'email': input("Email: "),
            'celular': input("Celular: "),
            'fecha_contratacion': input("Fecha de contratación (YYYY-MM-DD): "),
            'departamento_id': int(input("ID del departamento: ")),
            'cargo_id': int(input("ID del cargo: ")),
            'salario': {
                'salario_base': int(input("Salario base: ")),
                'bonificaciones': int(input("Bonificaciones: ")),
                'deducciones': int(input("Deducciones: "))
            }
        }

        response = self.send_request('INSERT', data)
        print(data)
        print("\nRespuesta:", response)

    def update_employee(self):
        print("\n=== Actualizar Empleado ===")
        employee_id = int(input("ID del empleado a actualizar: "))
        print("\nIngrese los campos a actualizar (deje en blanco para no modificar):")

        data = {'id': employee_id}

        email = input("Nuevo email (opcional): ")
        if email:
            data['email'] = email

        celular = input("Nuevo celular (opcional): ")
        if celular:
            data['celular'] = celular

        update_salary = input("¿Actualizar salario? (s/n): ").lower() == 's'
        if update_salary:
            data['salario'] = {
                'salario_base': int(input("Nuevo salario base: ")),
                'bonificaciones': int(input("Nuevas bonificaciones: ")),
                'deducciones': int(input("Nuevas deducciones: "))
            }

        response = self.send_request('UPDATE', data)
        print("\nRespuesta:", response)

    def select_employee(self):
        print("\n=== Consultar Empleado ===")
        search_by = input("Buscar por (1: ID, 2: Email): ")

        data = {}
        if search_by == '1':
            data['id'] = int(input("ID del empleado: "))
        else:
            data['email'] = input("Email del empleado: ")

        response = self.send_request('SELECT', data)

        if response['status'] == 'success':
            for employee in response['data']:
                print("\nDatos del empleado:")
                for key, value in employee.items():
                    print(f"{key}: {value}")
        else:
            print("\nError:", response['message'])

    def delete_employee(self):
        print("\n=== Dar de Baja Empleado ===")
        data = {
            'id': int(input("ID del empleado: ")),
            'motivo': input("Motivo de la baja: ")
        }

        response = self.send_request('DELETE', data)
        print("\nRespuesta:", response)

    def close(self):
        if self.socket:
            self.socket.close()
            self.socket = None

    def main_menu(self):
        while True:
            print("\n=== Sistema de Recursos Humanos ===")
            print("1. Insertar nuevo empleado")
            print("2. Actualizar empleado")
            print("3. Consultar empleado")
            print("4. Dar de baja empleado")
            print("5. Salir")

            option = input("\nSeleccione una opción: ")

            try:
                if option == '1':
                    self.insert_employee()
                elif option == '2':
                    self.update_employee()
                elif option == '3':
                    self.select_employee()
                elif option == '4':
                    self.delete_employee()
                elif option == '5':
                    print("Gracias por usar el sistema")
                    self.close()
                    break
                else:
                    print("Opción no válida")

            except Exception as e:
                logging.error(f"Error en la operación: {e}")
                print(f"Error realizando la operación: {e}")


if __name__ == '__main__':
    client = Client()
    try:
        client.main_menu()
    except KeyboardInterrupt:
        print("\nCerrando cliente...")
    finally:
        client.close()