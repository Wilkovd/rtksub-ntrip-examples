# Python NTRIP client for RTKsub

[`rtksub_ntrip_client.py`](rtksub_ntrip_client.py) is a small NTRIP client that only needs Python 3.8 or newer.

It connects to `ntrip.rtksub.com:2101`, sends your approximate position as NMEA GGA every 10 seconds and receives the RTCM 3 corrections. It can:

- write the correction stream to a file,
- forward it to a receiver on a serial port (needs `pip install pyserial`),
- show which RTCM message types arrive, for example 1074 (GPS), 1084 (GLONASS), 1094 (Galileo) and 1124 (BeiDou).

It reconnects by itself when the connection drops.

## Usage

```bash
export RTKSUB_USER=your_username
export RTKSUB_PASSWORD=your_password

# Save the corrections to a file and show the message types
python3 rtksub_ntrip_client.py --lat 52.0907 --lon 5.1214 --height 10 --out corrections.rtcm3

# Forward the corrections to a receiver on a serial port
python3 rtksub_ntrip_client.py --lat 52.0907 --lon 5.1214 --serial /dev/ttyACM0 --baud 115200
```

## Options

| Option | Default | Meaning |
| :--- | :--- | :--- |
| `--user`, `--password` | `RTKSUB_USER`, `RTKSUB_PASSWORD` | Your NTRIP login details |
| `--lat`, `--lon` | required | Approximate position in degrees |
| `--height` | `0` | Approximate height in metres |
| `--mountpoint` | `AUTO` | `AUTO`, `AUTO_WGS84`, `AUTO_ITRF2020` or `AUTO_ITRF2014` |
| `--out` | | Append the correction stream to this file |
| `--serial`, `--baud` | `115200` | Forward the correction stream to this serial port |
| `--gga-interval` | `10` | Seconds between GGA sentences |
| `--report` | `10` | Seconds between message summaries, `0` to switch off |
| `--host`, `--port` | `ntrip.rtksub.com`, `2101` | Caster address and port |

## Notes

- The position only has to be approximate: the network uses it to choose the nearest reference station. On a moving vehicle, send the current position of your receiver instead, for example with RTKLIB (`-b 1`, see [`../rtklib`](../rtklib)) or ROS 2 (`/fix`, see [`../ros2`](../ros2)).
- Keep your login details out of scripts you share. That is why the example uses environment variables.
