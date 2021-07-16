import logging
import os
from zipfile import ZipFile, ZIP_DEFLATED


def unzip_file(origin_local_path: str, dst_local_path: str, delete_zip_file: bool):
    logging.info(f"extracting {origin_local_path} to {dst_local_path}")

    with ZipFile(origin_local_path) as input_zip:
        input_zip.extractall(path=dst_local_path)

    if delete_zip_file:
        os.remove(origin_local_path)


def _zip_file(z: ZipFile, f: str, delete_files: bool):
    logging.info(f"zipping {f}")
    z.write(f, os.path.basename(f))
    if delete_files:
        os.remove(f)


def zip_file(dst_local_path: str, files, delete_files: bool):
    logging.info(f"zipping files to {dst_local_path}")
    with ZipFile(dst_local_path, "w", compression=ZIP_DEFLATED, compresslevel=9) as z:
        if isinstance(files, str):
            _zip_file(z, files, delete_files)
        else:
            [_zip_file(z, f, delete_files) for f in files]
