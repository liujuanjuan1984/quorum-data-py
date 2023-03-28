import base64
import datetime
import io
import logging
import os
import uuid
import zipfile

import filetype
from PIL import Image
from pygifsicle import gifsicle

logger = logging.getLogger(__name__)


# 每条 trx 有大小限制，否则会导致链异常；此为链端限定
IMAGE_MAX_SIZE_KB = 300  # kb, 每条trx中所包含的图片总大小限制
# 单条 trx 最多4 张图片；此为 rum app 客户端限定：第三方 app 调整该限定
IMAGE_MAX_NUM = 4
CHUNK_SIZE = 200 * 1024  # b, 文件切割为多条trxs时，每条 trx 所包含的文件字节流上限


def _filename_init(img):
    file_bytes, is_file = _get_filebytes(img)
    if is_file:
        file_name = os.path.basename(img).encode().decode("utf-8")
    else:
        extension = filetype.guess(file_bytes).extension
        name = f"{uuid.uuid4()}-{datetime.date.today()}"
        file_name = ".".join([name, extension])
    return file_name


def _zip_image_bytes(img_bytes, kb=IMAGE_MAX_SIZE_KB):
    """zip image bytes and return bytes; default changed to .jpeg"""

    kb = kb or IMAGE_MAX_SIZE_KB
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
                logger.debug(err)
                out.save(im, guess_extension)
            size = len(im.getvalue()) // 1024
        return im.getvalue()


def check_file(file_path):
    if not os.path.exists(file_path):
        raise ValueError(f"{file_path} file is not exists.")
    if not os.path.isfile(file_path):
        raise ValueError(f"{file_path} is not a file.")


def read_file_to_bytes(file_path):
    check_file(file_path)
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    return bytes_data


def zip_file(file_path, to_zipfile=None, mode="w"):
    check_file(file_path)
    to_zipfile = to_zipfile or file_path + "_.zip"
    with zipfile.ZipFile(to_zipfile, mode, zipfile.ZIP_DEFLATED) as zf:
        zf.write(file_path, arcname=os.path.basename(file_path))
    return to_zipfile


def zip_gif(gif, kb=IMAGE_MAX_SIZE_KB, cover=False):
    """压缩动图(gif)到指定大小(kb)以下

    gif: gif 格式动图本地路径
    kb: 指定压缩大小, 默认 200kb
    cover: 是否覆盖原图, 默认不覆盖

    返回压缩后图片字节. 该方法需要安装 gifsicle 软件和 pygifsicle 模块
    """
    kb = kb or IMAGE_MAX_SIZE_KB
    size = os.path.getsize(gif) / 1024
    if size < kb:
        return read_file_to_bytes(gif)

    destination = None
    if not cover:
        destination = f"{os.path.splitext(gif)[0]}-zip.gif"

    n = 0.9
    while size >= kb:
        gifsicle(
            gif,
            destination=destination,
            optimize=True,
            options=["--lossy=80", "--scale", str(n)],
        )
        if not cover:
            gif = destination
        size = os.path.getsize(gif) / 1024
        n -= 0.05

    return read_file_to_bytes(gif)


def _zip_image(img, kb=IMAGE_MAX_SIZE_KB):
    file_bytes, is_file = _get_filebytes(img)

    try:
        if filetype.guess(file_bytes).extension == "gif" and is_file:
            img_bytes = zip_gif(img, kb=kb, cover=False)
        else:
            img_bytes = _zip_image_bytes(file_bytes, kb=kb)
    except Exception as e:
        logger.warning("zip_image %s", e)
    return img_bytes


def pack_icon(icon):
    """icon: one image as file path, or bytes, or bytes-string."""

    img_bytes = _zip_image(icon)
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
    _size = len(img)
    is_file = False
    if isinstance(img, str):
        if os.path.exists(img):
            file_bytes = read_file_to_bytes(img)
            is_file = True
        else:
            file_bytes = base64.b64decode(img)
    elif isinstance(img, bytes):
        file_bytes = img
    else:
        raise TypeError(
            f"not support for type: {type(img)} and length: {_size}"
        )
    return file_bytes, is_file


def pack_imgs(images):
    kb = int(IMAGE_MAX_SIZE_KB // min(len(images), IMAGE_MAX_NUM))
    imgs = []
    for img in images[:IMAGE_MAX_NUM]:
        _bytes = _zip_image(img, kb)
        imgs.append(
            {
                "name": _filename_init(img),
                "mediaType": filetype.guess(_bytes).mime,
                "content": base64.b64encode(_bytes).decode("utf-8"),
                "type": "Image",
            }
        )
    return imgs


def pack_obj(content: str, images: list, name: str, post_id: str):
    content = content or ""
    images = images or []
    if not (content or images):
        raise ValueError("content and images are empty")
    if not isinstance(images, list):
        raise TypeError("images must be list")

    obj = {"type": "Note"}
    if content:
        obj["content"] = content
    if images:
        obj["image"] = pack_imgs(images)
    if name:
        obj["name"] = name
    obj["id"] = post_id or str(uuid.uuid4())
    return obj
