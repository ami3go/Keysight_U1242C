# import pyvisa # PyVisa info @ http://PyVisa.readthedocs.io/en/stable/
import time

import serial
import serial.tools.list_ports


def range_check(val, min, max, val_name):
    if val > max:
        print(f"Wrong {val_name}: {val}. Max value should be less then {max}")
        val = max
    if val < min:
        print(f"Wrong {val_name}: {val}. Should be >= {min}")
        val = min
    return val


class com_interface:
    def __init__(self):
        # Commands Subsystem
        # this is the list of Subsystem commands
        # super(communicator, self).__init__(port="COM10",baudrate=115200, timeout=0.1)
        # print("Communicator init")
        self.cmd = storage()
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

            read_back = self.query('*IDN?')
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

    def send(self, txt):
        # will put sending command here
        txt = f'{txt}\r\n'
        # print(f'Sending: {txt}')
        self.ser.write(txt.encode())
        # time.sleep(0.25)

    def query(self, cmd_srt):
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
        return self.query(self.cmd.measure.req())

    def get_conf(self):
        return self.query(self.cmd.conf.req())

    def get_battery(self):
        return self.query(self.cmd.battely_level.req())

    def reset(self):
        self.send(self.cmd.reset.str())

    def beep(self):
        self.send(self.cmd.beep.str())

    def back_light(self, on_off):
        if on_off == 0:
            self.send(self.cmd.black_light_off.str())
        else:
            self.send(self.cmd.black_light_on.str())



class req3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def req(self):
        return self.cmd + "?"


class str3:
    def __init__(self, prefix):
        self.prefix = prefix
        self.cmd = self.prefix

    def str(self, ):
        return self.cmd


class storage:
    def __init__(self):
        self.cmd = None
        self.prefix = None
        self.idn = req3("*IDN")
        self.measure = req3("FETC")
        self.conf = req3("CONF")
        self.battely_level = req3("SYST:BATT")
        self.reset = str3("*RST")
        self.beep = str3("SYST:BEEP")
        self.black_light_on = str3("SYST:BLIT 1")
        self.black_light_off = str3("SYST:BLIT 0")





if __name__ == '__main__':
    # dev = LOG_34970A()
    # dev.init("COM10")
    # dev.send("COM10 send")
    cmd = storage()
    print("")
    print("TOP LEVEL")
    print("*" * 150)
    inst = com_interface()
    inst.init("COM16")
    print(inst.query(cmd.idn.req()))
    print(inst.query(cmd.battely_level.req()))
    print(inst.query(cmd.measure.req()))
    print(inst.query(cmd.conf.req()))
    inst.close()

