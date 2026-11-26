#!/usr/bin/env python3
"""Minimal NTRIP client for RTKsub.

Connects to ntrip.rtksub.com, sends your approximate position as an NMEA GGA
sentence and receives RTCM 3 corrections. The corrections can be written to a
file, forwarded to a receiver on a serial port, or both.

Only the Python standard library is needed. Forwarding to a serial port also
needs pyserial (pip install pyserial).

Example:
    export RTKSUB_USER=your_username
    export RTKSUB_PASSWORD=your_password
    python3 rtksub_ntrip_client.py --lat 52.0907 --lon 5.1214 --height 10 --out corrections.rtcm3
"""

import argparse
import base64
import datetime
import os
import socket
import sys
import time

DEFAULT_HOST = "ntrip.rtksub.com"
DEFAULT_PORT = 2101
DEFAULT_MOUNTPOINT = "AUTO"
USER_AGENT = "NTRIP rtksub-ntrip-examples/1.0"


def build_gga(lat, lon, height, now=None):
    """Return an NMEA GGA sentence (with checksum and CRLF) for a position."""
    now = now or datetime.datetime.now(datetime.timezone.utc)
    utc = now.strftime("%H%M%S") + ".00"

    lat_hemi = "N" if lat >= 0 else "S"
    lon_hemi = "E" if lon >= 0 else "W"
    lat, lon = abs(lat), abs(lon)
    lat_deg = int(lat)
    lon_deg = int(lon)
    lat_min = (lat - lat_deg) * 60.0
    lon_min = (lon - lon_deg) * 60.0
    lat_str = "%02d%08.5f" % (lat_deg, lat_min)
    lon_str = "%03d%08.5f" % (lon_deg, lon_min)

    # Fix quality 1 (GPS fix), 12 satellites, HDOP 1.0. The caster only needs
    # an approximate position to choose the nearest reference station.
    body = "GPGGA,%s,%s,%s,%s,%s,1,12,1.0,%.1f,M,0.0,M,," % (
        utc, lat_str, lat_hemi, lon_str, lon_hemi, height)
    checksum = 0
    for char in body:
        checksum ^= ord(char)
    return "$%s*%02X\r\n" % (body, checksum)


def crc24q(data):
    """CRC-24Q as used by RTCM 3."""
    crc = 0
    for byte in data:
        crc ^= byte << 16
        for _ in range(8):
            crc <<= 1
            if crc & 0x1000000:
                crc ^= 0x1864CFB
    return crc & 0xFFFFFF


class RtcmCounter:
    """Finds complete RTCM 3 frames in a byte stream and counts message types."""

    def __init__(self):
        self.buffer = bytearray()
        self.counts = {}
        self.bad_crc = 0

    def feed(self, data):
        self.buffer.extend(data)
        while True:
            start = self.buffer.find(b"\xd3")
            if start < 0:
                self.buffer.clear()
                return
            if start > 0:
                del self.buffer[:start]
            if len(self.buffer) < 3:
                return
            if self.buffer[1] & 0xFC:
                # The six reserved bits after the preamble must be zero.
                del self.buffer[:1]
                continue
            length = ((self.buffer[1] & 0x03) << 8) | self.buffer[2]
            frame_len = 3 + length + 3
            if len(self.buffer) < frame_len:
                return
            frame = bytes(self.buffer[:frame_len])
            expected = int.from_bytes(frame[-3:], "big")
            if length >= 2 and crc24q(frame[:-3]) == expected:
                msg_type = (frame[3] << 4) | (frame[4] >> 4)
                self.counts[msg_type] = self.counts.get(msg_type, 0) + 1
                del self.buffer[:frame_len]
            else:
                self.bad_crc += 1
                del self.buffer[:1]

    def summary(self):
        if not self.counts:
            return "no RTCM messages yet"
        parts = ["%d:%d" % (k, v) for k, v in sorted(self.counts.items())]
        return "RTCM message types (type:count) " + " ".join(parts)


def open_serial(port, baud):
    try:
        import serial  # pyserial
    except ImportError:
        sys.exit("Forwarding to a serial port needs pyserial: pip install pyserial")
    return serial.Serial(port, baud, timeout=0)


def connect(args):
    """Open the NTRIP connection and return the socket, ready to receive RTCM."""
    sock = socket.create_connection((args.host, args.port), timeout=10)
    credentials = base64.b64encode(
        ("%s:%s" % (args.user, args.password)).encode()).decode()
    request = (
        "GET /%s HTTP/1.0\r\n"
        "User-Agent: %s\r\n"
        "Accept: */*\r\n"
        "Connection: close\r\n"
        "Authorization: Basic %s\r\n"
        "\r\n" % (args.mountpoint, USER_AGENT, credentials))
    sock.sendall(request.encode())

    def receive_until(marker, data):
        while marker not in data:
            chunk = sock.recv(1024)
            if not chunk:
                raise ConnectionError("The caster closed the connection without a reply")
            data += chunk
        return data

    response = receive_until(b"\r\n", b"")
    status_line, rest = response.split(b"\r\n", 1)
    status = status_line.decode(errors="replace").strip()

    if status.startswith("ICY 200"):
        # NTRIP 1: the correction stream starts right after the status line.
        leftover = rest[2:] if rest.startswith(b"\r\n") else rest
        return sock, leftover

    if status.startswith("HTTP/") and " 200" in status:
        # HTTP style reply: skip the headers, the rest is the correction stream.
        response = receive_until(b"\r\n\r\n", response)
        return sock, response.split(b"\r\n\r\n", 1)[1]

    sock.close()
    if status.startswith("SOURCETABLE"):
        raise PermissionError("Mountpoint '%s' not found. Use AUTO (in capitals)." % args.mountpoint)
    if "401" in status or "Unauthorized" in status:
        raise PermissionError("Login refused (%s). Check username, password and "
                              "that your subscription or trial is active." % status)
    raise ConnectionError("Unexpected reply from caster: %s" % status)


def run(args):
    out_file = open(args.out, "ab") if args.out else None
    serial_port = open_serial(args.serial, args.baud) if args.serial else None
    counter = RtcmCounter()
    backoff = 2

    try:
        while True:
            try:
                sock, leftover = connect(args)
            except PermissionError as error:
                sys.exit(str(error))
            except OSError as error:
                print("Connection failed: %s. Retrying in %d s." % (error, backoff), flush=True)
                time.sleep(backoff)
                backoff = min(backoff * 2, 60)
                continue

            print("Connected to %s:%d/%s" % (args.host, args.port, args.mountpoint), flush=True)
            backoff = 2
            sock.settimeout(1.0)
            last_gga = 0.0
            last_report = time.monotonic()
            last_data = time.monotonic()

            def handle(data):
                if out_file:
                    out_file.write(data)
                    out_file.flush()
                if serial_port:
                    serial_port.write(data)
                counter.feed(data)

            if leftover:
                handle(leftover)

            try:
                while True:
                    now = time.monotonic()
                    if now - last_gga >= args.gga_interval:
                        sock.sendall(build_gga(args.lat, args.lon, args.height).encode())
                        last_gga = now
                    try:
                        data = sock.recv(4096)
                        if not data:
                            raise ConnectionError("The caster closed the connection")
                        last_data = time.monotonic()
                        handle(data)
                    except socket.timeout:
                        if time.monotonic() - last_data > 30:
                            raise ConnectionError("No data for 30 seconds")
                    if args.report and time.monotonic() - last_report >= args.report:
                        print(counter.summary(), flush=True)
                        last_report = time.monotonic()
            except OSError as error:
                print("Connection lost: %s. Reconnecting." % error, flush=True)
            finally:
                sock.close()
            time.sleep(backoff)
    except KeyboardInterrupt:
        print("\n" + counter.summary())
    finally:
        if out_file:
            out_file.close()
        if serial_port:
            serial_port.close()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(
        description="Minimal NTRIP client for RTKsub: sends GGA, receives RTCM 3.")
    parser.add_argument("--host", default=DEFAULT_HOST, help="caster address [%(default)s]")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="caster port [%(default)s]")
    parser.add_argument("--mountpoint", default=DEFAULT_MOUNTPOINT,
                        help="AUTO, AUTO_WGS84, AUTO_ITRF2020 or AUTO_ITRF2014 [%(default)s]")
    parser.add_argument("--user", default=os.environ.get("RTKSUB_USER"),
                        help="NTRIP username (or set RTKSUB_USER)")
    parser.add_argument("--password", default=os.environ.get("RTKSUB_PASSWORD"),
                        help="NTRIP password (or set RTKSUB_PASSWORD)")
    parser.add_argument("--lat", type=float, required=True, help="approximate latitude (degrees)")
    parser.add_argument("--lon", type=float, required=True, help="approximate longitude (degrees)")
    parser.add_argument("--height", type=float, default=0.0, help="approximate height (m) [0]")
    parser.add_argument("--gga-interval", type=float, default=10.0,
                        help="seconds between GGA sentences [%(default)s]")
    parser.add_argument("--out", help="append the RTCM stream to this file")
    parser.add_argument("--serial", help="forward the RTCM stream to this serial port, e.g. /dev/ttyACM0 or COM3")
    parser.add_argument("--baud", type=int, default=115200, help="serial baud rate [%(default)s]")
    parser.add_argument("--report", type=float, default=10.0,
                        help="seconds between message summaries, 0 to switch off [%(default)s]")
    args = parser.parse_args(argv)
    if not args.user or not args.password:
        parser.error("username and password are required (--user/--password or RTKSUB_USER/RTKSUB_PASSWORD)")
    if not -90 <= args.lat <= 90 or not -180 <= args.lon <= 180:
        parser.error("latitude or longitude out of range")
    return args


if __name__ == "__main__":
    run(parse_args())
