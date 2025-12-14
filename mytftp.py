import socket
import sys
import struct

TFTP_PORT = 69
TIMEOUT = 5
BLOCK_SIZE = 512

def send_rrq(sock, server, filename):
    rrq = struct.pack("!H", 1) + filename.encode() + b'\x00octet\x00'
    sock.sendto(rrq, server)
    print("RRQ 패킷 전송 완료")

def do_get(server_ip, filename):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(TIMEOUT)

    server = (server_ip, TFTP_PORT)
    send_rrq(sock, server, filename)

    expected_block = 1

    with open(filename, "wb") as f:
        while True:
            try:
                data, addr = sock.recvfrom(516)
            except socket.timeout:
                print("서버 응답 없음 (timeout)")
                break

            opcode = struct.unpack("!H", data[:2])[0]

            if opcode == 3:  # DATA
                block = struct.unpack("!H", data[2:4])[0]
                if block == expected_block:
                    f.write(data[4:])
                    ack = struct.pack("!HH", 4, block)
                    sock.sendto(ack, addr)
                    expected_block += 1

                if len(data[4:]) < BLOCK_SIZE:
                    print("파일 다운로드 완료")
                    break

            elif opcode == 5:  # ERROR
                print("서버 오류:", data[4:].decode(errors="ignore"))
                break

    sock.close()

def main():
    if len(sys.argv) != 4:
        print("사용법: python mytftp.py host get filename")
        sys.exit(1)

    host = sys.argv[1]
    command = sys.argv[2]
    filename = sys.argv[3]

    if command == "get":
        do_get(host, filename)
    else:
        print("get만 지원합니다")

if __name__ == "__main__":
    main()



