"""Data structure recommendations in Quorum. For webapp Feed, Port and RumApp"""

import base64
import json
import logging
import uuid

import filetype

from quorum_data_py import util

logger = logging.getLogger(__name__)

IMAGE_NUM_LIMIT = 4  # 单条 trx 最多4 张图片；此为 rum app 限定：第三方 app 可调整该限定


def add_published(data: dict, published):
    """
    published: timestamp int or ISO format string
    e.g. 2020-01-01T00:00:00Z, 2023-04-04T10:31:45+08:00
    """
    data["published"] = util.check_publiched(published)
    return data


def add_origin(data: dict, origin_name, origin_type=None):
    origin_type = origin_type or "Application"
    if origin_type not in ["Application", "Service"]:
        logger.warning("origin_type should be 'Application' or 'Service'")
    data["origin"] = {"type": origin_type, "name": origin_name}
    return data


def new_post(
    content: str = None,
    images: list = None,
    post_id: str = None,
    name: str = None,
):
    """Creates a new post."""
    return {
        "type": "Create",
        "object": pack_obj(content, images, name, post_id),
    }


def del_post(post_id: str):
    """Deletes a post."""
    return {"type": "Delete", "object": {"type": "Note", "id": post_id}}


def edit_post(
    content: str = None,
    images: list = None,
    post_id: str = None,
    name: str = None,
):
    """Edits an existing post."""
    content_obj = pack_obj(content, images, name, post_id)
    del content_obj["id"]
    return {
        "type": "Update",
        "object": {
            "type": "Note",
            "id": post_id,
        },
        "result": content_obj,
    }


def reply(
    reply_id: str,
    content: str = None,
    images: list = None,
    post_id: str = None,
    name: str = None,
):
    """Replies to an existing post.
    reply_id: the post_id to reply to"""
    content_obj = pack_obj(content, images, name, post_id)
    content_obj["inreplyto"] = {"type": "Note", "id": reply_id}
    return {"type": "Create", "object": content_obj}


def like(post_id: str):
    """Likes a post."""
    return {"type": "Like", "object": {"type": "Note", "id": post_id}}


def undo_like(post_id: str):
    """Cancels a post like."""
    return {
        "type": "Undo",
        "object": {
            "type": "Like",
            "object": {"type": "Note", "id": post_id},
        },
    }


def dislike(post_id: str):
    """Disikes a post."""
    return {"type": "Dislike", "object": {"type": "Note", "id": post_id}}


def undo_dislike(post_id: str):
    """Cancels a post dislike."""
    return {
        "type": "Undo",
        "object": {
            "type": "Dislike",
            "object": {"type": "Note", "id": post_id},
        },
    }


def profile(name: str = None, avatar: str = None, addr: str = None):
    """Update profile of user."""
    if not (name or avatar):
        raise ValueError("name and avatar are empty")
    profile_obj = {
        "type": "Profile",
        "describes": {"type": "Person", "id": addr},
    }
    if name:
        profile_obj["name"] = name
    if avatar:
        profile_obj["image"] = pack_imgs([avatar])
    return {"type": "Create", "object": profile_obj}


def follow_user(addr: str):
    """Follow a user."""
    return {
        "type": "Follow",
        "object": {
            "type": "Person",
            "id": addr,
        },
    }


def unfollow_user(addr: str):
    """Unfollow a user"""
    return {
        "type": "Undo",
        "object": {
            "type": "Follow",
            "object": {"type": "Person", "id": addr},
        },
    }


def block_user(addr: str):
    """Block a user."""
    return {
        "type": "Block",
        "object": {"type": "Person", "id": addr},
    }


def unblock_user(addr: str):
    """Unlock a user."""
    return {
        "type": "Undo",
        "object": {
            "type": "Block",
            "object": {"type": "Person", "id": addr},
        },
    }


def group_icon(icon: str):
    """Init group icon as appconfig"""
    return {
        "name": "group_icon",
        "_type": "string",
        "value": util.pack_icon(icon),
        "action": "add",
        "memo": "init group icon",
    }


def group_desc(desc: str):
    """Init group description as appconfig"""
    return {
        "name": "group_desc",
        "_type": "string",
        "value": desc,
        "action": "add",
        "memo": "init group desc",
    }


def group_announcement(announcement: str):
    """Init group announcement as appconfig"""
    return {
        "name": "group_announcement",
        "_type": "string",
        "value": announcement,
        "action": "add",
        "memo": "init group announcement",
    }


def group_default_permission(default_permission: str):
    """Init group default permission as appconfig
    default_permission: WRITE or READ"""
    if default_permission.upper() not in ["WRITE", "READ"]:
        raise ValueError("default_permission must be one of these: WRITE,READ")
    return {
        "name": "group_default_permission",
        "_type": "string",
        "value": default_permission.upper(),
        "action": "add",
        "memo": "init group default permission",
    }


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
        kb = util.TRX_SIZE_LIMIT - int(len(json.dumps(obj)) // 1024) - 1
        obj["image"] = pack_imgs(images, kb)
    if name:
        obj["name"] = name
    obj["id"] = post_id or str(uuid.uuid4())
    return obj


def pack_imgs(images: list, kb: int = util.TRX_SIZE_LIMIT):
    """
    打包图片为 feed 所需的数据格式。
    由于每个 trx 限定了 300kb 的大小，图片的大小需要根据已有 content 计算得出余量。
    """
    # check images size
    if len(images) == 0:
        raise ValueError("images is empty.")
    # 从图片字节转换为 base64string 大小会膨胀 1.33 左右
    bytes_limit = int(1024 * kb / 1.34)
    sizes = [len(util.get_filebytes(i)) for i in images]
    total_size = sum(sizes)

    if total_size < bytes_limit:
        target_size = sizes
    else:
        target_size = [int(i * bytes_limit / total_size) for i in sizes]

    imgs = []
    for i, _img in enumerate(images):
        _bytes = util.zip_image(_img, target_size[i] // 1024)
        imgs.append(
            {
                "mediaType": filetype.guess(_bytes).mime,
                "content": base64.b64encode(_bytes).decode("utf-8"),
                "type": "Image",
            }
        )
    return imgs
