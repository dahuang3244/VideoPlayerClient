import struct
import enum
import time
from dataclasses import dataclass
from typing import Optional

class LogLevel(enum.IntEnum):
    INFO = 0
    DEBUG = 1
    WARNING = 2
    ERROR = 3
    FATAL = 4

@dataclass
class LogInfo:
    level: LogLevel
    timestamp: float  # Unix timestamp
    file_path: str
    line_number: int
    function_name: str
    content: str
    dump_data: Optional[bytes] = None

class LogSerializer:
    @staticmethod
    def _write_val(fmt: str, val) -> bytes:
        return struct.pack(fmt, val)

    @staticmethod
    def _write_str(s: str) -> bytes:
        # String encoding: Length (4B Big-Endian) + Data
        encoded = s.encode('utf-8')
        length = len(encoded)
        return struct.pack('>I', length) + encoded

    @staticmethod
    def _write_bytes(b: bytes) -> bytes:
        length = len(b)
        return struct.pack('>I', length) + b

    @staticmethod
    def serialize(info: LogInfo) -> bytes:
        """
        Serialize LogInfo to bytes according to the protocol:
        [Level(1)][Time(8)][File(Str)][Line(4)][Func(Str)][Content(Str)][HasDump(1)][DumpData(Str)?]

        Note: Internal integer fields are Big-Endian (>).
        """
        buffer = bytearray()

        # 1. Level (1 byte)
        buffer.extend(struct.pack('B', int(info.level)))

        # 2. Timestamp (8 bytes Big-Endian, milliseconds)
        # Convert float seconds to int64 milliseconds
        ts_ms = int(info.timestamp * 1000)
        buffer.extend(struct.pack('>q', ts_ms))

        # 3. File (String)
        buffer.extend(LogSerializer._write_str(info.file_path))

        # 4. Line (4 bytes Big-Endian)
        buffer.extend(struct.pack('>I', info.line_number))

        # 5. Function (String)
        buffer.extend(LogSerializer._write_str(info.function_name))

        # 6. Content (String)
        buffer.extend(LogSerializer._write_str(info.content))

        # 7. Dump Data
        if info.dump_data is not None:
            buffer.extend(struct.pack('B', 1)) # Has dump
            buffer.extend(LogSerializer._write_bytes(info.dump_data))
        else:
            buffer.extend(struct.pack('B', 0)) # No dump

        return bytes(buffer)
