import smbus2
import time
import csv
import os

BUS = 1
ADDRESS = 0x68

PWR_MGMT_1 = 0x6B
SMPLRT_DIV = 0x19
CONFIG = 0x1A
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(BUS)


bus.write_byte_data(ADDRESS, PWR_MGMT_1, 0x00)


bus.write_byte_data(ADDRESS, CONFIG, 0x02)


bus.write_byte_data(ADDRESS, SMPLRT_DIV, 0x01)


bus.write_byte_data(ADDRESS, ACCEL_CONFIG, 0x00)

sample_rate = 500
duration = 10
total_samples = sample_rate * duration

data_folder = "data/degraded"

os.makedirs(data_folder, exist_ok=True)

file_number = 1

while True:

    filename = f"{data_folder}/degraded_{file_number}.csv"

    if not os.path.exists(filename):
        break

    file_number += 1


start_time = time.perf_counter()

with open(filename, "w", newline="") as file:

    writer = csv.writer(file)

    writer.writerow([
        "timestamp",
        "ax",
        "ay",
        "az"
    ])

    next_sample_time = start_time

    for i in range(total_samples):

        while time.perf_counter() < next_sample_time:
            pass

        data = bus.read_i2c_block_data(
            ADDRESS,
            ACCEL_XOUT_H,
            6
        )

        ax_raw = (data[0] << 8) | data[1]
        ay_raw = (data[2] << 8) | data[3]
        az_raw = (data[4] << 8) | data[5]

        if ax_raw >= 32768:
            ax_raw -= 65536

        if ay_raw >= 32768:
            ay_raw -= 65536

        if az_raw >= 32768:
            az_raw -= 65536

        ax = ax_raw / 16384.0
        ay = ay_raw / 16384.0
        az = az_raw / 16384.0

        timestamp = time.perf_counter() - start_time

        writer.writerow([
            timestamp,
            ax,
            ay,
            az
        ])

        next_sample_time += 1.0 / sample_rate



end_time = time.perf_counter()

actual_duration = end_time - start_time
actual_rate = total_samples / actual_duration

print()

print("RECORDING COMPLETE")
print("Saved:", filename)
bus.close()