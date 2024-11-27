#!python

# A commandline and web tool to control NicePower bench supplys over RS232

from serial import Serial, PARITY_NONE, STOPBITS_ONE, EIGHTBITS
from time import sleep
from sys import stderr, exit
from os import environ
from argparse import ArgumentParser
from typing import Tuple

SERIAL_PORT: str|None = ''  # Pass in via command line arg -s
BAUD_RATE: int = 9600
TIMEOUT: int = 1
ARG_NOT_PRESENT = -99

def make_frame(read=True, voltage=True, val=0.0) -> str:
    if voltage:
        cmd = 2 if read else 1
    else:
        cmd = 4 if read else 3
    (intpart, rempart) = str(val).split('.')
    intpart = intpart.zfill(3)
    rempart = rempart.ljust(3, '0')
    devaddr = '0'.zfill(3)
    frame=f"<0{cmd}{intpart}{rempart}{devaddr}>"
    return frame

# Function to send a command to the device
def send_command(command):
    with Serial(
        port=SERIAL_PORT,
        baudrate=BAUD_RATE,
        parity=PARITY_NONE,
        stopbits=STOPBITS_ONE,
        bytesize=EIGHTBITS,
        timeout=TIMEOUT
    ) as ser:
        sleep(0.01)  # Adjust based on baud rate if necessary, this is  to leave a bit of a gap between commands as specified in the protocol document
        ser.write(command.encode('ascii'))
        response = ser.read(13)
        return response.decode('ascii')

def set_voltage(voltage=0.0) -> Tuple[float, str]:
    command = make_frame(read=False, voltage=True, val=voltage)
    response = send_command(command)
    return (voltage, response)

def set_current(device_address=0, current=0.0) -> Tuple[float, str]:
    command = make_frame(read=False, voltage=False, val=current)
    response = send_command(command)
    return (current, response)

def read_voltage() -> Tuple[float, str]:
    command = make_frame(read=True, voltage=True)
    response = send_command(command)
    val = float(response[3:6] + '.' + response[6:9])
    return (val, response)

def read_current(device_address=0) -> Tuple[float, str]:
    command = make_frame(read=True, voltage=False)
    response = send_command(command)
    val = float(response[3:6] + '.' + response[6:9])
    return (val, response)

def power_on() -> Tuple[None, str]:
    print("Powering on", file=stderr)
    response = send_command("<07000000000>")
    return (None, response)

def power_off() -> Tuple[None, str]:
    print("Powering off", file=stderr)
    response = send_command("<08000000000>")
    return (None, response)

def dispatch_request(args):
    if args.off:
        # Turn off the power and return immediately
        (value, response) = power_off()
        print(response, file=stderr)
        return

    if args.on:
        # Turn on the power, wait for 0.1 seconds and then continue with other commands
        (value, response) = power_on()
        print(response, file=stderr)
        sleep(0.1)

    if args.v == ARG_NOT_PRESENT:
        # Argument present but no value specified, so do a read
        (value, response) = read_voltage()
        print(f"V: {value}")
        print(response, file=stderr)
    elif args.v is not None:
        # Argument has a value
        (_, response) = set_voltage(voltage=float(args.v))
        print(response, file=stderr)

    if args.a == ARG_NOT_PRESENT:
        # Argument present but no value specified, so do a read
        (value, response) = read_current()
        print(f"A: {value}")
        print(response, file=stderr)
    elif args.a is not None:
        # Argument has a value
        (_, response) = set_current(current=float(args.a))
        print(response, file=stderr)

    if args.w == ARG_NOT_PRESENT:
        # Argument present but no value specified, so do a read of both V and A
        v = read_voltage()[0]
        c = read_current()[0]
        print(v*c)

# Main function to parse arguments and dispatch requests
def main():
    parser = ArgumentParser(prog="nicepower",
                            description="Control NicePower bench supplies over RS232.  Specify the tty on the command line or in the environment variable NICEPOWER_TTY.  use -v to set or get voltage, -a to set or get current, and -w to read both.  Use -on to enable output and -off to disable output",
                            epilog="If the power is off then you will get zeroes when reading v and c.  w is a simple multiplcation of v and c for convenience")

    parser.add_argument('-on', action='store_true')
    parser.add_argument('-off', action='store_true')
    parser.add_argument('-v', nargs='?', const=ARG_NOT_PRESENT)
    parser.add_argument('-a', nargs='?', const=ARG_NOT_PRESENT)
    parser.add_argument('-w', nargs='?', const=ARG_NOT_PRESENT)
    parser.add_argument('-s', nargs='?', const=ARG_NOT_PRESENT, default=None)
    args = parser.parse_args()

    global SERIAL_PORT
    if args.s == ARG_NOT_PRESENT:
        SERIAL_PORT = environ.get('NICEPOWER_TTY')
    elif args.s is not None:
        SERIAL_PORT = args.s
    if SERIAL_PORT == '' or SERIAL_PORT is None:
        print("Serial port not specified", file=stderr)
        exit(1)
    dispatch_request(args)

if __name__ == "__main__":
    main()
