import hashlib


def hash_str_to_int(text: str, N: int = 3):
    """Hash a string into an N-byte integer

    This method is used e.g. to convert the four-word style game identifiers into
    a database-friendly integer.
    """

    hash_obj = hashlib.md5(text.encode())
    hash_bytes = list(hash_obj.digest())

    # Slice off the first N bytes and cast to integer
    return int.from_bytes(hash_bytes[0:N], "big")
