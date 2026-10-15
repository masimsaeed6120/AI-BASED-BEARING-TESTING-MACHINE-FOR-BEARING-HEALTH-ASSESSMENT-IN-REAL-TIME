
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B

bus = smbus2.SMBus(1)

bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

print("MPU6050 connected.")
print("Reading acceleration...")

while True:
    data = bus.read_i2c_block_data(MPU6050_ADDR, ACCEL_XOUT_H, 6)

    ax = (data[0] << 8) | data[1]
    ay = (data[2] << 8) | data[3]
    az = (data[4] << 8) | data[5]

    if ax >= 32768:
        ax -= 65536
    if ay >= 32768:
        ay -= 65536
    if az >= 32768:
        az -= 65536

    ax_g = ax / 16384.0
    ay_g = ay / 16384.0
    az_g = az / 16384.0

    print(f"Ax: {ax_g:.3f} g | Ay: {ay_g:.3f} g | Az: {az_g:.3f} g")

    time.sleep(0.01)