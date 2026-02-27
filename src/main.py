import argparse
import sys

from config import parameters
from data.clean import CleanData
from logs_setup import get_time_stamp
from match_files import pair_files

RESIDENTIAL_PLANT_PATH = (
    parameters.PROJECT_ROOT / "databases" / "RM Planta Residencial.xlsx"
)
OFSC_CAPACITY_DAILY_FOLDER = (
    parameters.PROJECT_ROOT / "databases" / "Análisis Diario" / "OFSC (CAPACIDADES)"
)
OFSC_DISPATCH_DAILY_FOLDER = (
    parameters.PROJECT_ROOT / "databases" / "Análisis Diario" / "OFSC (DESPACHO)"
)
OFSC_CAPACITY_MONTHLY_FOLDER = (
    parameters.PROJECT_ROOT / "databases" / "Análisis Mensual" / "OFSC (CAPACIDADES)"
)
OFSC_DISPATCH_MONTHLY_FOLDER = (
    parameters.PROJECT_ROOT / "databases" / "Análisis Mensual" / "OFSC (DESPACHO)"
)


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Demo de flags booleano")
    parser.add_argument(
        "--monthly",
        action="store_true",
        help="Busca los archivos de los datos de un mes.",
    )
    parser.add_argument(
        "--daily",
        action="store_true",
        help="Solo busca los archivos de los datos de un día.",
    )
    return parser.parse_args()


def main(monthly: bool, daily: bool) -> None:

    if monthly:
        result = pair_files(
            dir1=OFSC_CAPACITY_MONTHLY_FOLDER,
            dir2=OFSC_DISPATCH_MONTHLY_FOLDER,
        )

        # Log init
        time_stamp = get_time_stamp()
        message = "Se van a limpiar los datos de los siguientes archivos:\n\n"

        for file_path1, file_path2 in result.pairs:
            message = message + f">> {file_path1}\n>> {file_path2}\n"

        message = message + f">> {RESIDENTIAL_PLANT_PATH}\n\n"
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

        for file_path1, file_path2 in result.pairs:
            try:
                data = CleanData(
                    ofsc_capacity_path=file_path1,
                    ofsc_dispatch_path=file_path2,
                    residential_plant_path=RESIDENTIAL_PLANT_PATH,
                )
                data.clean()
                data.create_tabla()
            except Exception as e:
                print(f"Error: {e}")

            # Log init
            time_stamp = get_time_stamp()
            message = "LIMPIEZA COMPLETADA."
            print(f"{time_stamp} [ INFO ] {message}")
            # Log end
    if daily:
        result = pair_files(
            dir1=OFSC_CAPACITY_DAILY_FOLDER,
            dir2=OFSC_DISPATCH_DAILY_FOLDER,
        )

        for file_path1, file_path2 in result.pairs:
            # Log init
            time_stamp = get_time_stamp()
            message = (
                "Se van a limpiar los datos de los siguientes archivos:\n\n"
                f">> {file_path1}\n"
                f">> {file_path2}\n"
                f">> {RESIDENTIAL_PLANT_PATH}\n"
            )
            print(f"{time_stamp} [ INFO ] {message}")
            # Log end

            try:
                data = CleanData(
                    ofsc_capacity_path=file_path1,
                    ofsc_dispatch_path=file_path2,
                    residential_plant_path=RESIDENTIAL_PLANT_PATH,
                )
                data.clean()
                data.create_tabla()
            except Exception as e:
                print(f"Error: {e}")

            # Log init
            time_stamp = get_time_stamp()
            message = "LIMPIEZA COMPLETADA."
            print(f"{time_stamp} [ INFO ] {message}")
            # Log end


if __name__ == "__main__":
    args = get_args()

    if args.monthly and args.daily:
        # Log init
        time_stamp = get_time_stamp()
        message = "No puedes usar las banderas --daily y --monthly al mismo tiempo."
        formatted_message = f"{time_stamp} [ ERROR ] {message}"
        sys.exit(formatted_message)
        # Log end
    if args.monthly:
        # Log init
        time_stamp = get_time_stamp()
        message = "Iniciando limpieza de datos para un análisis mensual..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end
    if args.daily:
        # Log init
        time_stamp = get_time_stamp()
        message = "Iniciando limpieza de datos para un análisis diario..."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end

    main(monthly=args.monthly, daily=args.daily)
