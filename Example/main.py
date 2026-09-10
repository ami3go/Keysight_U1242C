import csv
from datetime import datetime

from keysight_u1242c import U1242C


def excel_ready_timestamp(dt):
    """
    Generate an Excel-ready timestamp from a datetime object.

    :param dt: datetime object
    :return: Excel-ready timestamp as a string
    """
    # Excel timestamp format: 'yyyy-mm-dd hh:mm:ss'
    return dt.strftime('%Y-%m-%d %H:%M:%S')


def main():
    header = [['Timestamp', 'Resistance, Ohm']]

    file_name = 'data.csv'
    file = open(file_name, 'w', newline='')
    writer = csv.writer(file)
    writer.writerows(header)

    with U1242C("/dev/ttyUSB1") as dmm:
        for _ in range(1024):
            dmm_meas = round(dmm.get_data(), 3)
            excel_timestamp = excel_ready_timestamp(datetime.now())
            writer.writerow([excel_timestamp, dmm_meas])
            file.flush()
            print(f"Time: {excel_timestamp}, meas: {dmm_meas}")

    file.close()


if __name__ == "__main__":
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
