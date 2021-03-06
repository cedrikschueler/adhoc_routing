# Setting your Device to Ad-Hoc mode
## 1) Check if AP mode is supported
Check if `P2P` is listed in the command below:
```bash
$ iw list
>>> 	Supported interface modes:
>>>		 * IBSS
>>>		 * managed
>>>		 * AP
>>>		 * AP/VLAN
>>>		 * monitor
>>>		 * mesh point
>>>      * P2P-*
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
auto wlp2s0
iface wlp2s0 inet static
    pre-up iptables -t nat -A POSTROUTING -o wlp2s0 -j MASQUERADE
    address 20.0.0.1     # Use reasonable IP addresses here
    netmask 255.255.255.0
    wireless-channel 1  # Some channels might be congested
    wireless-essid masterthesis
    wireless-mode ad-hoc
    dns-nameservers 208.67.222.222
```
Save the file.

## 4) Setup IP Tables
Where `wlp2s0` is the wireless interface
``` bash
$ sudo iptables -t nat -A POSTROUTING -o wlp2s0 -j MASQUERADE
```

## 5) Invalidate default Gateway
To ensure that only the routing is responsible for successfull transmissions, you might want to invalidate the default gateway.
```
$ ip route replace 20.0.0.0/24 via 20.0.0.99 dev wlp2s0 onlink
```

## Troubleshooting
If you're still not receiving routing messages via broadcast (which should mostly work if the devices are in range),
you want to check if the devices are registered in ARP list.

```
$ arp
Address                  HWtype  HWaddress           Flags Mask            Iface
20.0.0.1                 ether   aa:aa:aa:aa:aa:aa   C                     wlp2s0
```
If not, you can add it manually:
```
arp -s 20.0.0.1 aa:aa:aa:aa:aa:aa
```