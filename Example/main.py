import time
from keysight_U1242C_class import u1242c
import csv
from datetime import datetime

def excel_ready_timestamp(dt):
    """
    Generate an Excel-ready timestamp from a datetime object.

    :param dt: datetime object
    :return: Excel-ready timestamp as a string
    """
    # Excel timestamp format: 'yyyy-mm-dd hh:mm:ss'
    return dt.strftime('%Y-%m-%d %H:%M:%S')

# Example usage:
now = datetime.now()  # Get current datetime
excel_timestamp = excel_ready_timestamp(now)
print(excel_timestamp)



def main():

    # Your main code goes here
    header = [['Register', 'Resistance, Ohm']]

    dmm = u1242c()
    dmm.init("/dev/ttyUSB1")
    file_name = 'data.csv'
    file = open(file_name, 'w', newline='')
    writer = csv.writer(file)
    writer.writerows(header)

    for i in range(0,1024,1):
        
        dmm_meas = round(float(dmm.get_data()), 3)
        now = datetime.now()  # Get current datetime
        excel_timestamp = excel_ready_timestamp(now)
        meas = [excel_timestamp, dmm_meas]

        writer.writerow(meas)
        file.flush()
        print(f"Time: {excel_ready_timestamp}, meas: {dmm_meas}")


if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
