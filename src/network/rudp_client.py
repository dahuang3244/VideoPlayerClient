import socket
import struct
import time
import sys

class RUDPClient:
    def __init__(self, host: str = '127.0.0.1', port: int = 9000, timeout: float = 1.0, max_retries: int = 5):
        self.server_addr = (host, port)
        self.timeout = timeout
        self.max_retries = max_retries
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.settimeout(timeout)

    def send_log(self, seq: int, log_data: bytes) -> bool:
        """
        Send log data reliably using RUDP.
        Packet Format: [Seq(4B Big-Endian)][LogData...]
        Ack Format: [ACK(3B)][Seq(4B Big-Endian)]
        """
        # Construct packet: Seq (Big-Endian) + Data
        packet = struct.pack('>I', seq) + log_data

        for attempt in range(self.max_retries):
            try:
                # Send
                self.sock.sendto(packet, self.server_addr)

                # Wait for ACK
                ack_data, _ = self.sock.recvfrom(1024)

                # Verify ACK
                # Expected size: 3 ("ACK") + 4 (Seq) = 7 bytes
                if len(ack_data) == 7 and ack_data[:3] == b'ACK':
                    ack_seq = struct.unpack('>I', ack_data[3:7])[0]
                    if ack_seq == seq:
                        return True # Success

            except socket.timeout:
                continue # Retry on timeout
            except Exception as e:
                # Log to stderr on socket error but don't crash
                sys.stderr.write(f"[RUDP] Socket error: {e}\n")
                return False

        return False # Failed after retries

    def close(self):
        if self.sock:
            self.sock.close()
