import time

# Message types
HELLO       = "HELLO"
HELLO_ACK   = "HELLO_ACK"
BYE         = "BYE"
MSG         = "MSG"
FILE_LIST   = "FILE_LIST"
FILE_LIST_ACK = "FILE_LIST_ACK"
FILE_REQ    = "FILE_REQ"
FILE_ACK    = "FILE_ACK"
FILE_CHUNK  = "FILE_CHUNK"
FILE_DONE   = "FILE_DONE"

def make_msg(from_name: str, text:str) -> dict:
    """Sent when a peer leaves."""
    return{
        "type" : BYE,
        "from" : from_name
    }
    
def make_file_list(files: list) -> dict:
    """
    Response to FILE_LIST request.
    files  → list of dicts: [{"name": "notes.pdf", "size": 204800}]
    """
    return{
        "type": FILE_LIST_ACK,
        "files": files
    }
    
def make_file_req(filename: str) -> dict:
    """Request to download a file from a peer."""
    return{
        "type" : FILE_REQ,
        "file" : filename
    }
    
def make_file_ack(filename:str, size:int, checksum: str) -> dict:
    """Sent before file chunks - tells receiver what to expect."""
    return {
        "type" : FILE_ACK,
        "file" : filename,
        "size" : size,
        "checksum" : checksum
    }
    
def make_file_done(filename: str) -> dict:
    """Sent after all chunks - signals transfer complete."""
    return{
        "type" : FILE_DONE,
        "file" : filename
    }