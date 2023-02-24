import logging

from quorum_data_py._utils import pack_icon, pack_imgs, pack_obj

logger = logging.getLogger(__name__)


class FeedData:
    """适用于 quorum 的 feed、port 和 rum app 的推荐数据结构"""

    @classmethod
    def new_post(
        cls,
        content: str = None,
        images: list = None,
        post_id: str = None,
        name: str = None,
    ):
        return {
            "type": "Create",
            "object": pack_obj(content, images, name, post_id),
        }

    @classmethod
    def del_post(cls, post_id):
        return {"type": "Delete", "object": {"type": "Note", "id": post_id}}

    @classmethod
    def edit_post(
        cls,
        content: str = None,
        images: list = None,
        post_id: str = None,
        name: str = None,
    ):
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

    @classmethod
    def reply(
        cls,
        content: str,
        images: list,
        reply_id: str,
        post_id: str = None,
        name: str = None,
    ):
        content_obj = pack_obj(content, images, name, post_id)
        content_obj["inreplyto"] = {"type": "Note", "id": reply_id}
        return {"type": "Create", "object": content_obj}

    @classmethod
    def like(cls, post_id: str):
        return {"type": "Like", "object": {"type": "Note", "id": post_id}}

    @classmethod
    def undo_like(cls, post_id: str):
        return {
            "type": "Undo",
            "object": {
                "type": "Like",
                "object": {"type": "Note", "id": post_id},
            },
        }

    @classmethod
    def dislike(cls, post_id: str):
        return {"type": "Dislike", "object": {"type": "Note", "id": post_id}}

    @classmethod
    def undo_dislike(cls, post_id: str):
        return {
            "type": "Undo",
            "object": {
                "type": "Dislike",
                "object": {"type": "Note", "id": post_id},
            },
        }

    @classmethod
    def profile(cls, name: str, avatar: str, addr: str):
        """update profile of user"""
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

    @classmethod
    def follow_user(cls, addr: str):
        return {
            "type": "Follow",
            "object": {
                "type": "Person",
                "id": addr,
            },
        }

    @classmethod
    def unfollow_user(cls, addr: str):
        return {
            "type": "Undo",
            "object": {
                "type": "Follow",
                "object": {"type": "Person", "id": addr},
            },
        }

    @classmethod
    def block_user(cls, addr: str):
        return {
            "type": "Block",
            "object": {"type": "Person", "id": addr},
        }

    @classmethod
    def unblock_user(cls, addr: str):
        return {
            "type": "Undo",
            "object": {
                "type": "Block",
                "object": {"type": "Person", "id": addr},
            },
        }

    @classmethod
    def group_icon(cls, icon: str):
        """init group icon as appconfig"""
        return {
            "name": "group_icon",
            "_type": "string",
            "value": pack_icon(icon),
            "action": "add",
            "memo": "init group icon",
        }

    @classmethod
    def group_desc(cls, desc: str):
        """init group description as appconfig"""
        return {
            "name": "group_desc",
            "_type": "string",
            "value": desc,
            "action": "add",
            "memo": "init group desc",
        }

    @classmethod
    def group_announcement(cls, announcement: str):
        """init group announcement as appconfig"""
        return {
            "name": "group_announcement",
            "_type": "string",
            "value": announcement,
            "action": "add",
            "memo": "init group announcement",
        }

    @classmethod
    def group_default_permission(cls, default_permission: str):
        """init group default permission as appconfig
        default_permission: WRITE or READ"""
        if default_permission.upper() not in ["WRITE", "READ"]:
            raise ValueError(
                "default_permission must be one of these: WRITE,READ"
            )
        return {
            "name": "group_default_permission",
            "_type": "string",
            "value": default_permission.upper(),
            "action": "add",
            "memo": "init group default permission",
        }
