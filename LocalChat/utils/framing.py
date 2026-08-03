import json

HEADER_SIZE = 4

def encode_message(data: dict) -> bytes:
    """
    Convert a dict to bytes with a 4 byte length prefix.This is what we send over TCP 
    """

    json_bytes = json.dumps(data).encode("utf-8")
    length = len(json_bytes)
    header = length.to_bytes(HEADER_SIZE, byteorder="big")
    return header + json_bytes

def decode_message(sock) -> dict:
    """
    Read one complete message from a TCP socket.
    First reads 4 byte header to know message length
    Then reads exactly that many bytes
    Returns the decoded dict or None if connection closed
    """
    try:
        header = _recv_exact(sock, HEADER_SIZE)
        if header is None:
            return None

        length = int.from_bytes(header, byteorder="big")
        json_bytes = _recv_exact(sock, length)
        if json_bytes is None:
            return None

        return json.loads(json_bytes.decode("utf-8"))

    except Exception:
        return None

def _recv_exact(sock, num_bytes: int) -> bytes:
    """
    Keep reading form socket until we have exactly num_bytes.
    TCP may deliver data in small chunks so we loop until done.
    """

    data = b""
    while len(data) < num_bytes:
        chunk = sock.recv(num_bytes - len(data))
        if not chunk:
            return None
        data += chunk
    return data


