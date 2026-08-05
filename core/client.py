import socket
import json
from utils.framing import encode_message
from utils.crypto import encrypt_message


class Client:
    def __init__(self, key: bytes):
        """
        key → AES key derived from room code
        """
        self.key = key

    def send(self, ip: str, port: int, payload: dict) -> bool:
        """
        Encrypts and sends a message to a specific peer.
        Returns True if successful, False if connection failed.
        """
        try:
            encrypted = encrypt_message(payload, self.key)
            msg = {"payload": encrypted}
            data = encode_message(msg)

            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(5.0)
                s.connect((ip, port))
                s.sendall(data)
            return True

        except Exception as e:
            print(f"[Client] Failed to send to {ip}:{port} — {e}")
            return False

    def broadcast(self, peers: dict, payload: dict):
        """
        Sends a message to all known peers.
        peers → dict from PeerManager.get_peers()
        """
        for ip, info in peers.items():
            self.send(ip, info["port"], payload)