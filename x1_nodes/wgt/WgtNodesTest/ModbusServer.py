import logging
import random

from pymodbus.datastore import (
    ModbusSequentialDataBlock,
    ModbusServerContext,
    ModbusSlaveContext,
)
from pymodbus.server.sync import StartTcpServer


def run_server(port, host="localhost"):
    # Initalize all register with the register address as default value
    samples = [random.randint(1, 2**16) for _ in range(800)]
    register = ModbusSequentialDataBlock(100, samples)

    # Create data store and create context
    store = ModbusSlaveContext(
        hr=register, ir=register, zero_mode=True  # holding register  # input register
    )
    context = ModbusServerContext(slaves=store, single=True)

    # Start server
    logging.info("Starting debug server on %s:%i.", host, port)
    try:
        StartTcpServer(context, address=(host, port))
    except KeyboardInterrupt:
        logging.info("Server shut down.")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    port = 5020
    run_server(port=port)
