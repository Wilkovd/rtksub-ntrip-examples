# ROS 2 with RTKsub

The open-source [`ntrip_client`](https://github.com/LORD-MicroStrain/ntrip_client/tree/ros2) package connects to an NTRIP caster, publishes the RTCM corrections on `/rtcm` and sends your position to the caster from `/nmea` or `/fix`.

## Launch

```bash
export RTKSUB_USER=your_username
export RTKSUB_PASSWORD=your_password

ros2 launch ntrip_client ntrip_client_launch.py \
  host:=ntrip.rtksub.com \
  port:=2101 \
  mountpoint:=AUTO \
  username:=$RTKSUB_USER \
  password:=$RTKSUB_PASSWORD
```

## Topics

| Topic | Direction | Content |
| :--- | :--- | :--- |
| `/rtcm` | published | The RTCM corrections from RTKsub. The message type is set with the `rtcm_message_package` parameter: `mavros_msgs/RTCM` or `rtcm_msgs/Message`. |
| `/nmea` | subscribed | NMEA sentences (`nmea_msgs/Sentence`) from your GNSS driver. The GGA sentences go to the caster. |
| `/fix` | subscribed | Instead of `/nmea`: a `sensor_msgs/NavSatFix`, which the node turns into a GGA sentence. |

Your GNSS driver must publish its position on `/nmea` or `/fix`. Without it, RTKsub cannot choose a reference station and no corrections arrive. Feed `/rtcm` to the driver of your receiver, with a remapping if its topic has another name.

## Notes

- Install or build `ntrip_client` as described in its README.
- The package uses NTRIP 1 by default, which works with RTKsub.
- Keep your login details out of launch files you commit. That is why the example uses environment variables.
