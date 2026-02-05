import sys
import time
import threading
import socket
import struct
import unittest
from unittest.mock import MagicMock

# Add src to path
sys.path.append('D:\\编程\\项目\\YiBoClient')

from src.core.log_info import LogInfo, LogLevel, LogSerializer
from src.core.logger import get_logger

class MockLogServer(threading.Thread):
    """
    A simple mock UDP server that mimics the YiboServer logger behavior.
    It receives RUDP packets and sends back ACKs.
    """
    def __init__(self, port=9000):
        super().__init__()
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind(('127.0.0.1', port))
        self.running = True
        self.received_logs = []

    def run(self):
        print(f"[MockServer] Listening on 127.0.0.1:{self.port}")
        while self.running:
            try:
                self.sock.settimeout(0.5)
                data, addr = self.sock.recvfrom(4096)

                # Parse RUDP Header: Seq (4B Big-Endian)
                if len(data) < 4:
                    continue

                seq = struct.unpack('>I', data[:4])[0]

                # Parse LogInfo (Just checking it's valid enough to decode)
                # Skip seq (4 bytes)
                payload = data[4:]

                # Store for verification
                self.received_logs.append({
                    'seq': seq,
                    'size': len(payload),
                    'raw': payload
                })

                # Send ACK: "ACK" + Seq (Big-Endian)
                ack = b'ACK' + struct.pack('>I', seq)
                self.sock.sendto(ack, addr)
                # print(f"[MockServer] Received Seq={seq}, Sent ACK")

            except socket.timeout:
                continue
            except OSError:
                break

    def stop(self):
        self.running = False
        self.sock.close()

def test_manual():
    print("Starting Manual Test...")

    # Start Mock Server
    server = MockLogServer()
    server.start()

    try:
        # Initialize Logger
        logger = get_logger()

        # Allow some time for threads to start
        time.sleep(0.5)

        print("Sending logs...")
        logger.info("Test Info Message")
        logger.debug("Test Debug Message")
        logger.error("Test Error Message")

        # Test binary dump
        binary_data = b'\x01\x02\x03\x04\xFF'
        logger.dump("Test Dump", binary_data)

        # Wait for transmission
        time.sleep(1.0)

        print(f"Server received {len(server.received_logs)} logs")

        # Verification
        assert len(server.received_logs) >= 4
        print("Test Passed!")

    finally:
        logger.stop()
        server.stop()
        server.join()

if __name__ == "__main__":
    test_manual()
