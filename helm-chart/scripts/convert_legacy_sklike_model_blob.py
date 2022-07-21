import json
import os
import shutil
import sys
from typing import Any, Optional

import accern_xyme

print(sys.argv)
if len(sys.argv) < 2:
    raise ValueError(
        "legacy model blob uri not found. Usage:\n"
        f"{sys.argv[0]} <LEGACY_MODEL_BLOB_URI> <XYME_HOST>")
MODEL_BLOB_URI = sys.argv[1]
XYME_HOST = sys.argv[2] if len(sys.argv) > 2 else "http://xyme-monitor:8080/"
XYME_SERVER_TOKEN = accern_xyme.XYMEClient.get_env_str("XYME_SERVER_TOKEN")
MODEL_VERSIONS_DIR = "versions"
INIT_MODEL_NAME = "init"
MODEL_NAME = "model.pkl"


def is_int(value: Any) -> bool:
    try:
        int(value)
        return True
    except ValueError:
        return False


def is_version_name(name: str) -> bool:
    if is_int(name) or name == INIT_MODEL_NAME:
        return True
    return False


def update_blob_dir(zipdirname: str) -> Optional[int]:
    latest_model_version = None
    for fname in os.listdir(zipdirname):
        to_path = None
        if is_version_name(fname):
            version = 0 if fname == INIT_MODEL_NAME else int(fname)
            if latest_model_version is None or version > latest_model_version:
                latest_model_version = version
            to_path = os.path.join(zipdirname, MODEL_VERSIONS_DIR)
        elif fname == MODEL_NAME:
            latest_model_version = 0
            to_path = os.path.join(
                zipdirname, MODEL_VERSIONS_DIR, INIT_MODEL_NAME)
        if to_path:
            from_path = os.path.join(zipdirname, fname)
            if not os.path.exists(to_path):
                os.makedirs(to_path, exist_ok=True)
            shutil.move(from_path, to_path)
    return latest_model_version


print(XYME_HOST, XYME_SERVER_TOKEN)
XYME = accern_xyme.create_xyme_client(XYME_HOST, XYME_SERVER_TOKEN)

print("Model blob uri", MODEL_BLOB_URI)

LEGACY_MODEL_BLOB = XYME.get_blob_handle(MODEL_BLOB_URI)
INFO_OBJ = LEGACY_MODEL_BLOB.get_info()
LEGACY_MODEL_VERSIONS = LEGACY_MODEL_BLOB.get_model_version()
ALL_VERSIONS = LEGACY_MODEL_VERSIONS["all_versions"]
if len(ALL_VERSIONS) > 0:
    print(
        f"Model blob: {MODEL_BLOB_URI} already converted. "
        f"Model versions available: {ALL_VERSIONS}")
else:
    LEGACY_MODEL_UUID = MODEL_BLOB_URI.split('/')[-1]
    COPIED_MODEL_UUID = f"b{XYME.get_uuid()}"
    COPIED_MODEL_URI = MODEL_BLOB_URI.replace(
        LEGACY_MODEL_UUID, COPIED_MODEL_UUID)
    COPIED_MODEL_BLOB = LEGACY_MODEL_BLOB.copy_to(COPIED_MODEL_URI)
    print(f"copied the old model blob to a new blob: {COPIED_MODEL_URI}")
    ZIP_FILENAME = f"/tmp/{LEGACY_MODEL_UUID}"
    ZIP_DIRNAME = f"{ZIP_FILENAME}_dir"
    LEGACY_MODEL_BLOB.download_zip(ZIP_FILENAME)

    shutil.unpack_archive(ZIP_FILENAME, ZIP_DIRNAME, "zip")

    LATEST_MODEL_VERSION = update_blob_dir(ZIP_DIRNAME)
    assert LATEST_MODEL_VERSION is not None
    INFO_OBJ["latest_model_version"] = LATEST_MODEL_VERSION
    INFO_OBJ["version_tags"] = None
    with open(os.path.join(ZIP_DIRNAME, "info.json"), "w") as f:
        obj = json.dumps(
            INFO_OBJ,
            sort_keys=True,
            indent=None,
            separators=(',', ':'))
        print(obj, file=f)

    NEW_ZIP_FILENAME = f"{ZIP_FILENAME}_new"
    shutil.make_archive(NEW_ZIP_FILENAME, 'zip', ZIP_DIRNAME)

    uploaded_handles = LEGACY_MODEL_BLOB.upload_zip(f"{NEW_ZIP_FILENAME}.zip")
    print(f"Uploaded model blob handles: {uploaded_handles}")
    shutil.rmtree(ZIP_DIRNAME)
