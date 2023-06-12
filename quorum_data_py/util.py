import datetime


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
