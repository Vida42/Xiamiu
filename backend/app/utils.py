from datetime import datetime


def convert_datetime_to_iso8601(dt: datetime) -> str:
    """
    Convert datetime objects to ISO 8601 formatted strings.
    """
    if isinstance(dt, datetime):
        return dt.isoformat()
    return dt
