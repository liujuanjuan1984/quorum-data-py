"""Data structure recommendations in Quorum. For webapp Feed, Port and RumApp"""

import logging

from quorum_data_py import util
from quorum_data_py._utils import pack_icon, pack_imgs, pack_obj

logger = logging.getLogger(__name__)


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
        "value": pack_icon(icon),
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
