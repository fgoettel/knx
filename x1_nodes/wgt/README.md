# WGT
Dieser Gira X1 Logic Node verbindet deine Schwörer Lüftungsanlage (kurz: WGT) mit deiner KNX Welt.
Hierzu wird ein simples Modbus Protokoll verwendet.

## Logic Nodes SDK1
* Download [SDK from Gira Partner Site](https://partner.gira.de/service/software-tools/developer.html).
 [Direct link](https://link.gira.de/LogicNodeSDKneu)
* Extract the SDK from either templates or examples (use the lowest level of LogicNodesSDK)

## Run tests
### Prerequisite
Setup poetry environment for modbus test server

`poetry install`

Run test modbus server (in order to run it on 502 admin rights are required):

`sudo poetry run python ModbusServer.py`

# Todos:
* Extend this readme to be a help
* Do network communication in threads (do not block in case of timeout)
