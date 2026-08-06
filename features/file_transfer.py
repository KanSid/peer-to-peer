import os
import socket
import hashlib
from config import CHUNK_SIZE, SHARED_DIR, DOWNLOAD_DIR
from features.protocol import make_file_ack, make_file_done, make_file_req, FILE_ACK, FILE_CHUNK, FILE_DONE
from utils.framing import encode_message, decode_message
from utils.crypto import encrypt_message, decrypt_message


def get_checksum(filepath: str) -> str:
    """MD5 checksum of a file."""
    md5 = hashlib.md5()
    with open(filepath, "rb") as f:
        while chunk := f.read(CHUNK_SIZE):
            md5.update(chunk)
    return md5.hexdigest()


def send_file(ip: str, port: int, filename: str, key: bytes) -> bool:
    """
    Sends a file to a peer.
    1. Sends FILE_ACK with metadata
    2. Sends raw chunks
    3. Sends FILE_DONE
    """
    filepath = os.path.join(SHARED_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[FileTransfer] File not found: {filepath}")
        return False

    size = os.path.getsize(filepath)
    checksum = get_checksum(filepath)

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(10.0)
            s.connect((ip, port))

            # Send FILE_ACK with metadata
            ack = make_file_ack(filename, size, checksum)
            encrypted = encrypt_message(ack, key)
            s.sendall(encode_message({"payload": encrypted}))

            # Send file in chunks
            with open(filepath, "rb") as f:
                while chunk := f.read(CHUNK_SIZE):
                    s.sendall(chunk)

            # Send FILE_DONE
            done = make_file_done(filename)
            encrypted = encrypt_message(done, key)
            s.sendall(encode_message({"payload": encrypted}))

            print(f"[FileTransfer] Sent {filename} to {ip}")
            return True

    except Exception as e:
        print(f"[FileTransfer] Send failed: {e}")
        return False


def receive_file(conn: socket.socket, key: bytes) -> bool:
    """
    Receives a file from a connected peer.
    1. Reads FILE_ACK for metadata
    2. Reads raw chunks until FILE_DONE
    3. Verifies checksum
    """
    try:
        # Read FILE_ACK
        raw = decode_message(conn)
        if raw is None:
            return False

        msg = decrypt_message(raw.get("payload", ""), key)
        if msg is None or msg.get("type") != FILE_ACK:
            return False

        filename = msg["file"]
        expected_size = msg["size"]
        expected_checksum = msg["checksum"]

        filepath = os.path.join(DOWNLOAD_DIR, filename)
        received = 0

        with open(filepath, "wb") as f:
            while received < expected_size:
                remaining = expected_size - received
                chunk = conn.recv(min(CHUNK_SIZE, remaining))
                if not chunk:
                    break
                f.write(chunk)
                received += len(chunk)

        # Verify checksum
        actual_checksum = get_checksum(filepath)
        if actual_checksum != expected_checksum:
            print(f"[FileTransfer] Checksum mismatch for {filename}")
            os.remove(filepath)
            return False

        print(f"[FileTransfer] Received {filename} successfully")
        return True

    except Exception as e:
        print(f"[FileTransfer] Receive failed: {e}")
        return False


def list_shared_files() -> list:
    """Returns list of files available in shared/ folder."""
    if not os.path.exists(SHARED_DIR):
        return []
    return [
        {"name": f, "size": os.path.getsize(os.path.join(SHARED_DIR, f))}
        for f in os.listdir(SHARED_DIR)
        if os.path.isfile(os.path.join(SHARED_DIR, f))
    ]