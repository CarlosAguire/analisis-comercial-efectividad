from config import parameters
from data.clean import CleanData
from logs_setup import get_time_stamp
from match_files import pair_files

RESIDENTIAL_PLANT_PATH = (
    parameters.PROJECT_ROOT / "databases" / "RM Planta Residencial.xlsx"
)
OFSC_CAPACITY_FOLDER = parameters.PROJECT_ROOT / "databases" / "OFSC (CAPACIDADES)"
OFSC_DISPATCH_FOLDER = parameters.PROJECT_ROOT / "databases" / "OFSC (DESPACHO)"


def main() -> None:

    result = pair_files(dir1=OFSC_CAPACITY_FOLDER, dir2=OFSC_DISPATCH_FOLDER)

    # Log init
    time_stamp = get_time_stamp()
    message = "Se van a limpiar los datos de los siguientes archivos:\n\n"

    for file_path1, file_path2 in result.pairs:
        message = message + f">> {file_path1}\n>> {file_path2}\n"

    message = message + f">> {RESIDENTIAL_PLANT_PATH}\n"
    print(f"{time_stamp} [ INFO ] {message}")
    # Log end

    df_ofsc_list = []
    df_residential_plant_list = []

    for file_path1, file_path2 in result.pairs:
        try:
            data = CleanData(
                ofsc_capacity_path=file_path1,
                ofsc_dispatch_path=file_path2,
                residential_plant_path=RESIDENTIAL_PLANT_PATH,
            )
            data.clean()
            df_ofsc_list.append(data.df_ofsc)
            df_residential_plant_list.append(data.df_residential_plant)
        except Exception as e:
            print(f"Error: {e}")

        CleanData.create_tabla(
            df_ofsc_list=df_ofsc_list,
            df_residential_plant_list=df_residential_plant_list,
        )
        # Log init
        time_stamp = get_time_stamp()
        message = "LIMPIEZA COMPLETADA."
        print(f"{time_stamp} [ INFO ] {message}")
        # Log end


if __name__ == "__main__":
    main()
