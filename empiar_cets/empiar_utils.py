import json
from pathlib import Path
from typing import List
from fs.ftpfs import FTPFS
from pydantic import BaseModel, Field
import rich
import parse
import struct


class EMPIARFile(BaseModel, frozen=True):
    path: Path
    size_in_bytes: int


class EMPIARFileList(BaseModel):

    files: List[EMPIARFile]


def get_files_matching_pattern(
        file_list: EMPIARFileList, 
        file_pattern: str
) -> list[str]:

    selected_file_references = []
    for file in file_list.files:
        result = parse.parse(file_pattern, str(file.path))
        if result is not None:
            selected_file_references.append(str(file.path))
    rich.print(f"Found {len(selected_file_references)} file references matching pattern {file_pattern}")

    return selected_file_references


def get_list_of_empiar_files(accession_no: str) -> EMPIARFileList:

    ftp_fs = FTPFS('ftp.ebi.ac.uk')
    root_path = f"/empiar/world_availability/{accession_no}/data"
    walker = ftp_fs.walk(root_path)

    empiar_files = []

    for path, dirs, files in walker:
        for file in files:
            relpath = Path(path).relative_to(root_path)
            empiar_file = EMPIARFile(
                path=relpath/file.name,
                size_in_bytes=file.size
            )
            empiar_files.append(empiar_file)

    return EMPIARFileList(files=empiar_files)


def get_files_for_empiar_entry_cached(
        accession_id: str
) -> EMPIARFileList:
    
    #FIXME - do the caching properly, use a separately configurable path
    cache_dirpath = Path(f"local-data/{accession_id}/cache")
    cache_dirpath.mkdir(exist_ok=True, parents=True)
    file_list_fpath = cache_dirpath / "all_files.json"

    accession_no = accession_id.split("-")[1]

    if file_list_fpath.exists():
        with open(file_list_fpath) as fh:
            model_data = json.load(fh)
            list_of_files = EMPIARFileList.model_validate(model_data) # type: ignore
    else:
        list_of_files = get_list_of_empiar_files(accession_no)
        with open(file_list_fpath, "w") as fh:
            model_json_str = list_of_files.model_dump_json(indent=2) # type: ignore
            fh.write(model_json_str)

    return list_of_files


def read_mrc_header_pyfs(filepath):

    ftp_url = 'ftp.ebi.ac.uk'

    # Open FTP filesystem
    with FTPFS(ftp_url) as ftp_fs:
        # Open file and read only the first 1024 bytes (header)
        with ftp_fs.open(filepath, 'rb') as f:
            header_data = f.read(1024)
    
    # Parse MRC header - first 40 bytes contain key info
    # Format: nx, ny, nz, mode, nxstart, nystart, nzstart, mx, my, mz
    header_ints = struct.unpack('<10i', header_data[:40])
    
    # Extract more header info
    # Bytes 40-52: cell dimensions (3 floats)
    cell_dims = struct.unpack('<3f', header_data[40:52])
    
    # Bytes 52-64: cell angles (3 floats) 
    cell_angles = struct.unpack('<3f', header_data[52:64])
    
    return {
        'dimensions': header_ints[:3],  # nx, ny, nz
        'mode': header_ints[3],         # data type
        'cell_dimensions': cell_dims,
        'cell_angles': cell_angles
        # Add more fields as needed
    }

