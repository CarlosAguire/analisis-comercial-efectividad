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

        # 1. Filtramos para eliminar filas que no necesitamos
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

        # 2. Removemos columnas duplicada
        # Log init
        time_stamp = get_time_stamp()
        message = "Removiendo columnas duplicadas..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_ofsc_dispatch = remove_duplicate_columns(df=self.df_ofsc_dispatch)

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

        # 4. Eliminamos filas duplicadas
        # Log init
        time_stamp = get_time_stamp()
        message = "Removiendo filas que no se necesitan..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.df_residential_plant = drop_duplicates_by_column(
            df=self.df_residential_plant,
            column="NOMBRE",
        )

    def create_tabla(self) -> None:
        """
        Crea el archivo de Excel del `DataFrame` que contiene los datos unificados y
        limpios de las tablas:
        - OFSC de despacho y capacidad.
        - Planta residencial.
        """

        # 1. Unimos el OFSC de despacho y capacidades en uno solo
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

        # 2. Cmabiamos el nombre de la llave foranea
        self.df_residential_plant = self.df_residential_plant.rename(
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
        self.df_output = join(
            df1=self.df_ofsc,
            df2=self.df_residential_plant,
            foreign_key="Asesor comercial",
            columns_df1=set(
                parameters.OFSC_CAPACITY_COLUMNS + parameters.OFSC_DISPATCH_COLUMNS
            ),
            columns_df2=RESIDENTIAL_PLANT_COLUMNS,
        )
        self.df_output["Razón sugerida"] = None
        self.df_output["Estado del análisis"] = None

        if parameters.DEBUG:
            self.__create_file(
                path=parameters.CLEAN_OFSC_PATH,
                df=self.df_ofsc,
                engine="openpyxl",
                sheet_name="DATOS",
                is_excel_table=False,
            )
            self.__create_file(
                path=parameters.CLEAN_RESIDENTIAL_PLANT_PATH,
                df=self.df_residential_plant,
                engine="openpyxl",
                sheet_name="DATOS",
                is_excel_table=False,
            )

        # Log init
        time_stamp = get_time_stamp()
        message = f"Creando earchivo final: {parameters.OUTPUT_FILE_PATH}"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        self.__create_file(
            path=parameters.OUTPUT_FILE_PATH,
            df=self.df_output,
            engine="xlsxwriter",
            sheet_name="DATOS",
            is_excel_table=True,
        )

    @staticmethod
    def __create_file(
        path: Path,
        df: pd.DataFrame,
        engine: str,
        sheet_name: str,
        is_excel_table: bool,
    ) -> None:
        """Crea el archivo de Excel de un `DataFrame` en la ruta indicada."""

        with pd.ExcelWriter(path=path, engine=engine, mode="w") as w:  # type: ignore
            df.to_excel(excel_writer=w, index=False, sheet_name=sheet_name)

            if is_excel_table:
                worksheet = w.sheets[sheet_name]

                # Dimensiones del rango
                (n_rows, n_columns) = df.shape

                # Encabezados para la tabla
                columns = [{"header": col} for col in df.columns]

                # La creamos como tabla de Excel
                worksheet.add_table(
                    0,
                    0,
                    n_rows,
                    n_columns - 1,
                    {"name": "TablaDatos", "columns": columns, "style": None},
                )
