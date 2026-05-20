from operations.files import pair_files
from src.config import parameters

REASONED_ANALYSIS = parameters.REASONED_ANALYSIS
PRODUCTIVITY_ANALYSIS = parameters.PRODUCTIVITY_ANALYSIS
CONTACT_ANALYSIS = parameters.CONTACT_ANALYSIS
BACKLOG_ANALYSIS = parameters.BACKLOG_ANALYSIS
BACKLOG_ONNET_ANALYSIS = parameters.BACKLOG_ONNET_ANALYSIS
MIGRATIONS_ANALYSIS = parameters.MIGRATIONS_ANALYSIS

FTTH_HFC_CAPACITY_FOLDER = parameters.FTTH_HFC_FOLDER / "Area de Capacidades"
FTTH_HFC_DISPATCH_FOLDER = parameters.FTTH_HFC_FOLDER / "Area de Despacho"

if __name__ == "__main__":
    file_paths = pair_files(
        dir1=FTTH_HFC_CAPACITY_FOLDER,
        dir2=FTTH_HFC_DISPATCH_FOLDER,
        date_format_dir1="dmy",
        date_format_dir2="mdy",
    )
    print(len(file_paths.pairs))
    print(file_paths.unpaired_dir1)
    print(file_paths.unpaired_dir2)
