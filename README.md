# Python based Ad-Hoc Routing
## Description
This Repository provides a python based Ad-Hoc Routing implementation

See `Notes` folder for some useful documentation on issues around setup and usage descriptions.

An example experiment setup is provided in `main.py`. 

The usage of json-formatted setup is recommended. This way you can easily extend the code and load different experimental setups from files.

`sudo` privileges are required to allow the routing table module to write and delete IP table entries.
#### Provided MANET Routing Protocols
- [x] PARRoT (own implementation)
#### Possible Additions
- [ ] DSDV

#### Known Issues
- [x] Conversion of GPS coordinates to Cartesian is missing (required for Mobility Prediction)
- [x] Traffic Generator generates traffic, but no evaluation is implemented
- [x] ~~Control flags when writing to Linux routing table~~ (Seems fine)
- [x] Mobility Prediction methods are not embedded yet
- [x] ~~Provide velocity from GNSSReceiver~~ (Velocity not needed in newest Parrod implementation)

## Related Work
Created during my master thesis at [Communication Networks Institute (CNI)](https://www.kn.e-technik.tu-dortmund.de/cms/en/institute/), TU Dortmund University
>Design and Performance Evaluation of a Reinforcement Learning-Based
Mobile Ad-hoc Network Routing Protocol

If you use this in your research, please cite the following:
```
@InProceedings{Sliwa2021parrot,
	Author = {Benjamin Sliwa and Cedrik Schüler and Manuel Patchou and Christian Wietfeld},
	Title = {{PARRoT}: {Predictive} ad-hoc routing fueled by reinforcement learning and trajectory knowledge},
	Booktitle = {2021 IEEE 93rd Vehicular Technology Conference (VTC-Spring)},
	Year = {2021},
	Publishingstatus = {accepted for presentation},
	Address = {Helsinki, Finland},
	Month = apr,
	Eprint = {2012.05490},
	Eprinttype = {arxiv},
	Cnidoc = {1607585431},
	Project = {A-DRZ, SFB876-A4, SFB876-B4}
}
```

(c) Cedrik Schüler, 2020
