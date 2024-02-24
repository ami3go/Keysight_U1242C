# import pyvisa # PyVisa info @ http://PyVisa.readthedocs.io/en/stable/
import time
import serial
import serial.tools.list_ports


def range_check(val, min_val, max_val, val_name):
    if val > max_val:
        print(f"Wrong {val_name}: {val}. Max value should be less than {max_val}")
        return max_val
    elif val < min_val:
        print(f"Wrong {val_name}: {val}. Should be >= {min_val}")
        return min_val
    else:
        return val


class u1242c:
    def __init__(self):
        # Commands Subsystem
        # this is the list of Subsystem commands
        # super(communicator, self).__init__(port="COM10",baudrate=115200, timeout=0.1)
        # print("Communicator init")
        self.cmd = _Storage()
        self.ser = None

    def init(self, com_port, baudrate_var=9600):
        com_port_list = [comport.device for comport in serial.tools.list_ports.comports()]
        if com_port not in com_port_list:
            print("COM port is not found")
            print("Please ensure that USB is connected")
            print(f"Please check COM port Number. Currently it is {com_port} ")
            print(f'Founded COM ports:{com_port_list}')
            return False
        else:
            self.ser = serial.Serial(
                port=com_port,
                baudrate=baudrate_var,
                timeout=0.1
            )
            if not self.ser.isOpen:
                self.ser.open()

            read_back = self._query('*IDN?')
            conf = self.get_conf()
            bat_level = self.get_battery()
            print(f"Connected to: {read_back.strip()}, configured as {conf.strip()}, battery: {bat_level} ")
            bat_level = bat_level.replace("%", "")

            if float(bat_level) <= 30:
                print(f"!!! WARNING !!! LOW BATTERY {bat_level}!!!")
                time.sleep(5)
            if float(bat_level) <= 15:
                print(f"!!! WARNING !!! VERY LOW BATTERY {bat_level}!!!")
                time.sleep(30)
            return True

    def _send(self, txt):
        # will put sending command here
        txt = f'{txt}\r\n'
        # print(f'Sending: {txt}')
        self.ser.write(txt.encode())
        # time.sleep(0.25)

    def _query(self, cmd_srt):
        txt = f'{cmd_srt}\r\n'
        self.ser.reset_input_buffer()
        self.ser.write(txt.encode())
        # print(f'Query: {txt}')
        return_val = self.ser.readline().decode()
        return return_val

    def close(self):
        self.ser.close()
        self.ser = None

    def get_data(self):
        return self._query(self.cmd.measure.req())

    def get_conf(self):
        return self._query(self.cmd.conf.req())

    def get_battery(self):
        return self._query(self.cmd.battely_level.req())

    def reset(self):
        self._send(self.cmd.reset.str())

    def beep(self):
        self._send(self.cmd.beep.str())

    def back_light(self, on_off):
        if on_off == 0:
            self._send(self.cmd.black_light_off.str())
        else:
            self._send(self.cmd.black_light_on.str())



class _req3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def req(self):
        return self.cmd + "?"


class _str3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def str(self, ):
        return self.cmd


class _Storage:
    def __init__(self):
        self.cmd = None
        self.prefix = None
        self.idn = _req3("*IDN")
        self.measure = _req3("FETC")
        self.conf = _req3("CONF")
        self.battely_level = _req3("SYST:BATT")
        self.reset = _str3("*RST")
        self.beep = _str3("SYST:BEEP")
        self.black_light_on = _str3("SYST:BLIT 1")
        self.black_light_off = _str3("SYST:BLIT 0")





if __name__ == '__main__':
    # dev = LOG_34970A()
    # dev.init("COM10")
    # dev.send("COM10 send")
    cmd = _Storage()
    print("")
    print("TOP LEVEL")
    print("*" * 150)
    inst = u1242c()
    inst.init("COM16")
    print(inst._query(cmd.idn.req()))
    print(inst._query(cmd.battely_level.req()))
    print(inst._query(cmd.measure.req()))
    print(inst._query(cmd.conf.req()))
    inst.close()

