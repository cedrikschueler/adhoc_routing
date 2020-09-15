# Python based Ad-Hoc Routing
## Description
This Repository provides a python based Ad-Hoc Routing implementation

See `Notes` folder for some useful documentation on issues around setup and usage descriptions.

An example experiment setup is provided in `main.py`. 

The usage of json-formatted setup is recommended. This way you can easily extend the code and load different experimental setups from files.

`sudo` privileges are required to allow the routing table module to write and delete IP table entries.
#### Provided MANET Routing Protocols
- [x] Parrod (own implementation)
#### Possible Additions
- [ ] DSDV

#### Known Issues
- [x] Conversion of GPS coordinates to Cartesian is missing (required for Mobility Prediction)
- [x] Traffic Generator generates traffic, but no evaluation is implemented
- [x] ~~Control flags when writing to Linux routing table~~ (Seems fine)
- [ ] Mobility Prediction methods are not embedded yet
- [x] ~~Provide velocity from GNSSReceiver~~ (Velocity not needed in newest Parrod implementation)

## Related Work
Created during my master thesis at [Communication Networks Institute (CNI)](https://www.kn.e-technik.tu-dortmund.de/cms/en/institute/), TU Dortmund University
>Design and Performance Evaluation of a Reinforcement Learning-Based
Mobile Ad-hoc Network Routing Protocol


(c) Cedrik Schüler, 2020
