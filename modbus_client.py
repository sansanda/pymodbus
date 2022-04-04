#!/usr/bin/env python
"""
Pymodbus Synchronous Client Examples
--------------------------------------------------------------------------

The following is an example of how to use the synchronous modbus client
implementation from pymodbus.

It should be noted that the client can also be used with
the guard construct that is available in python 2.5 and up::

    with ModbusClient('127.0.0.1') as client:
        result = client.read_coils(1,10)
        print result
"""

import matplotlib.pyplot as plt
from matplotlib.axes._axes import _AxesBase
# --------------------------------------------------------------------------- #
# import the various client implementations
# --------------------------------------------------------------------------- #
# from pymodbus.client.sync import ModbusTcpClient as ModbusClient
# from pymodbus.client.sync import ModbusUdpClient as ModbusClient
from time import sleep

from pymodbus.bit_read_message import ReadDiscreteInputsResponse
from pymodbus.client.sync import ModbusSerialClient as ModbusClient

# --------------------------------------------------------------------------- #
# configure the client logging
# --------------------------------------------------------------------------- #
import logging

from pymodbus.register_read_message import ReadHoldingRegistersResponse

FORMAT = ('%(asctime)-15s %(threadName)-15s '
          '%(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')
logging.basicConfig(format=FORMAT)
log = logging.getLogger()
log.setLevel(logging.DEBUG)

UNIT = 1
REFRESH_TIME = 5
PLOT_WINDOW_X_LIMIT = int((24 * 60 * 60) / REFRESH_TIME)


def run_sync_client():
    time = list()
    temperature_log = list()
    humidity_log = list()

    # ------------------------------------------------------------------------#
    # choose the client you want
    # ------------------------------------------------------------------------#
    # make sure to start an implementation to hit against. For this
    # you can use an existing device, the reference implementation in the tools
    # directory, or start a pymodbus server.
    #
    # If you use the UDP or TCP clients, you can override the framer being used
    # to use a custom implementation (say RTU over TCP). By default they use
    # the socket framer::
    #
    #    client = ModbusClient('localhost', port=5020, framer=ModbusRtuFramer)
    #
    # It should be noted that you can supply an ipv4 or an ipv6 host address
    # for both the UDP and TCP clients.
    #
    # There are also other options that can be set on the client that controls
    # how transactions are performed. The current ones are:
    #
    # * retries - Specify how many retries to allow per transaction (default=3)
    # * retry_on_empty - Is an empty response a retry (default = False)
    # * source_address - Specifies the TCP source address to bind to
    # * strict - Applicable only for Modbus RTU clients.
    #            Adheres to modbus protocol for timing restrictions
    #            (default = True).
    #            Setting this to False would disable the inter char timeout
    #            restriction (t1.5) for Modbus RTU
    #
    #
    # Here is an example of using these options::
    #
    #    client = ModbusClient('localhost', retries=3, retry_on_empty=True)
    # ------------------------------------------------------------------------#
    # client = ModbusClient('localhost', port=5020)
    # from pymodbus.transaction import ModbusRtuFramer
    # client = ModbusClient('localhost', port=5020, framer=ModbusRtuFramer)
    # client = ModbusClient(method='binary', port='/dev/ptyp0', timeout=1)
    # client = ModbusClient(method='ascii', port='/dev/ptyp0', timeout=1)
    client = ModbusClient(method='rtu', port='COM3', timeout=1, baudrate=9600)
    client.connect()

    # creating subplot and figure
    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    ax2 = ax.twinx()



    while True:

        if len(time) == 0:
            time.append(0)
        else:
            time.append(time[-1] + REFRESH_TIME)

        hrs = client.read_holding_registers(0, 16, unit=UNIT)
        temperature = hrs.registers[0]
        humidity = hrs.registers[1]

        temperature_log.append(temperature)
        humidity_log.append(humidity)

        ax.clear()
        ax2.clear()

        if len(time) < PLOT_WINDOW_X_LIMIT:
            ax.plot(time, temperature_log, color='red')
            ax2.plot(time, humidity_log, color='blue')

        else:
            ax.plot(time[-PLOT_WINDOW_X_LIMIT:], temperature_log[-PLOT_WINDOW_X_LIMIT:], color='red')
            ax2.plot(time[-PLOT_WINDOW_X_LIMIT:], humidity_log[-PLOT_WINDOW_X_LIMIT:], color='blur')

        # Format plot
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.3)
        plt.title('Chamber Temperature and Humidity over Time')
        ax.set_ylabel("Temperature (ºC)", color='red')
        ax.set_ylim(auto=False, ymin=0, ymax=100)
        ax2.set_ylabel("Humidity (%)", color='blue')
        ax2.set_ylim(auto=False, ymin=20, ymax=80)
        plt.xlabel('Seconds (s) x ' + str(REFRESH_TIME))

        plt.pause(REFRESH_TIME)

    # log.debug("Write to a holding register and read back")
    # rq = client.write_register(1, 12, unit=UNIT)
    # rr = client.read_holding_registers(1, 1, unit=UNIT)
    # print(rr.registers[0])
    #
    # log.debug("Write to multiple holding registers and read back")
    # rq = client.write_registers(1, [10]*8, unit=UNIT)
    # rr = client.read_holding_registers(1, 8, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # assert(rr.registers == [10]*8)      # test the expected value

    # # ------------------------------------------------------------------------#
    # # specify slave to query
    # # ------------------------------------------------------------------------#
    # # The slave to query is specified in an optional parameter for each
    # # individual request. This can be done by specifying the `unit` parameter
    # # which defaults to `0x00`
    # # ----------------------------------------------------------------------- #
    # log.debug("Reading Coils")
    # rr = client.read_coils(1, 1, unit=UNIT)
    # log.debug(rr)
    #
    #
    # # ----------------------------------------------------------------------- #
    # # example requests
    # # ----------------------------------------------------------------------- #
    # # simply call the methods that you would like to use. An example session
    # # is displayed below along with some assert checks. Note that some modbus
    # # implementations differentiate holding/input discrete/coils and as such
    # # you will not be able to write to these, therefore the starting values
    # # are not known to these tests. Furthermore, some use the same memory
    # # blocks for the two sets, so a change to one is a change to the other.
    # # Keep both of these cases in mind when testing as the following will
    # # _only_ pass with the supplied asynchronous modbus server (script supplied).
    # # ----------------------------------------------------------------------- #
    # log.debug("Write to a Coil and read back")
    # rq = client.write_coil(0, True, unit=UNIT)
    # rr = client.read_coils(0, 1, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # assert(rr.bits[0] == True)          # test the expected value
    #
    # log.debug("Write to multiple coils and read back- test 1")
    # rq = client.write_coils(1, [True]*8, unit=UNIT)
    # rr = client.read_coils(1, 21, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # resp = [True]*21
    #
    # # If the returned output quantity is not a multiple of eight,
    # # the remaining bits in the final data byte will be padded with zeros
    # # (toward the high order end of the byte).
    #
    # resp.extend([False]*3)
    # assert(rr.bits == resp)         # test the expected value
    #
    # log.debug("Write to multiple coils and read back - test 2")
    # rq = client.write_coils(1, [False]*8, unit=UNIT)
    # rr = client.read_coils(1, 8, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # assert(rr.bits == [False]*8)         # test the expected value
    #
    # log.debug("Read discrete inputs")
    # rr = client.read_discrete_inputs(0, 8, unit=UNIT)
    # assert(not rr.isError())     # test that we are not an error
    #
    # log.debug("Write to a holding register and read back")
    # rq = client.write_register(1, 10, unit=UNIT)
    # rr = client.read_holding_registers(1, 1, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # assert(rr.registers[0] == 10)       # test the expected value
    #
    # log.debug("Write to multiple holding registers and read back")
    # rq = client.write_registers(1, [10]*8, unit=UNIT)
    # rr = client.read_holding_registers(1, 8, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # assert(rr.registers == [10]*8)      # test the expected value
    #
    # log.debug("Read input registers")
    # rr = client.read_input_registers(1, 8, unit=UNIT)
    # assert(not rr.isError())     # test that we are not an error
    #
    # arguments = {
    #     'read_address':    1,
    #     'read_count':      8,
    #     'write_address':   1,
    #     'write_registers': [20]*8,
    # }
    # log.debug("Read write registeres simulataneously")
    # rq = client.readwrite_registers(unit=UNIT, **arguments)
    # rr = client.read_holding_registers(1, 8, unit=UNIT)
    # assert(not rq.isError())     # test that we are not an error
    # assert(not rr.isError())     # test that we are not an error
    # assert(rq.registers == [20]*8)      # test the expected value
    # assert(rr.registers == [20]*8)      # test the expected value

    # ----------------------------------------------------------------------- #
    # close the client
    # ----------------------------------------------------------------------- #
    client.close()


if __name__ == "__main__":
    run_sync_client()
