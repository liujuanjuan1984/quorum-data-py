def get_trx_type(trx: dict):
    """
    获取 trx 的类型，和 rum-feed js 的定义保持一致。
    https://github.com/okdaodine/rum-feed/blob/main/server/utils/getTrxType.js
    返回结果：
    unknown/post/comment/counter/profile/delete/relation/wallet
    """
    data = trx.get("Data") or trx.get("Content")  # 兼容新旧链
    if not data or isinstance(data, str):
        raise ValueError("trx is encrypted.")

    out_type = data.get("type")
    inner_type = data.get("object", {}).get("type")
    trx_type = "unknown"
    if out_type == "Create":
        if inner_type == "Note":
            inreplyto = data.get("object", {}).get("inreplyto")
            if not inreplyto:
                trx_type = "post"
            elif inreplyto.get("type") == "Note":
                trx_type = "comment"
        elif inner_type == "Profile":
            trx_type = "profile"
    elif out_type == "Like" or (out_type == "Undo" and inner_type == "Like"):
        trx_type = "counter"
    elif out_type == "Delete" and inner_type == "Note":
        trx_type = "delete"
    elif out_type in ["Follow", "Block"] or (
        out_type == "Undo" and inner_type in ["Follow", "Block"]
    ):
        trx_type = "relation"
    elif out_type == "Announce" and data.get("name").find("private key") != -1:
        trx_type = "wallet"
    return trx_type
