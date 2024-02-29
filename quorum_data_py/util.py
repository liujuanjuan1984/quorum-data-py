import base64
import datetime
import hashlib
import io
import json
import logging
import math
import os
import uuid
import zipfile

import filetype
from PIL import Image

logger = logging.getLogger(__name__)

TRX_SIZE_LIMIT = 300  # kb, 每条trx的总大小上限，超出会被限制出块

CHUNK_SIZE = 200 * 1024  # bytes, 文件切割为多条trxs时，每条 trx 所包含的文件字节流上限


def check_publiched(published):
    if isinstance(published, (float, int)):
        published = int(str(published)[:10])
        dt = datetime.datetime.fromtimestamp(published, datetime.timezone.utc)
        published = dt.isoformat(timespec="seconds")
    else:
        try:
            dt = datetime.datetime.fromisoformat(
                published.replace("Z", "+00:00")
            )
            published = dt.isoformat(timespec="seconds")
        except Exception as e:
            raise ValueError(f"published format error: {published}") from e
    return published


def get_published_datetime(trx: dict):
    published = trx["Data"].get("published")
    if published:
        try:
            dt = datetime.datetime.strptime(published, "%Y-%m-%dT%H:%M:%S%z")
        except Exception:
            dt = datetime.datetime.strptime(published, "%Y-%m-%dT%H:%M:%S.%fZ")
        utc_offset = dt.utcoffset()
        if utc_offset is not None:
            utc_dt = dt - utc_offset
        else:
            utc_dt = dt.replace(tzinfo=datetime.timezone.utc)
    else:
        trx_ts = int(str(trx["TimeStamp"])[:10])
        utc_dt = datetime.datetime.utcfromtimestamp(trx_ts)
        utc_dt = utc_dt.replace(tzinfo=datetime.timezone.utc)
    return utc_dt


def read_file_to_bytes(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    return bytes_data


def zip_image(img, kb=TRX_SIZE_LIMIT):
    img_bytes = get_filebytes(img)
    guess_extension = filetype.guess(img_bytes).extension

    with io.BytesIO(img_bytes) as im:
        size = len(im.getvalue()) // 1024
        if size < kb:
            return img_bytes
        while size >= kb:
            img = Image.open(im)
            x, y = img.size
            out = img.resize((int(x * 0.95), int(y * 0.95)), Image.ANTIALIAS)
            im.close()
            im = io.BytesIO()
            try:
                out.save(im, "jpeg")
            except Exception as err:
                logger.info(err)
                out.save(im, guess_extension)
            size = len(im.getvalue()) // 1024
        return im.getvalue()


def pack_icon(icon):
    """icon: one image as file path, or bytes, or bytes-string."""
    img_bytes = zip_image(icon)
    icon = "".join(
        [
            "data:",
            filetype.guess(img_bytes).mime,
            ";base64,",
            base64.b64encode(img_bytes).decode("utf-8"),
        ]
    )
    return icon


def get_filebytes(img):
    if isinstance(img, str):
        if os.path.exists(img):
            file_bytes = read_file_to_bytes(img)
        else:
            file_bytes = base64.b64decode(img)
    elif isinstance(img, bytes):
        file_bytes = img
    else:
        raise TypeError(
            f"not support for type: {type(img)} and length: {len(img)}"
        )
    return file_bytes


def filename_init(path_bytes_string):
    if os.path.exists(path_bytes_string):
        file_name = os.path.basename(path_bytes_string)
    else:
        file_bytes = get_filebytes(path_bytes_string)
        extension = filetype.guess(file_bytes).extension
        name = f"{uuid.uuid4()}-{datetime.date.today()}"
        file_name = ".".join([name, extension])
    return file_name


def init_fileinfo(path_bytes_string, memo: str = None):
    file_bytes = get_filebytes(path_bytes_string)
    file_name = filename_init(path_bytes_string)
    try:
        mediaType = filetype.guess(file_bytes).mime
    except:
        mediaType = "text/plain"
    fileinfo = {
        "mediaType": mediaType,
        "name": file_name,
        "memo": memo or "",
        "title": os.path.splitext(file_name)[0],
        "sha256": hashlib.sha256(file_bytes).hexdigest(),
        "segments": [],
    }
    return file_bytes, fileinfo


def split_file_to_pieces(
    file_bytes, fileinfo: dict, chunk_kb: int = CHUNK_SIZE
):
    total_size = len(file_bytes)

    n = math.ceil(total_size / chunk_kb)
    pieces = []
    for i in range(n):
        ibytes = file_bytes[i * chunk_kb : (i + 1) * chunk_kb]
        trx_id = str(uuid.uuid4())
        fileinfo["segments"].append(
            {
                "id": f"seg-{i+1}",
                "trx_id": trx_id,
                "sha256": hashlib.sha256(ibytes).hexdigest(),
            }
        )
        pieces.append(
            {
                "name": f"seg-{i + 1}",
                "trx_id": trx_id,
                "content": base64.b64encode(ibytes).decode("utf-8"),
                "mediaType": "application/octet-stream",
            }
        )
    pieces.insert(
        0,
        {
            "name": "fileinfo",
            "trx_id": str(uuid.uuid4()),
            "content": json.dumps(fileinfo),
            "mediaType": "application/json",
        },
    )
    return pieces


def check_file(file_path: str):
    if not os.path.exists(file_path):
        raise ValueError("file not exists.")

    if not os.path.isfile(file_path):
        raise ValueError("not a file.")


def zip_file(file_path: str, to_zipfile=None, mode="w"):
    check_file(file_path)
    to_zipfile = to_zipfile or file_path + "_.zip"
    with zipfile.ZipFile(to_zipfile, mode, zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, arcname=os.path.basename(file_path))
    check_file(to_zipfile)
    return to_zipfile
