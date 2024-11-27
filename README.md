# NicePower-Serial

Serial control of nicepower bench supplies from the command line.

Requires pyserial but no other dependencies.  so pip install pyserial and you are good to go.

I've also tidied up the rather inaccurate manufacturer spec.

Usage is:

```sh
nicepower.py [-s <serial port>] [-v [<volts>]] [-a [<amps>]] [-on] [-off] [-w]>
```

The serial port can be set as NICEPOWER_SERIAL in your environment as well
