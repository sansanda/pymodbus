#!/usr/bin/env python
"""
Pymodbus Server With Updating Thread
--------------------------------------------------------------------------

This is an example of having a background thread updating the
context while the server is operating. This can also be done with
a python thread::

    from threading import Thread

    thread = Thread(target=updating_writer, args=(context,))
    thread.start()
"""

import threading
from datetime import timedelta, time

# --------------------------------------------------------------------------- #
# import the modbus libraries we need
# --------------------------------------------------------------------------- #

from pymodbus.version import version
from pymodbus.server.sync import StartSerialServer

from pymodbus.device import ModbusDeviceIdentification
from pymodbus.datastore import ModbusSequentialDataBlock
from pymodbus.datastore import ModbusSlaveContext, ModbusServerContext

from pymodbus.transaction import ModbusRtuFramer, ModbusBinaryFramer

# --------------------------------------------------------------------------- #
# configure the service logging
# --------------------------------------------------------------------------- #
import logging

logging.basicConfig()
log = logging.getLogger()
log.setLevel(logging.DEBUG)


WAIT_TIME_SECONDS = 5

# --------------------------------------------------------------------------- #
# function for loading the numbers to be served by the modbus server
# The data is loaded via reading a comma separated value file columns
# --------------------------------------------------------------------------- #

def load_numbers(path, n_cols):

    data = list()
    col1 = list()
    col2 = list()

    with open(path) as f:
        data = f.readlines()

    for line in data:
        cols = line.split(",")
        col1.append(int(float(cols[0])))
        col2.append(int(float(cols[1][:-1])))

    return col1,col2

# --------------------------------------------------------------------------- #
# function aclled periodically for updating the modbus registers
# --------------------------------------------------------------------------- #

def updating_context(a, temperatures, humidities):
    """ A worker process that runs every so often and
    updates live values of the context. It should be noted
    that there is a race condition for the update.

    :param arguments: The input arguments to the call
    """
    log.debug("updating the context")
    context = a
    address = 0
    register = 3
    slave_id = 0x00


    #tomamos el primer numero de la lista de temperaturas y lo añadimos al final
    temperature = temperatures.pop(0)
    temperatures.append(temperature)

    # tomamos el primer numero de la lista de humedades y lo añadimos al final
    humidity = humidities.pop(0)
    humidities.append(humidity)

    print(temperature,humidity)


    # values = context[slave_id].getValues(register, address, count=5)
    # values = [v + 1 for v in values]
    # log.debug("new values: " + str(values))
    context[slave_id].setValues(register, address, [temperature])
    context[slave_id].setValues(register, address+1, [humidity])


def run_server():
    # ----------------------------------------------------------------------- #
    # load the numbers for testing
    # ----------------------------------------------------------------------- #
    temperatures, humidities = load_numbers("Tdata",2)

    # ----------------------------------------------------------------------- #
    # initialize your data store
    # ----------------------------------------------------------------------- #

    store = ModbusSlaveContext(
        di=ModbusSequentialDataBlock(0, [(100+i) for i in range (0,100)]),
        co=ModbusSequentialDataBlock(0, [(200+i) for i in range (0,100)]),
        hr=ModbusSequentialDataBlock(0, [(300+i) for i in range (0,100)]),
        ir=ModbusSequentialDataBlock(0, [(400+i) for i in range (0,100)]))
    context = ModbusServerContext(slaves=store, single=True)

    # ----------------------------------------------------------------------- #
    # initialize the server information
    # ----------------------------------------------------------------------- #
    identity = ModbusDeviceIdentification()
    identity.VendorName = 'pymodbus'
    identity.ProductCode = 'PM'
    identity.VendorUrl = 'http://github.com/riptideio/pymodbus/'
    identity.ProductName = 'pymodbus Server'
    identity.ModelName = 'pymodbus Server'
    identity.MajorMinorRevision = version.short()

    # ----------------------------------------------------------------------- #
    # run the thread that updates the context every defined time
    # ----------------------------------------------------------------------- #

    job = Job(timedelta(seconds=WAIT_TIME_SECONDS), updating_context, context, temperatures, humidities)
    job.start()

    # ----------------------------------------------------------------------- #
    # run the server you want
    # ----------------------------------------------------------------------- #

    # RTU:
    StartSerialServer(context, framer=ModbusRtuFramer, identity=identity, port='COM1', timeout=.005, baudrate=9600)


# --------------------------------------------------------------------------- #
# Auxiliary class for Job, Thread managing
# --------------------------------------------------------------------------- #

class Job(threading.Thread):
    def __init__(self, interval, execute, *args, **kwargs):
        threading.Thread.__init__(self)
        self.daemon = False
        self.stopped = threading.Event()
        self.interval = interval
        self.execute = execute
        self.args = args
        self.kwargs = kwargs

    def stop(self):
        self.stopped.set()
        self.join()

    def run(self):
        while not self.stopped.wait(self.interval.total_seconds()):
            self.execute(*self.args, **self.kwargs)

if __name__ == "__main__":
    run_server()
