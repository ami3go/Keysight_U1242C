import src.keysight_U1242C_class as dev
import datetime
import time


if __name__ == "__main__":
    try:
        inst = dev.com_interface()
        inst.init("COM22")

        inst.back_light(1)
        time.sleep(5)
        inst.back_light(0)


        for i in range(1000):
            temp = float(inst.get_data())
            txt = f"{datetime.datetime.now()} Temperature: {temp} degC"
            print(txt)
            time.sleep(2)

    except KeyboardInterrupt:
        print("Test finished")
        inst.close()