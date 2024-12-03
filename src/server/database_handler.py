import json
import mysql.connector
import configparser
import os
import logging
from datetime import datetime, date

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

            logging.info(f"Resultados de la consulta: {result}")  # Agregado

            return {'status': 'success', 'data': result}

        except mysql.connector.Error as err:
            return {'status': 'error', 'message': str(err)}
        except Exception as e:
            return {'status': 'error ', 'message': str(e)}

    def delete_employee(self, data):
        try:
            self._ensure_connection()
            cursor = self.connection.cursor()

            fecha_retiro = datetime.now().date()

            self.connection.start_transaction()

            update_query = """
            UPDATE empleados 
            SET 
                estado = 0, 
                updated_at = %s 
            WHERE id = %s
            """

            cursor.execute(update_query, (
                datetime.now(),
                data['id']
            ))

            insert_historico_query = """
            INSERT INTO historicos (
                empleado_id, 
                fecha_retiro, 
                motivo
            ) VALUES (%s, %s, %s)
            """

            cursor.execute(insert_historico_query, (
                data['id'],
                fecha_retiro,
                data.get('motivo', '')
            ))

            self.connection.commit()

            if cursor.rowcount > 0:
                return {
                    'status': 'success',
                    'message': 'Empleado dado de baja exitosamente',
                    'rows_affected': cursor.rowcount
                }
            else:
                return {
                    'status': 'error',
                    'message': 'No se encontró el empleado o no se pudo dar de baja'
                }

        except mysql.connector.Error as err:
            self.connection.rollback()
            logging.error(f"Error en la base de datos: {err}")
            return {'status': 'error', 'message': str(err)}
        except Exception as e:
            self.connection.rollback()
            logging.error(f"Error inesperado: {e}")
            return {'status': 'error', 'message': str(e)}
        finally:
            if cursor:
                cursor.close()

    def __del__(self):
        if self.connection and self.connection.is_connected():
            self.connection.close()