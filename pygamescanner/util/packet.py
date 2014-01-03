# coding=utf-8

import StringIO
import struct

__all__ = ["Packet"]


class Packet(StringIO.StringIO):
    def put_byte(self, val):
        self.write(struct.pack('<B', val))

    def get_byte(self):
        return struct.unpack('<B', self.read(1))[0]

    def put_short(self, val):
        self.write(struct.pack('<h', val))

    def get_short(self):
        return struct.unpack('<h', self.read(2))[0]

    def put_long(self, val):
        self.write(struct.pack('<l', val))

    def get_long(self):
        return struct.unpack('<l', self.read(4))[0]

    def put_long_long(self, val):
        self.write(struct.pack('<Q', val))

    def get_long_long(self):
        return struct.unpack('<Q', self.read(8))[0]

    def put_float(self, val):
        self.write(struct.pack('<f', val))

    def get_float(self):
        return struct.unpack('<f', self.read(4))[0]

    def put_string(self, val):
        self.write(val + '\x00')

    def get_string(self):
        val = self.getvalue()
        start = self.tell()
        end = val.index('\0', start)
        val = val[start:end]
        self.seek(end + 1)
        return val
