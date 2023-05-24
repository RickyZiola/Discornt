from itertools import count

class data_decoder(object):
    payload: bytes
    current: int
    
    def __init__(self, payload: bytes):
        self.payload = payload
        self.current = 0
        
    def read_bytes(self, size: int) -> bytes:
        end = self.current + size
        if end > len(self.payload):
            raise IndexError("Attempting to read more bytes than available")
        try:
            return self.payload[self.current:end]
        finally:
            self.current = end
    
    def read_byte(self) -> int:
        return self.read_bytes(1)[0]
        
    def read_var_int(self, max_size_bits: int | None = None) -> int:
        value: int = 0
        for i in count():
            byte: int = self.read_byte()
            value |= (byte & 0x7F) << (i * 7)
            
            if byte & 0x80 == 0x00: break
            
            if max_size_bits != None and i * 7 > max_size_bits:
                raise ValueError("Variable-length integer too large")
        
        return value
    
    def read_string(self) -> str:
        size = self.read_byte()
        return "".join([chr(c) for c in self.read_bytes(size)])
        
class data_encoder(object):
    payload: bytes
    
    def __init__(self):
        self.payload = bytes(0)
    
    def write_bytes(self, data: bytes):
        self.payload += data
    
    def write_byte(self, value: int):
        self.write_bytes(bytes([value]))
    
    def write_var_int(self, value: int):
        for i in count():
            if (value >> (7*i)) & ((2**64-1) << 7) == 0:
                self.write_byte(value >> (7*i))
                break 
            self.write_byte(0x80 | ((value >> (7*i)) & 0x7F))
        return
    
    def write_string(self, value: str):
        self.write_byte(len(value))
        self.write_bytes(bytes([ord(c) for c in value]))
            