import socket
import json
import threading
from database_handler import DatabaseHandler
import logging

logging.basicConfig(level=logging.INFO,
                   format='%(asctime)s - %(levelname)s - %(message)s')

class Server:
    def __init__(self, host='localhost', port=5000):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
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
                    args=(client_socket,)
                )
                client_thread.start()

        except Exception as e:
            logging.error(f"Error en el servidor: {e}")
        finally:
            self.server_socket.close()

    def handle_client(self, client_socket):
        try:
            while True:
                data = client_socket.recv(4096).decode('utf-8')
                if not data:
                    break

                request = json.loads(data)
                response = self.process_request(request)
                client_socket.send(json.dumps(response).encode('utf-8'))

        except Exception as e:
            logging.error(f"Error manejando cliente: {e}")
        finally:
            client_socket.close()

    def process_request(self, request):
        try:
            operation = request.get('operation')
            data = request.get('data', {})

            if operation == 'INSERT':
                return self.db_handler.insert_employee(data)
            elif operation == 'UPDATE':
                return self.db_handler.update_employee(data)
            elif operation == 'SELECT':
                return self.db_handler.select_employee(data)
            elif operation == 'DELETE':
                return self.db_handler.delete_employee(data)
            else:
                return {'status': 'error', 'message': 'Operación no válida'}

        except Exception as e:
            logging.error(f"Error procesando solicitud: {e}")
            return {'status': 'error', 'message': str(e)}

if __name__ == '__main__':
    server = Server()
    server.start()