# Sistema de Recursos Humanos con Sockets

Este proyecto implementa un sistema de gestión de recursos humanos utilizando una arquitectura cliente-servidor basada en sockets TCP/IP y MySQL como base de datos.

## Descripción

El sistema permite realizar operaciones CRUD (Create, Read, Update, Delete) sobre una base de datos de recursos humanos, utilizando una arquitectura distribuida donde:

- El cliente envía peticiones a través de sockets
- El servidor procesa estas peticiones y realiza operaciones en la base de datos
- Los resultados se devuelven al cliente para su visualización

### Características principales

- Arquitectura cliente-servidor usando sockets TCP/IP
- Base de datos MySQL para almacenamiento persistente
- Operaciones CRUD completas para gestión de empleados
- Manejo de históricos para empleados eliminados
- Gestión de departamentos, cargos y ubicaciones

## Estructura del Proyecto

```
rh-socket-system/
├── README.md                # Este archivo
├── requirements.txt         # Dependencias del proyecto
├── src/                    # Código fuente
│   ├── database/          # Scripts de base de datos
│   ├── server/            # Código del servidor
│   └── client/            # Código del cliente
└── config/                # Archivos de configuración
   └── database.ini            # Configuración de la Base de Datos
```

## Requisitos Previos

1. Python 3.8 o superior
2. MySQL Server 8.0 o superior
3. Pip (gestor de paquetes de Python)

## Instalación

1. Clonar el repositorio:
```bash
git clone https://github.com/usuario/rh-socket-system.git
cd rh-socket-system
```

2. Crear un entorno virtual:
```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. Instalar dependencias:
```bash
pip install -r requirements.txt
```

4. Configurar la base de datos:
   - Copiar `config/database.ini.example` a `config/database.ini`
   - Editar los datos de conexión en `database.ini`

5. Crear la base de datos:
```bash
python src/database/create_database.py
```

## Uso

1. Iniciar el servidor:
```bash
python src/server/server.py
```

2. En otra terminal, iniciar el cliente:
```bash
python src/client/client.py
```

### Operaciones Disponibles

1. Insertar empleado (INSERT)
2. Actualizar empleado (UPDATE)
3. Consultar empleado (SELECT)
4. Eliminar empleado (DELETE)

## Flujo de Trabajo

1. El cliente inicia y muestra un menú de opciones
2. El usuario selecciona una operación
3. El cliente solicita los datos necesarios
4. La petición se envía al servidor
5. El servidor procesa la petición y actualiza la base de datos
6. El resultado se devuelve al cliente
7. El cliente muestra el resultado al usuario

## Consideraciones Técnicas

- Puerto por defecto: 5000
- Protocolo: TCP/IP
- Formato de mensajes: JSON
- Timeout de conexión: 60 segundos

## Manejo de Errores

- Conexión perdida con el servidor
- Errores de base de datos
- Validación de datos
- Timeout de operaciones

## Seguridad

- Validación de datos de entrada
- Sanitización de consultas SQL
- Manejo de conexiones cerradas
- Logs de operaciones

## Autor
SUBGRUPO B02
