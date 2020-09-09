# Changing the Baud Rate on your GPS Receiver
While trying to increase the sampling interval of my gps receiver, I encountered the problem, that my baud rate was messed up.
After rebooting or re-plugging my receiver, the baud rate was set to a high value the gpsd-client could not handle.

Resetting with `stty` was not persistent.

## Solution:

```bash
>>> exec 3<>/dev/ttyACM0        # open a file descriptor
>>> stty -f /dev/ttyACM0 9600   # configure the serial port, set baud rate to 9600 bps
>>> exec 3<&-                   # close the file descriptor
```

Credits: https://apple.stackexchange.com/questions/177448/stty-device-baud-rate-resets-once-no-longer-being-used

## Takeaway
Most gps receivers seem to have a fixed sampling interval (mostly 1.0s). 
Its not possible to tune this.

If the receiver is tunable in that manner, this is the right command for gpsd:
```bash
>>> gpsctl -c 0.2               # For 0.2s sampling interval respectively 5Hz
```