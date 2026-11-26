# RTKLIB str2str with RTKsub

`str2str` is the stream server of [RTKLIB](https://github.com/rtklibexplorer/RTKLIB). It takes the RTKsub correction stream and passes it to a receiver on a serial or USB port. This works well on a Raspberry Pi or another small Linux computer next to the receiver.

For RTKNAVI and STRSVR on Windows, see the [RTKLIB setup guide](https://rtksub.com/rtklib-ntrip-setup/) on rtksub.com.

## Install

Use a recent build of the RTKLIB demo5 fork by [rtklibexplorer](https://github.com/rtklibexplorer/RTKLIB), or the `rtklib` package of your Linux distribution.

## Send corrections to your receiver

Replace `USER` and `PASSWORD` with your NTRIP login details, and `ttyACM0` with the port of your receiver.

```bash
str2str -in ntrip://USER:PASSWORD@ntrip.rtksub.com:2101/AUTO \
        -out serial://ttyACM0:115200 \
        -b 1
```

`-b 1` relays what the receiver sends on that port back to the caster. Your receiver must output NMEA GGA on the same port, so the network knows where you are. This is the best option on a moving vehicle, because the network always gets your current position.

## Or send a fixed position

If the receiver does not output GGA on that port, give your approximate position. `str2str` then sends a GGA sentence every 10 seconds:

```bash
str2str -in ntrip://USER:PASSWORD@ntrip.rtksub.com:2101/AUTO \
        -out serial://ttyACM0:115200 \
        -p 52.0907 5.1214 10 -n 10000
```

`-p` is latitude and longitude in degrees and height in metres. `-n` is the interval in milliseconds. A rough position is enough: the network uses it to pick the nearest reference station.

## Save the corrections to a file

```bash
str2str -in ntrip://USER:PASSWORD@ntrip.rtksub.com:2101/AUTO \
        -out file://rtksub.rtcm3 \
        -p 52.0907 5.1214 10 -n 10000
```

## Notes

- On Windows the port is written as `serial://COM3:115200`.
- Over USB the baud rate is usually ignored. Over a UART it must match the receiver.
- The receiver must accept RTCM 3 on the port you use. On a u-blox ZED-F9P, check that RTCM3 is enabled as an input protocol on that port.
- Stop `str2str` with Ctrl+C.
