#!/usr/bin/env python3

from pymodbus.server.sync import StartTcpServer
from pymodbus.datastore import ModbusSequentialDataBlock, ModbusSparseDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.device import ModbusDeviceIdentification

import logging
import random

def run_server(port, host="localhost"):
    # Initalize all register with the register address as default value
    samples = [random.randint(1,2**16) for _ in range(800)]
    register = ModbusSequentialDataBlock(100, samples)

    # Create data store and create context
    store = ModbusSlaveContext(
        hr=register, # holding register
        ir=register, # input register
        zero_mode=True)
    context = ModbusServerContext(slaves=store, single=True)

    # Start server
    logging.info("Starting debug server on %s:%i.", host, port)
    StartTcpServer(context, address=(host, port))


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = 502
    run_server(port=port)
