import mysql.connector
import configparser
import os


class DatabaseCreator:
    def __init__(self):
        self.config = self._read_config()

    def _read_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database.ini')
        config.read(config_path)
        return config['mysql']

    def create_database(self):
        try:
            # Conectar a MySQL sin seleccionar una base de datos
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password']
            )

            cursor = conn.cursor()

            # Leer el archivo SQL
            schema_path = os.path.join(os.path.dirname(__file__), 'schema.sql')
            with open(schema_path, 'r') as file:
                sql_commands = file.read().split(';')

            # Ejecutar cada comando SQL
            for command in sql_commands:
                if command.strip():
                    cursor.execute(command)
                    conn.commit()

            print("Base de datos creada exitosamente")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if 'conn' in locals():
                cursor.close()
                conn.close()

    def insert_initial_data(self):
        try:
            conn = mysql.connector.connect(
                host=self.config['host'],
                user=self.config['user'],
                password=self.config['password'],
                database='rh_socket_system'
            )

            cursor = conn.cursor()

            # Insertar departamento inicial
            cursor.execute("""
                INSERT INTO departamentos (nombre) 
                VALUES ('Recursos Humanos')
            """)

            # Insertar cargo inicial
            cursor.execute("""
                INSERT INTO cargo (titulo, descripcion, departamento_id) 
                VALUES ('Director RRHH', 'Director del departamento de RRHH', 1)
            """)

            # Insertar tipo de permiso inicial
            cursor.execute("""
                INSERT INTO tipos_permisos (nombre, descripcion) 
                VALUES ('Vacaciones', 'Permiso por vacaciones anuales')
            """)

            conn.commit()
            print("Datos iniciales insertados exitosamente")

        except mysql.connector.Error as err:
            print(f"Error: {err}")

        finally:
            if 'conn' in locals():
                cursor.close()
                conn.close()


if __name__ == "__main__":
    creator = DatabaseCreator()
    creator.create_database()
    creator.insert_initial_data()