import socket
import json
import threading
from database_handler import DatabaseHandler
import logging
import traceback
from datetime import date, datetime

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

class CustomJSONEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, (date, datetime)):
            return obj.isoformat()
        return super().default(obj)

class Server:
    def __init__(self, host='localhost', port=33056):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.db_handler = DatabaseHandler()

    def start(self):
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            logging.info(f"Servidor iniciado en {self.host}:{self.port}")

            while True:
                client_socket, address = self.server_socket.accept()
                logging.info(f"Cliente conectado desde {address}")
                client_thread = threading.Thread(
                    target=self.handle_client,
                    args=(client_socket, address)
                )
                client_thread.start()

        except Exception as e:
            logging.error(f"Error en el servidor: {e}")
            logging.error(traceback.format_exc())
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket, address):
        try:
            while True:
                data = client_socket.recv(4096)
                if not data:
                    logging.info(f"Cliente {address} desconectado")
                    break

                try:
                    request = json.loads(data.decode('utf-8'))
                    logging.debug(f"Solicitud recibida de {address}: {request}")
                except json.JSONDecodeError:
                    logging.error(f"Error decodificando JSON de {address}")
                    response = {'status': 'error', 'message': 'JSON inválido'}
                    client_socket.send(json.dumps(response).encode('utf-8'))
                    continue

                try:
                    response = self.process_request(request)
                    logging.debug(f"Respuesta para {address}: {response}")

                    if not response:
                        response = {'status': 'error', 'message': 'Sin respuesta del servidor'}

                    response_json = json.dumps(response, cls=CustomJSONEncoder)
                    client_socket.send(response_json.encode('utf-8'))

                except Exception as e:
                    logging.error(f"Error procesando solicitud de {address}: {e}")
                    error_response = {
                        'status': 'error',
                        'message': f'Error interno del servidor: {str(e)}'
                    }
                    client_socket.send(json.dumps(error_response).encode('utf-8'))

        except Exception as e:
            logging.error(f"Error manejando cliente {address}: {e}")
        finally:
            client_socket.close()

    def process_request(self, request):
        try:
            logging.debug(f"Procesando solicitud: {request}")
            operation = request.get('operation')
            data = request.get('data', {})

            if operation == 'INSERT':
                return self.db_handler.insert_employee(data)
            elif operation == 'UPDATE':
                return self.db_handler.update_employee(data)
            elif operation == 'SELECT':
                result = self.db_handler.select_employee(data)
                logging.debug(f"Resultado SELECT: {result}")
                return result
            elif operation == 'DELETE':
                return self.db_handler.delete_employee(data)
            else:
                logging.warning(f"Operación no válida: {operation}")
                return {'status': 'error', 'message': 'Operación no válida'}

        except Exception as e:
            logging.error(f"Error en process_request: {e}")
            logging.error(traceback.format_exc())
            return {'status': 'error', 'message': str(e)}


if __name__ == '__main__':
    server = Server()
    server.start()