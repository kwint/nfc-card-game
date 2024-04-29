import uuid


def short_uuid() -> str:
    return str(uuid.uuid4())[:8]
