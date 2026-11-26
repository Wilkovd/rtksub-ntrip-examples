# RTKsub NTRIP examples

Settings and small examples for connecting GNSS receivers, robots, drones and machines to [RTKsub](https://rtksub.com) RTK corrections over NTRIP.

RTKsub delivers real-time RTK corrections from the GEODNET network to any receiver or app with an NTRIP client. Under good conditions RTK typically reaches 1 to 2 cm.

## Contents

- [Connection settings](#connection-settings)
- [How it works](#how-it-works)
- [Mountpoints and coordinates](#mountpoints-and-coordinates)
- [Examples](#examples)
- [Setup guides for devices and apps](#setup-guides-for-devices-and-apps)
- [Troubleshooting](#troubleshooting)
- [About](#about)

## Connection settings

| Setting | Value |
| :--- | :--- |
| Caster address | `ntrip.rtksub.com` |
| Port | `2101` |
| Mountpoint | `AUTO` |
| Protocol | NTRIP 1 or NTRIP 2 |
| Username and password | Your NTRIP login details in your RTKsub account: My account > NTRIP login details |
| Send position (NMEA GGA) | On. This is required. |
| Correction format | RTCM 3.2 MSM for GPS, GLONASS, Galileo and BeiDou |

Use the address, not an IP address. `ntrip.rtksub.com` works worldwide, so you do not need to choose a regional server. One subscription is one connection: one device at a time.

## How it works

1. Your NTRIP client connects to `ntrip.rtksub.com:2101` with the mountpoint `AUTO`.
2. It sends your approximate position as an NMEA GGA sentence, for example every 10 seconds.
3. The network picks the nearest reference station and streams its RTCM corrections.
4. Your receiver applies the corrections and goes from FLOAT to FIX.

Without a GGA position the connection opens, but no corrections arrive.

## Mountpoints and coordinates

| Mountpoint | Coordinates you get |
| :--- | :--- |
| `AUTO` | The regional reference frame for your country, for example NAD83(2011) in the United States, ETRS89 (ETRF2000) in Europe and GDA2020 in Australia. Recommended for most users. |
| `AUTO_WGS84` | WGS84 (G2139) at the middle of the current year, for example 2026.5 |
| `AUTO_ITRF2020` | ITRF2020 at the current epoch |
| `AUTO_ITRF2014` | ITRF2014 at the current epoch |

Type the mountpoint exactly as shown, in capitals.

Heights are ellipsoidal. For heights above sea level, apply your national geoid model in your field or processing software.

What `AUTO` delivers per country, including the epoch, is listed in GEODNET's [coordinate system reference](https://github.com/geodnet/geodnet_rtk_service_coordinate_system) and on the country pages of [rtksub.com](https://rtksub.com).

## Examples

| Folder | What it shows |
| :--- | :--- |
| [`rtklib/`](rtklib/) | Stream the corrections to a receiver on a serial or USB port with RTKLIB `str2str`, for example on a Raspberry Pi. Or save them to a file. |
| [`python/`](python/) | A small NTRIP client in Python without dependencies. It sends GGA, receives RTCM 3 and writes the stream to a file or a serial port. |
| [`ros2/`](ros2/) | Use RTKsub in ROS 2 with the open-source `ntrip_client` package. |

## Setup guides for devices and apps

Step-by-step guides on rtksub.com. Start with the general [connection guide](https://rtksub.com/how-to-connect-to-the-rtk-network/).

**Receivers, software and GIS apps**
- [u-blox ZED-F9P with u-center](https://rtksub.com/u-blox-zed-f9p-ntrip-setup/)
- [RTKLIB (RTKNAVI and STRSVR)](https://rtksub.com/rtklib-ntrip-setup/)
- [Emlid Reach](https://rtksub.com/emlid-reach-ntrip-setup/)
- [SW Maps](https://rtksub.com/sw-maps-ntrip-setup/)
- [Lefebure NTRIP Client (Android)](https://rtksub.com/lefebure-ntrip-client-setup/)

**Survey controllers**
- [Trimble Access](https://rtksub.com/trimble-access-ntrip-setup/)
- [Leica Captivate](https://rtksub.com/leica-captivate-ntrip-setup/)
- [CHCNAV LandStar](https://rtksub.com/chcnav-landstar-ntrip-setup/)
- [ComNav T300](https://rtksub.com/comnav-t300-ntrip-setup/)

**Drones**
- [DJI Matrice 4 series](https://rtksub.com/dji-matrice-4-rtk-setup/)
- [DJI Matrice 400](https://rtksub.com/dji-matrice-400-rtk-setup/)
- [DJI Matrice 350 RTK and 300 RTK](https://rtksub.com/dji-matrice-350-300-rtk-setup/)
- [DJI Mavic 3 Enterprise](https://rtksub.com/dji-mavic-3-enterprise-rtk-setup/)
- [DJI Mavic 3 Multispectral](https://rtksub.com/dji-mavic-3-multispectral-rtk-setup/)
- [Autel EVO II RTK](https://rtksub.com/autel-evo-ii-rtk-ntrip-setup/)
- [Autel EVO Max](https://rtksub.com/autel-evo-max-rtk-ntrip-setup/)
- [Mission Planner (ArduPilot)](https://rtksub.com/mission-planner-rtk-setup/)

**Agriculture**
- [AgOpenGPS](https://rtksub.com/agopengps-rtk-setup/)
- [DJI Agras T50, T25, T70P and T100](https://rtksub.com/dji-agras-rtk-setup/)
- [CHCNAV NX510](https://rtksub.com/chcnav-nx510-ntrip-setup/)
- [FJD AT2 autosteering kit](https://rtksub.com/fjd-at2-ntrip-setup/)

## Troubleshooting

| What you see | What to check |
| :--- | :--- |
| Login refused | Username and password, exactly as shown in your account. Is your subscription or trial active? Is the same login already in use on another device? |
| Connected, but no corrections | Is the position (NMEA GGA) being sent? Is the mountpoint `AUTO`, in capitals? |
| No connection at all | Some Wi-Fi networks block port 2101. Try mobile data. |
| FLOAT, but no FIX | Open sky, a multi-band receiver and antenna, and the distance to the nearest station on the [coverage map](https://rtksub.com/coverage/). Results are best within about 25 km of a station. |
| Age of corrections above 5 seconds | Usually the data connection. Check the mobile signal. |
| Coordinates differ from an earlier survey | Check the reference frame and epoch of both, and compare with a known point. |

## About

[RTKsub](https://rtksub.com) offers RTK correction subscriptions on the GEODNET network, with monthly and annual plans and a free trial. See [pricing](https://rtksub.com/pricing/) and the [coverage map](https://rtksub.com/coverage/). Questions: [contact us](https://rtksub.com/contact/).

This repository is maintained by RTKsub. GEODNET is a separate organization; its own documentation is at [github.com/geodnet](https://github.com/geodnet).

Last checked: November 2026.

## License

The code and examples in this repository are released under the [MIT License](LICENSE).
