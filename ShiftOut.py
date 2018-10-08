from pyfirmata import Arduino
from time import sleep

OUTPUT = 1

# Adapted from https://www.arduino.cc/en/Tutorial/ShftOut13
# For use with 74HC595 and PyFirmata on Arduino


class ShiftOut:
    def __init__(self, comm, dataPin, latchPin, clockPin):
        self._comm = comm

        self.pins = dict()
        self.pins['dataPin'] = dataPin
        self.pins['latchPin'] = latchPin
        self.pins['clockPin'] = clockPin

    def _digitalWrite(self, pin, val):
        self._comm.digital[pin].write(val)

    def _pinMode(self, pin, mode):
        self._comm.digital[pin].write(mode)

    # Shift 8 bits out MSB first on rising edge of clock
    # clock idling low
    def ShiftOut(self, dataOut):
        self._digitalWrite(self.pins["latchPin"], 0)  # Pull latch to enable data flow

        self._pinMode(self.pins["clockPin"], OUTPUT)

        # Clear everything to prepare shift register
        self._digitalWrite(self.pins["dataPin"], 0)
        self._digitalWrite(self.pins["clockPin"], 0)

        # Loop to check and shift MSB first
        for x in range(0, 8):
            self._digitalWrite(self.pins["clockPin"], 0)
            temp = dataOut & 0x80
            if temp == 0x80:
                pinState = 1
            else:
                pinState = 0

            x = 0
            dataOut = dataOut << 0x01

            self._digitalWrite(self.pins["dataPin"], pinState)
            self._digitalWrite(self.pins["clockPin"], 1)
            self._digitalWrite(self.pins["dataPin"], 0)

        # stop shifting
        self._digitalWrite(self.pins["clockPin"], 0)
        self._digitalWrite(self.pins["latchPin"], 1)  # Change latch to stop data


# Test function to check 74HC595
if __name__ == "__main__":
    comm = Arduino('COM3')
    monitor = ShiftOut(comm, 11, 8, 12)
    monitor.ShiftOut(0x00)
    # monitor._pinMode(2, 1)
    while True:

        '''
        monitor._digitalWrite(2, 0)
        sleep(1)
        monitor._digitalWrite(2, 1)
        sleep(1)
        '''

        monitor.ShiftOut(0x00)
        print(b'0x00')
        sleep(1)

        monitor.ShiftOut(0x01)  # 00001 b
        print(b'0x01')
        sleep(1)

        monitor.ShiftOut(0x03)  # 0011 b
        print(b'0x03')
        sleep(1)

        monitor.ShiftOut(0x05)  # 0101 b
        print(b'0x05')
        sleep(1)

        monitor.ShiftOut(0x09)  # 1001 b
        print(b'0x09')
        sleep(1)
