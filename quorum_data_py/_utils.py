import base64
import io
import json
import logging
import os
import uuid
import zipfile

import filetype
from PIL import Image

logger = logging.getLogger(__name__)


TRX_SIZE_LIMIT = 300  # kb, 每条trx的总大小上限，超出会被限制出块
IMAGE_NUM_LIMIT = 4  # 单条 trx 最多4 张图片；此为 rum app 限定：第三方 app 可调整该限定
CHUNK_SIZE = 280 * 1024  # bytes, 文件切割为多条trxs时，每条 trx 所包含的文件字节流上限


def read_file_to_bytes(file_path):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    return bytes_data


def zip_file(file_path, to_zipfile=None, mode="w"):
    if not os.path.exists(file_path):
        raise ValueError(f"{file_path} file is not exists.")
    if not os.path.isfile(file_path):
        raise ValueError(f"{file_path} is not a file.")
    to_zipfile = to_zipfile or file_path + "_.zip"
    with zipfile.ZipFile(to_zipfile, mode, zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, arcname=os.path.basename(file_path))
    return to_zipfile


def zip_image(img, kb=TRX_SIZE_LIMIT):
    img_bytes = _get_filebytes(img)
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


def _get_filebytes(img):
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


def pack_imgs(images: list, kb: int = TRX_SIZE_LIMIT):
    """
    打包图片为 feed 所需的数据格式。
    由于每个 trx 限定了 300kb 的大小，图片的大小需要根据已有 content 计算得出余量。
    """
    # check images size
    if len(images) == 0:
        raise ValueError("images is empty.")
    # 从图片字节转换为 base64string 大小会膨胀 1.33 左右
    bytes_limit = int(1024 * kb / 1.34)
    sizes = [len(_get_filebytes(i)) for i in images]
    total_size = sum(sizes)

    if total_size < bytes_limit:
        target_size = sizes
    else:
        target_size = [int(i * bytes_limit / total_size) for i in sizes]

    imgs = []
    for i, _img in enumerate(images):
        _bytes = zip_image(_img, target_size[i] // 1024)
        imgs.append(
            {
                "mediaType": filetype.guess(_bytes).mime,
                "content": base64.b64encode(_bytes).decode("utf-8"),
                "type": "Image",
            }
        )
    return imgs


def pack_obj(content: str, images: list, name: str, post_id: str):
    content = content or ""
    images = images or []
    images = images[:IMAGE_NUM_LIMIT]
    if not (content or images):
        raise ValueError("content and images are empty")
    if not isinstance(images, list):
        raise TypeError("images must be list")

    obj = {"type": "Note"}
    if content:
        obj["content"] = content
    if images:
        kb = TRX_SIZE_LIMIT - int(len(json.dumps(obj)) // 1024) - 1
        obj["image"] = pack_imgs(images, kb)
    if name:
        obj["name"] = name
    obj["id"] = post_id or str(uuid.uuid4())
    return obj
