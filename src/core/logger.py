import os
import sys
import time
import queue
import threading
import inspect
from typing import Optional
from pathlib import Path

from src.core.log_info import LogInfo, LogLevel, LogSerializer
from src.network.rudp_client import RUDPClient

class Logger:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(Logger, cls).__new__(cls)
                cls._instance._initialized = False
            return cls._instance

    def __init__(self):
        with Logger._lock:
            if self._initialized:
                return
            self._initialized = True

        # Configuration
        self.host = os.environ.get('YIBO_LOG_IP', '127.0.0.1')
        self.port = int(os.environ.get('YIBO_LOG_PORT', 9000))

        # Queue and Worker
        self.queue = queue.Queue(maxsize=10000)
        self.running = True
        self.seq_counter = 0

        # Start worker thread
        self.worker_thread = threading.Thread(target=self._worker_loop, name="LogWorker", daemon=True)
        self.worker_thread.start()

    def _worker_loop(self):
        # Initialize client in worker thread to be safe
        client = RUDPClient(self.host, self.port)

        while self.running:
            try:
                # Get log info from queue
                info = self.queue.get(timeout=1.0)

                # Serialize
                data = LogSerializer.serialize(info)

                # Send
                success = client.send_log(self.seq_counter, data)

                if not success:
                    # Fallback to stderr if RUDP fails
                    self._fallback_log(info, "No ACK")

                self.seq_counter = (self.seq_counter + 1) & 0xFFFFFFFF # Wrap around 32-bit

            except queue.Empty:
                continue
            except Exception as e:
                sys.stderr.write(f"[Logger] Worker error: {e}\n")

        client.close()

    def _fallback_log(self, info: LogInfo, reason: str):
        """Fallback logging when network fails"""
        timestamp_str = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(info.timestamp))
        sys.stderr.write(f"[LOG FALLBACK][{reason}] [{timestamp_str}] [{info.level.name}] {info.content}\n")

    def _push_log(self, level: LogLevel, content: str, dump_data: Optional[bytes] = None):
        if not self.running:
            return

        # Capture call stack
        # 0: _push_log, 1: info/debug/etc, 2: caller
        try:
            stack = inspect.stack()
            if len(stack) >= 3:
                frame = stack[2]
                file_path = os.path.basename(frame.filename)
                line_number = frame.lineno
                function_name = frame.function
            else:
                file_path = "unknown"
                line_number = 0
                function_name = "unknown"
        except Exception:
            file_path = "unknown"
            line_number = 0
            function_name = "unknown"

        info = LogInfo(
            level=level,
            timestamp=time.time(),
            file_path=file_path,
            line_number=line_number,
            function_name=function_name,
            content=content,
            dump_data=dump_data
        )

        try:
            self.queue.put_nowait(info)
        except queue.Full:
            sys.stderr.write("[Logger] Queue full, dropping log\n")

    # Public API

    def info(self, msg: str):
        self._push_log(LogLevel.INFO, msg)

    def debug(self, msg: str):
        self._push_log(LogLevel.DEBUG, msg)

    def warning(self, msg: str):
        self._push_log(LogLevel.WARNING, msg)

    def error(self, msg: str):
        self._push_log(LogLevel.ERROR, msg)

    def fatal(self, msg: str):
        self._push_log(LogLevel.FATAL, msg)

    def dump(self, msg: str, data: bytes):
        self._push_log(LogLevel.INFO, msg, data)

    def stop(self):
        self.running = False
        if self.worker_thread.is_alive():
            self.worker_thread.join(timeout=2.0)

# Global Instance Access
_logger_instance = None

def get_logger():
    global _logger_instance
    if _logger_instance is None:
        _logger_instance = Logger()
    return _logger_instance
