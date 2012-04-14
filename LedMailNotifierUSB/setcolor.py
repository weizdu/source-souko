#!/usr/bin/env python
import sys

class MailNotifier:
    def __init__(self):
        import os
        if os.name == 'posix':
            self.dev=UsbDevice(0x1294, 0x1320)
        elif os.name == 'nt':
            self.dev=UsbDeviceWin(0x1294, 0x1320)
        else:
            sys.stderr.write("for Windows or linux\n")
            sys.exit(1)
            
        self.dev.open()

    def setColor(self, color):
        self.dev.write(color)

class UsbDevice:
    def __init__(self, vendor_id, product_id):
        import usb
        busses = usb.busses()
        self.handle = None
        count = 0
        for bus in busses:
                devices = bus.devices
                for dev in devices:
                    if dev.idVendor==vendor_id and dev.idProduct==product_id:
                        self.dev = dev
                        self.conf = self.dev.configurations[0]
                        self.intf = self.conf.interfaces[0][0]
                        self.endpoints = []
                        for endpoint in self.intf.endpoints:
                            self.endpoints.append(endpoint)
                        return
        sys.stderr.write("No mail notifier found\n")

    def open(self):
        if self.handle:
            self.handle = None
        try:
            self.handle = self.dev.open()
            self.handle.detachKernelDriver(0)
            self.handle.detachKernelDriver(1)
            self.handle.setConfiguration(self.conf)
            self.handle.claimInterface(self.intf)
            self.handle.setAltInterface(self.intf)

            self.dev.handle.reset()

            return True
        except:
            return False
        
    def makeData(self, color):
        return (color, 0, 0, 0, 0)

    def write(self, color):
        self.handle.interruptWrite(0x02, self.makeData(color), 1000)

class UsbDeviceWin:
    def __init__(self, vendor_id, product_id):
        from pywinusb import hid

        devices = hid.HidDeviceFilter( vendor_id, product_id ).get_devices()
        self.handle = None

        self.dev = devices[0]

        if self.dev is None:
            sys.stderr.write("No mail notifier found\n")
            sys.exit( 1 )
            
#        self.conf = self.dev.configurations[0]
#        self.intf = self.conf.interfaces[0][0]
#        self.endpoints = []
#        for endpoint in self.intf.endpoints:
#            self.endpoints.append(endpoint)
        return

    def open(self):
        if self.handle:
            self.handle = None
        try:
            self.handle = self.dev.open()
            self.report = self.dev.find_output_reports()[ 0 ]
            self.handle.detachKernelDriver(0)
            self.handle.detachKernelDriver(1)
            self.handle.setConfiguration(self.conf)
            self.handle.claimInterface(self.intf)
            self.handle.setAltInterface(self.intf)
            return True
        except:
            print sys.exc_info()[0], sys.exc_info()[1]
            return False
    
    def write(self, color):
        self.report[ 0xff000001 ][ 0 ] = color
        self.report.send()

def main(argv):
    if len(argv) != 2:
        sys.stderr.write("Usage : %s color_number\n" % argv[0])
    else:
        m = MailNotifier()
        m.setColor(int(argv[1]))

if __name__=="__main__":
    main(sys.argv)
