"""
数据结构转换

把 解密后的 trx （通过 get content api 所获得的 trx）转换成新版的 trx data 和 timestamp 等，用来重新发布上链
"""
from quorum_mininode_py.crypto.account import public_key_to_address


def from_new_chain(trx: dict):
    """
    把新共识版本的 trx 还原为 trx data 和 timestamp，
    然后通过轻节点的 post to group api 发送上链
    适用场景：把链 a 的 trx 发送到 链 b
    保留原有 trx_id 是为了继承此前所产生的交互数据
    """
    if isinstance(trx.get("Data"), str):
        raise ValueError("trx is encrypted.")
    new = {
        "data": trx.get("Content") or trx.get("Data"),
        "timestamp": trx["TimeStamp"],
        "trx_id": trx["TrxId"],
    }
    return new


def from_old_chain(trx: dict):
    """
    把旧共识版本的 trx 转换成新版的 trx data 和 timestamp，
    然后通过轻节点的 post to group api 发送上链
    适用场景：把旧链的 trxs 发送到新链
    """
    if isinstance(trx.get("Data"), str):
        raise ValueError("trx is encrypted.")

    typeurl = trx.get("TypeUrl")
    pubkey = trx.get("Publisher") or trx.get("SenderPubkey")

    contentobj = trx.get("Content") or trx.get("Data") or {}

    obj = None
    if typeurl == "quorum.pb.Person":
        address = public_key_to_address(pubkey)
        obj = {
            "type": "Create",
            "object": {
                "type": "Profile",
                "describes": {"type": "Person", "id": address},
            },
        }
        name = contentobj.get("name", "")
        if name:
            obj["object"]["name"] = name

        image = contentobj.get("image")
        if image:
            obj["object"]["image"] = [
                {
                    "mediaType": image["mediaType"],
                    "content": image["content"],
                    "type": "Image",
                }
            ]

    elif typeurl == "quorum.pb.Object":
        imgs = contentobj.get("image")
        if imgs:
            _temp_imgs = []
            for img in imgs:
                if img.get("type") != "Image":
                    img["type"] = "Image"
                _temp_imgs.append(img)
            contentobj["image"] = _temp_imgs

        content_type = contentobj.get("type")
        if content_type in ["Like", "Dislike"]:
            obj = {
                "type": content_type,
                "object": {"type": "Note", "id": contentobj.get("id")},
            }
        else:
            contentobj["id"] = trx.get("TrxId")
            if "inreplyto" in contentobj:
                contentobj["inreplyto"] = {
                    "type": "Note",
                    "id": contentobj["inreplyto"]["trxid"],
                }
            obj = {"type": "Create", "object": contentobj}

    new = {"data": obj, "timestamp": trx.get("TimeStamp")}
    return new
