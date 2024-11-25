import mysql.connector
import configparser
import os
import logging
from datetime import datetime


class DatabaseHandler:
    def __init__(self):
        self.config = self._read_config()
        self.connection = None
        self._connect()

    def _read_config(self):
        config = configparser.ConfigParser()
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config', 'database.ini')
        config.read(config_path)
        return config['mysql']

    def _connect(self):
        try:
            self.connection = mysql.connector.connect(
                host=self.config['host'],
                database=self.config['database'],
                user=self.config['user'],
                password=self.config['password']
            )
        except mysql.connector.Error as err:
            logging.error(f"Error conectando a la base de datos: {err}")
            raise

    def _ensure_connection(self):
        if not self.connection or not self.connection.is_connected():
            self._connect()

    def insert_employee(self, data):
        try:
            self._ensure_connection()
            cursor = self.connection.cursor(dictionary=True)

            # Insertar empleado
            insert_query = """
            INSERT INTO empleados (
                primer_nombre, segundo_nombre, primer_apellido, segundo_apellido,
                email, celular, fecha_contratacion, departamento_id, cargo_id
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            insert_values = (
                data['primer_nombre'],
                data['segundo_nombre'],
                data['primer_apellido'],
                data['segundo_apellido'],
                data['email'],
                data['celular'],
                data['fecha_contratacion'],
                data['departamento_id'],
                data['cargo_id']
            )
            cursor.execute(insert_query, insert_values)
            employee_id = cursor.lastrowid

            # Insertar salario
            if 'salario' in data:
                salary_query = """
                    INSERT INTO salarios (
                        empleado_id, salario_base, bonificaciones,
                        deducciones, salario_total
                    ) VALUES (
                        %s, %s, %s, %s, %s
                    )
                """
                salario_total = (data['salario'].get('salario_base', 0) +
                                 data['salario'].get('bonificaciones', 0) -
                                 data['salario'].get('deducciones', 0))
                cursor.execute(salary_query, (
                    employee_id,
                    data['salario'].get('salario_base'),
                    data['salario'].get('bonificaciones'),
                    data['salario'].get('deducciones'),
                    salario_total
                ))

            self.connection.commit()
            return {'status': 'success', 'message': 'Empleado insertado correctamente', 'id': employee_id}

        except mysql.connector.Error as err:
            self.connection.rollback()
            return {'status': 'error', 'message': str(err)}
        finally:
            cursor.close()

    def update_employee(self, data):
        try:
            self._ensure_connection()
            cursor = self.connection.cursor(dictionary=True)

            employee_id = data.pop('id')

            # Construir query dinámica de actualización
            update_fields = []
            update_values = {}

            for key, value in data.items():
                if key != 'salario':
                    update_fields.append(f"{key} = %({key})s")
                    update_values[key] = value

            if update_fields:
                update_query = f"""
                    UPDATE empleados 
                    SET {', '.join(update_fields)}
                    WHERE id = %(employee_id)s
                """
                update_values['employee_id'] = employee_id
                cursor.execute(update_query, update_values)

            # Actualizar salario si está presente
            if 'salario' in data:
                salary_query = """
                    UPDATE salarios
                    SET salario_base = %s, bonificaciones = %s,
                        deducciones = %s, salario_total = %s
                    WHERE empleado_id = %s
                """
                salario_total = (data['salario'].get('salario_base', 0) +
                                 data['salario'].get('bonificaciones', 0) -
                                 data['salario'].get('deducciones', 0))
                cursor.execute(salary_query, (
                    data['salario'].get('salario_base'),
                    data['salario'].get('bonificaciones'),
                    data['salario'].get('deducciones'),
                    salario_total,
                    employee_id
                ))

            self.connection.commit()
            return {'status': 'success', 'message': 'Empleado actualizado correctamente'}

        except mysql.connector.Error as err:
            self.connection.rollback()
            return {'status': 'error', 'message': str(err)}
        finally:
            cursor.close()

    def select_employee(self, data):
        try:
            self._ensure_connection()
            cursor = self.connection.cursor(dictionary=True)

            query = """
                SELECT e.*, s.salario_base, s.bonificaciones, s.deducciones, s.salario_total,
                       d.nombre as departamento, c.titulo as cargo
                FROM empleados e
                LEFT JOIN salarios s ON e.id = s.empleado_id
                LEFT JOIN departamentos d ON e.departamento_id = d.id
                LEFT JOIN cargo c ON e.cargo_id = c.id
            """

            conditions = []
            params = {}

            if 'id' in data:
                conditions.append("e.id = %(id)s")
                params['id'] = data['id']
            if 'email' in data:
                conditions.append("e.email = %(email)s")
                params['email'] = data['email']

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

            cursor.execute(query, params)
            result = cursor.fetchall()

            return {'status': 'success', 'data': result}

        except mysql.connector.Error as err:
            return {'status': 'error', 'message': str(err)}
        finally:
            cursor.close()

    def delete_employee(self, data):
        try:
            self._ensure_connection()
            cursor = self.connection.cursor(dictionary=True)

            # Primero insertar en históricos
            historic_query = """
                INSERT INTO historicos (empleado_id, fecha_retiro, motivo)
                VALUES (%(id)s, %(fecha_retiro)s, %(motivo)s)
            """
            historic_data = {
                'id': data['id'],
                'fecha_retiro': datetime.now().date(),
                'motivo': data.get('motivo', 'No especificado')
            }
            cursor.execute(historic_query, historic_data)

            # Luego marcar como inactivo en empleados
            update_query = """
                UPDATE empleados
                SET estado = FALSE
                WHERE id = %(id)s
            """
            cursor.execute(update_query, {'id': data['id']})

            self.connection.commit()
            return {'status': 'success', 'message': 'Empleado dado de baja correctamente'}

        except mysql.connector.Error as err:
            self.connection.rollback()
            return {'status': 'error', 'message': str(err)}
        finally:
            cursor.close()

    def __del__(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()