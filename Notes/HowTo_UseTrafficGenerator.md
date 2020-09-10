# Usage of Traffic Generator and Receiver
## Introduction
The Traffic Generator folder provides two base classes, which are `TrafficGenerator` and `TrafficReceiver`.
They are meant to stream a constant bit rate from one node to another to do a performance analysis of the mobile ad-hoc network.

## Traffic Generator
The generator has following parameters to tune the data stream:

| Parameter   |      Type      |  Description |
|:----------|:-------------|------:|
| `targetCBR_MBits`|  Float | Target constant bit rate in MBit/s |
| `destination`| String with IPv4 address in dotted decimal repr. or `<broadcast>`   |  Defines the target of the data stream |
| `MTU_used_byte` | Integer |  MTU to use |
|`port`| Integer| Port to use for data stream|

Create an instance, then call `start()` to run the thread routine.
You can cancel it after some runtime with `terminate()`.
#### Example
```python3
ip = "192.168.178.99"
# ip = "<broadcast>"    # You can also set destination to broadcast if its reasonable for your experiment
tg = TrafficGenerator(2.0, ip, MTU_used_byte=1460, port=1801)
tg.start()
time.sleep(60)
tg.terminate()
```

## Traffic Receiver
The receiver is the counterpart for the traffic generator.
It provides the following parameters:

(self, sender: str, port: int, bufferSize: int)

| Parameter   |      Type      |  Description |
|:----------|:-------------|------:|
| `sender`|  String with IPv4 address in dotted decimal repr. or `""` | The receiver reacts to this address or to any if `""` |
|`port`| Integer| Port to use for data stream|
|`bufferSize`| Integer | Buffer size for stream reception. Choose reasonable (e.g. MTU of generator)|

#### Example
```python3
tr = TrafficReceiver('192.168.178.24', 1801, 1460)
tr.start()
time.sleep(60)
tr.terminate()
```
Create an instance, then call `start()` to run the thread routine.
You can cancel it after some runtime with `terminate()`.