# Setting your Device to Ad-Hoc mode
## 1) Check if AP mode is supported
Check if `AP` is listed in the command below:
```bash
$ iw list
>>> 	Supported interface modes:
>>>		 * IBSS
>>>		 * managed
>>>		 * AP
>>>		 * AP/VLAN
>>>		 * monitor
>>>		 * mesh point
```

## 2) Enable IP Forwarding
Open `sysctl` in any editor (nano in this case).
``` bash
$ sudo nano /etc/sysctl.conf
```
And make sure that IP forwarding is enabled.
```bash
net.ipv4.ip_forward=1
```

## 3) Create/Modify interface file
Open the interface configuration file in any editor (nano in this  case)
``` bash
$ cd /etc/network
$ sudo cp interfaces interfaces.bak # Create backup copy
$ sudo nano interfaces
```
Add the configuration (`wlp2s0` is the wireless interface here):
``` bash
auto lo
iface lo inet loopback

auto wlp2s0
iface wlp2s0 inet static
    address 20.0.0.1     # Use reasonable IP addresses here
    netmask 255.255.255.0
    wireless-channel 1
    wireless-essid Experimental-Ad-Hoc-Network
    wireless-key my_supersecret_passkey_NEVER_push_to_github    # Optional, but reasonable
    wireless-mode ad-hoc
```
Save the file.

## 4) Setup IP Tables
Where `wlp2s0` is the wireless interface
``` bash
$ sudo iptables -t nat -A POSTROUTING -o wlp2s0 -j MASQUERADE
```