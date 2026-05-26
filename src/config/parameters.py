from pathlib import Path

# Configuración de ruta raíz del proyecto
THIS_FILE = Path(__file__).resolve()
PROJECT_ROOT = THIS_FILE.parent.parent.parent


# Configuraciónes y rutas de archivos
DATABASES_FOLDER = PROJECT_ROOT / "databases"
FTTH_HFC_FOLDER = DATABASES_FOLDER / "FTTH-HFC"
FO_FOLDER = DATABASES_FOLDER / "FO"
BACKLOG_FOLDER = DATABASES_FOLDER / "Backlog"
LOGS_FOLDER = PROJECT_ROOT / "logs"


# Configuración de rutas de archivos
RESIDENTIAL_PLANT_PATH = DATABASES_FOLDER / "RM Planta Residencial.csv"
GPON_BASES_PATH = DATABASES_FOLDER / "BASES CENTROS COMERCIALES GPON.xlsx"
BROWNFIELD_BASES_PATH = DATABASES_FOLDER / "BASE BROWNFIELD 2026 Oriente.xlsx"
PY_OUT_LOGS_PATH = LOGS_FOLDER / "py_out_logs.txt"
LOGS_PATH = LOGS_FOLDER / "logs.txt"


# Tipos de análisis
REASONED_ANALYSIS = "análisis de razonadas"
CONTACT_ANALYSIS = "análisis de contacto"
BACKLOG_ANALYSIS = "análisis de backlog"
BACKLOG_ONNET_ANALYSIS = "análisis de backlog onnet"
PRODUCTIVITY_ANALYSIS = "análisis de productividad"
MIGRATIONS_ANALYSIS = "análisis de migraciones"


# Tipos de datos para cada archivo
RESIDENTIAL_PLANT_TYPES = {
    "TCARGU": "string",
    "CC_COMPLETA": "string",
    "NOMBRE": "string",
    "GV-Especialista": "string",
    "GV-Descripcion": "string",
    "CANAL2": "string",
    "JEFE 1 CANAL REGIONAL": "string",
}
FTTH_HFC_CAPACITY_TYPES = {
    "Estado": "string",
    "Razón": "string",
    "Tipo de Actividad": "string",
    "Ciudad": "string",
    "Orden de trabajo": "string",
    "Tipo de Red": "string",
    "Asesor comercial": "string",
    "Código Asesor comercial": "string",
    "Ventana de servicio": "string",
    "Fecha": "string",
    "Inicio": "string",
}
FTTH_HFC_DISPATCH_TYPES = {
    "Notas de Cierre": "string",
    "Orden de trabajo": "string",
    "Tipo de Actividad": "string",
    "Fecha": "string",
    "Inicio": "string",
    "Compañia": "string",
}
FO_TYPES = {
    "Orden de trabajo": "string",
    "Ventana de servicio": "string",
}
BACKLOG_TYPES = {
    "TIPO_TRABAJO": "string",
    "TIPO_BACKLOG": "string",
    "CUENTA": "string",
    "OT/LL": "string",
    "Region": "string",
    "CONVENIENCIA": "string",
    "Comunidad": "string",
    "Opera": "string",
    "Red": "string",
    "NODO": "string",
    "ESTADO_ORDEN": "string",
    "ESTADO_VISITA": "string",
    "FECHA_AGENDA_FUTURO": "string",
    "ANTIGUEDAD_ULTIMA_VISITA": "string",
    "CUENTA_MATRIZ": "string",
    "CEDULA_VENDEDOR": "string",
    "ANTIGUEDAD_DIGITACION": "string",
    "CLASE": "string",
    "SEGMENTO": "string",
    "Aliado Zonificado": "string",
}
GPON_TYPES = {
    "CODIGO": "string",
    "CUENTA": "string",
    "TIPIFICACION REGIONAL": "string",
    "CUENTA MATRIZ": "string",
    "BASE TV": "string",
    "ALIADO": "string",
    "Ciudad": "string",
    "FECHA DE MIGRACION": "string",
}
BROWNFIELD_TYPES = {
    "ESTADO REGIONAL": "string",
    "CRONOGRAMA DESMONTE REGIONAL": "string",
    "CRONOGRAMA DESMONTE TRANSVERSAL": "string",
    "TIPIFICACION": "string",
    "ESTADO": "string",
    "CUENTA MATRIZ": "string",
    "CRUCE POTENCIAL": "string",
    "CUENTA": "string",
    "ALIADO": "string",
    "CIUDAD": "string",
    "FECHA AGENDA": "string",
    "NOTA": "string",
}

# Filtros para cada tipo de análisis
FILTERS = {
    REASONED_ANALYSIS: {
        "dispatch_file": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            },
        },
        "capacity_file": {
            "include": {
                "Estado": "No completado",
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            }
        },
    },
    CONTACT_ANALYSIS: {
        "capacity_file": {
            "include": {
                "Tipo de Actividad": ["Instalaciones", "INSTALACIONES FTTH"],
                "Tipo de Red": ["Pymes", "FTTX"],
            }
        },
    },
    BACKLOG_ANALYSIS: {
        "backlog_file": {
            "include": {
                "Region": "REGION ORIENTE",
            },
            "exclude": {
                "TIPO_TRABAJO": [
                    "Cambio Control",
                    "Demostracion",
                    "Desconexiones",
                    "Reconexiones",
                    "Supervision",
                ],
                "SEGMENTO": [
                    "RE",
                    "RAN",
                    "RAT",
                    "RVA",
                    "REC",
                ],
            },
        },
    },
    BACKLOG_ONNET_ANALYSIS: {
        "capacity_file": {
            "include": {
                "Owner": "Onnet",
                "Tipo de Red": ["Pymes", "FTTX"],
            },
            "contains": {
                "Nodo": "K",
            },
        },
    },
}


# Lista de columnas a conservar
COLUMNS_TO_RESERVE = {
    REASONED_ANALYSIS: {
        "dispatch_file": [
            "Notas de Cierre",
            "Orden de trabajo",
            "Fecha",
            "Inicio",
            "Compañia",
        ],
        "capacity_file": [
            "Estado",
            "Razón",
            "Tipo de Actividad",
            "Ciudad",
            "Orden de trabajo",
            "Tipo de Red",
            "Asesor comercial",
            "Código Asesor comercial",
            "Fecha",
            "Inicio",
        ],
        "residential_plant_file": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    CONTACT_ANALYSIS: {
        "capacity_file": [
            "Tipo de Actividad",
            "Ciudad",
            "Orden de trabajo",
            "Tipo de Red",
            "Compañia",
            "Asesor comercial",
            "Código Asesor comercial",
            "Telefono dos del cliente",
            "Teléfono 3",
            "Celuar del contacto",
            "Fecha",
        ],
        "residential_plant_file": [
            "NOMBRE",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
        ],
    },
    BACKLOG_ANALYSIS: {
        "backlog_file": [
            "TIPO_TRABAJO",
            "TIPO_BACKLOG",
            "CUENTA",
            "OT/LL",
            "Region",
            "CONVENIENCIA",
            "Comunidad",
            "Opera",
            "Red",
            "NODO",
            "ESTADO_ORDEN",
            "ESTADO_VISITA",
            "FECHA_AGENDA_FUTURO",
            "ANTIGUEDAD_ULTIMA_VISITA",
            "CUENTA_MATRIZ",
            "CEDULA_VENDEDOR",
            "ANTIGUEDAD_DIGITACION",
            "CLASE",
            "SEGMENTO",
            "Aliado Zonificado",
        ],
        "residential_plant_file": [
            "TCARGU",
            "CC_COMPLETA",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
            "NOMBRE",
        ],
        "capacity_file": [
            "Orden de trabajo",
            "Ventana de servicio",
        ],
        "fo_file": [
            "Orden de trabajo",
            "Ventana de servicio",
        ],
    },
    BACKLOG_ONNET_ANALYSIS: {
        "residential_plant_file": [
            "TCARGU",
            "CC_COMPLETA",
            "GV-Especialista",
            "GV-Descripcion",
            "JEFE 1 CANAL REGIONAL",
            "CANAL2",
            "NOMBRE",
        ],
        "ofsc_capacity": [
            "Orden de trabajo",
            "Tipo de Actividad",
            "Estado",
            "Ciudad",
            "Razón",
            "Tipo de Red",
            "Compañia",
            "Ventana de servicio",
            "Fecha",
            "Asesor comercial",
        ],
    },
}


# Nombre de columnas finales para cada análisis
FINAL_COLUMNS = {
    REASONED_ANALYSIS: {
        "Orden de trabajo": "Orden de Trabajo",
        "Notas de Cierre": "Nota de Cierre",
        "Compañia": "Aliado",
        "Inicio": "Hora",
        "Asesor comercial": "Asesor Comercial",
        "Código Asesor comercial": "Código del Asesor Comercial",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    CONTACT_ANALYSIS: {
        "Orden de trabajo": "Orden de Trabajo",
        "Compañia": "Aliado",
        "Asesor comercial": "Asesor Comercial",
        "Código Asesor comercial": "Código del Asesor Comercial",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    BACKLOG_ANALYSIS: {
        "TIPO_TRABAJO": "Tipo de Trabajo",
        "TIPO_BACKLOG": "Tipo de Backlog",
        "CUENTA": "Cuenta",
        "OT/LL": "OT",
        "CONVENIENCIA": "Convivencia",
        "ESTADO_ORDEN": "Estado de la Orden",
        "Aliado Zonificado": "Aliado",
        "ANTIGUEDAD_DIGITACION": "Antiguedad desde la Digitación",
        "CLASE": "Clase",
        "NODO": "Nodo",
        "CEDULA_VENDEDOR": "Cédula del Vendedor",
        "SEGMENTO": "Segmento",
        "Comunidad": "Ciudad",
        "FECHA_AGENDA_FUTURO": "Fecha Agenda Futuro",
        "ESTADO_VISITA": "Estado de la Visita",
        "ANTIGUEDAD_ULTIMA_VISITA": "Antiguedad desde la Última Visita",
        "CUENTA_MATRIZ": "Cuenta Matriz",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    BACKLOG_ONNET_ANALYSIS: {
        "Orden de trabajo": "Orden de Trabajo",
        "Compañia": "Aliado",
        "GV-Especialista": "Especialista",
        "GV-Descripcion": "Proveedor",
        "CANAL2": "Canal",
        "JEFE 1 CANAL REGIONAL": "Jefe de Canal",
    },
    MIGRATIONS_ANALYSIS: {
        "brownfield_file": {
            "ESTADO REGIONAL": "Estado",
            "CUENTA MATRIZ": "Cuenta Matriz",
            "CUENTA": "Cuenta",
            "CRUCE POTENCIAL": "Cruce Potencial",
            "ALIADO": "Aliado",
            "CIUDAD": "Ciudad",
            "FECHA AGENDA": "Fecha",
            "TIPIFICACION": "Tipificación",
            "CRONOGRAMA DESMONTE REGIONAL": "Cronograma Desmonte Regional",
            "CRONOGRAMA DESMONTE TRANSVERSAL": "Cronograma Desmonte Transversal",
            "NOTA": "Nota",
        },
        "gpon_file": {
            "TIPIFICACION REGIONAL": "Estado",
            "CUENTA MATRIZ": "Cuenta Matriz",
            "CUENTA": "Cuenta",
            "ALIADO": "Aliado",
            "BASE TV": "Cruce Potencial",
            "Ciudad": "Ciudad",
            "FECHA DE MIGRACION": "Fecha",
            "CODIGO": "Código",
        },
    },
}


# Orden de columnas para el archivo final de cada análisis
COLUMN_ORDER = {
    REASONED_ANALYSIS: [
        "Orden de Trabajo",
        "Tipo de Actividad",
        "Estado",
        "Razón",
        "Nota de Cierre",
        "Tipo de Red",
        "Aliado",
        "Ciudad",
        "Código del Asesor Comercial",
        "Asesor Comercial",
        "Especialista",
        "Proveedor",
        "Canal",
        "Jefe de Canal",
        "Razón Sugerida",
        "Estado de la Razón",
        "Fecha",
        "Hora",
    ],
    MIGRATIONS_ANALYSIS: [
        "Estado",
        "Cuenta Matriz",
        "Tipo de Red",
        "Cuenta",
        "Aliado",
        "Ciudad",
        "Tipificación",
        "Cruce Potencial",
        "Cronograma Desmonte Regional",
        "Cronograma Desmonte Transversal",
        "Nota",
        "Código",
        "Fecha",
    ],
}


# Archivo de salida
REASONED_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-razonadas.xlsx"
PRODUCTIVITY_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-productividad.xlsx"
MIGRATIONS_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-migraciones.xlsx"
CONTACT_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-contacto.xlsx"
BACKLOG_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-backlog.xlsx"
BACKLOG_ONNET_ANALYSIS_FILE_PATH = PROJECT_ROOT / "datos-backlog-onnet.xlsx"
