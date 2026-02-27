from copy import deepcopy
from pathlib import Path

import pandas as pd

from config import parameters
from data.operations import (
    drop_columns,
    drop_duplicates_by_column,
    filter,
    join,
    read_excel,
    remove_duplicate_columns,
)
from logs_setup import get_time_stamp


class CleanData:
    def __init__(
        self,
        ofsc_dispatch_path: Path,
        ofsc_capacity_path: Path,
        residential_plant_path: Path,
    ) -> None:
        # Log init
        time_stamp = get_time_stamp()
        message = f"Leyendo datos del archivo: {ofsc_dispatch_path}"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc_dispatch = read_excel(path=ofsc_dispatch_path, sheet=0)

        # Log init
        time_stamp = get_time_stamp()
        message = f"Leyendo datos del archivo: {ofsc_capacity_path}"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc_capacity = read_excel(path=ofsc_capacity_path, sheet=0)

        # Log init
        time_stamp = get_time_stamp()
        message = f"Leyendo datos del archivo: {residential_plant_path}"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_residential_plant = read_excel(path=residential_plant_path, sheet=0)

        self.df_ofsc = None
        self.df_output = None

    def clean(self) -> None:
        """
        Crea los `DataFrame` y limpia los datos de las tablas:
        - OFSC de despacho y capacidad.
        - Planta residencial.
        """

        # 1. Removemos columnas duplicada
        # Log init
        time_stamp = get_time_stamp()
        message = "Removiendo columnas duplicadas..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc_dispatch = remove_duplicate_columns(
            df=self.df_ofsc_dispatch,
            columna_objetivo="Notas de Cierre",
        )

        # 2. Filtramos para eliminar filas que no necesitamos
        # Log init
        time_stamp = get_time_stamp()
        message = "Filtrando datos..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc_dispatch = filter(
            df=self.df_ofsc_dispatch,
            filters={
                "Estado": "No completado",
                "Tipo de Actividad": "Instalaciones",
                "Tipo de Red": "Pymes",
            },
        )
        self.df_ofsc_capacity = filter(
            df=self.df_ofsc_capacity,
            filters={
                "Estado": "No completado",
                "Tipo de Actividad": "Instalaciones",
                "Tipo de Red": "Pymes",
            },
        )
        self.df_residential_plant = filter(
            df=self.df_residential_plant,
            filters={"NOMBRE": self.df_ofsc_capacity["Asesor comercial"].tolist()},
        )

        # 3. Eliminamos columnas que no necesitamos
        # Log init
        time_stamp = get_time_stamp()
        message = "Removiendo columnas que no se necesitan..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc_dispatch = drop_columns(
            columns_preserve=parameters.OFSC_DISPATCH_COLUMNS,
            df=self.df_ofsc_dispatch,
        )
        self.df_ofsc_capacity = drop_columns(
            columns_preserve=parameters.OFSC_CAPACITY_COLUMNS,
            df=self.df_ofsc_capacity,
        )
        self.df_residential_plant = drop_columns(
            columns_preserve=parameters.RESIDENTIAL_PLANT_COLUMNS,
            df=self.df_residential_plant,
        )

        # 5. Unimos el OFSC de despacho y capacidades en uno solo
        # Log init
        time_stamp = get_time_stamp()
        message = "Uniendo el OFSC de despacho y capacidades en uno solo..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc = join(
            df1=self.df_ofsc_dispatch,
            df2=self.df_ofsc_capacity,
            foreign_key="Orden de trabajo",
            columns_df1=parameters.OFSC_DISPATCH_COLUMNS,
            columns_df2=parameters.OFSC_CAPACITY_COLUMNS,
        )

    @classmethod
    def create_tabla(
        cls,
        df_ofsc_list: list[pd.DataFrame],
        df_residential_plant_list: list[pd.DataFrame],
    ) -> None:
        """
        Crea el archivo de Excel del `DataFrame` que contiene los datos unificados y
        limpios de las tablas:
        - OFSC de despacho y capacidad.
        - Planta residencial.
        """

        df_ofsc_final = pd.concat(objs=df_ofsc_list, ignore_index=True)
        df_residential_plant_final = pd.concat(
            objs=df_residential_plant_list,
            ignore_index=True,
        )

        # 4. Eliminamos filas duplicadas
        # Log init
        time_stamp = get_time_stamp()
        message = "Removiendo filas que no se necesitan..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        df_residential_plant_final = drop_duplicates_by_column(
            df=df_residential_plant_final,
            column="NOMBRE",
        )

        # 2. Cmabiamos el nombre de la llave foranea
        df_residential_plant_final = df_residential_plant_final.rename(
            columns={"NOMBRE": "Asesor comercial"}
        )

        index = 0

        for campo in parameters.RESIDENTIAL_PLANT_COLUMNS:
            if campo == "NOMBRE":
                break

            index = index + 1

        RESIDENTIAL_PLANT_COLUMNS = deepcopy(parameters.RESIDENTIAL_PLANT_COLUMNS)
        RESIDENTIAL_PLANT_COLUMNS.pop(index)
        RESIDENTIAL_PLANT_COLUMNS.append("Asesor comercial")

        # 3. Creamos la tabla final
        df_output = join(
            df1=df_ofsc_final,
            df2=df_residential_plant_final,
            foreign_key="Asesor comercial",
            columns_df1=set(
                parameters.OFSC_CAPACITY_COLUMNS + parameters.OFSC_DISPATCH_COLUMNS
            ),
            columns_df2=RESIDENTIAL_PLANT_COLUMNS,
        )
        df_output["Razón sugerida"] = None
        df_output["Estado del análisis"] = None

        # Log init
        time_stamp = get_time_stamp()
        message = f"Creando earchivo final: {parameters.OUTPUT_FILE_PATH}"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        with pd.ExcelWriter(
            path=parameters.OUTPUT_FILE_PATH,
            engine="xlsxwriter",
            mode="w",
        ) as w:
            sheet_name = "DATOS"
            df_output.to_excel(excel_writer=w, index=False, sheet_name=sheet_name)

            worksheet = w.sheets[sheet_name]

            # Dimensiones del rango
            (n_rows, n_columns) = df_output.shape

            # Encabezados para la tabla
            columns = [{"header": col} for col in df_output.columns]

            # La creamos como tabla de Excel
            worksheet.add_table(
                0,
                0,
                n_rows,
                n_columns - 1,
                {"name": "TablaDatos", "columns": columns, "style": None},
            )
