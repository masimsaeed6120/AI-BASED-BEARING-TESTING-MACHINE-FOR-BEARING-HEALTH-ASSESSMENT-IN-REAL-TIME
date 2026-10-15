import time
import numpy as np
import joblib

from smbus2 import SMBus
from scipy.stats import kurtosis, skew
from scipy.fft import rfft, rfftfreq


BUS = 1
ADDRESS = 0x68

PWR_MGMT_1 = 0x6B
CONFIG = 0x1A
SMPLRT_DIV = 0x19
ACCEL_CONFIG = 0x1C
ACCEL_XOUT_H = 0x3B

SAMPLE_RATE = 500
WINDOW_SECONDS = 10
SAMPLES = SAMPLE_RATE * WINDOW_SECONDS


# Load trained model

model = joblib.load("models/random_forest_model.pkl")

print("Random Forest model loaded.")
print("")


def read_acceleration(bus):
    data = bus.read_i2c_block_data(
        ADDRESS,
        ACCEL_XOUT_H,
        6
    )

    ax = (data[0] << 8) | data[1]
    ay = (data[2] << 8) | data[3]
    az = (data[4] << 8) | data[5]

    if ax >= 32768:
        ax -= 65536

    if ay >= 32768:
        ay -= 65536

    if az >= 32768:
        az -= 65536

    ax = ax / 16384.0
    ay = ay / 16384.0
    az = az / 16384.0

    return ax, ay, az


def extract_features(signal, sample_rate):

    mean_value = np.mean(signal)
    std_value = np.std(signal)
    rms_value = np.sqrt(np.mean(signal ** 2))
    peak_value = np.max(np.abs(signal))
    peak_to_peak = np.ptp(signal)

    if rms_value != 0:
        crest_factor = peak_value / rms_value
    else:
        crest_factor = 0

    kurtosis_value = kurtosis(signal)
    skewness_value = skew(signal)

    fft_values = np.abs(rfft(signal))
    frequencies = rfftfreq(len(signal), 1 / sample_rate)

    fft_values[0] = 0

    dominant_frequency = frequencies[
        np.argmax(fft_values)
    ]

    spectral_energy = np.sum(fft_values ** 2)

    return [
        mean_value,
        std_value,
        rms_value,
        peak_value,
        peak_to_peak,
        crest_factor,
        kurtosis_value,
        skewness_value,
        dominant_frequency,
        spectral_energy
    ]



# Collect vibratio
print("Starting real-time test...")
print("Keep the bearing running normally.")
print("Collecting 10 seconds of vibration data...")
print("")

bus = SMBus(BUS)

bus.write_byte_data(ADDRESS, PWR_MGMT_1, 0x00)
bus.write_byte_data(ADDRESS, CONFIG, 0x02)
bus.write_byte_data(ADDRESS, SMPLRT_DIV, 0x01)
bus.write_byte_data(ADDRESS, ACCEL_CONFIG, 0x00)

ax_data = []
ay_data = []
az_data = []

next_time = time.perf_counter()

for i in range(SAMPLES):

    ax, ay, az = read_acceleration(bus)

    ax_data.append(ax)
    ay_data.append(ay)
    az_data.append(az)

    next_time += 1 / SAMPLE_RATE

    sleep_time = next_time - time.perf_counter()

    if sleep_time > 0:
        time.sleep(sleep_time)

bus.close()

print("Data collection complete.")
print("")



ax_data = np.array(ax_data)
ay_data = np.array(ay_data)
az_data = np.array(az_data)



features = []

for signal in [ax_data, ay_data, az_data]:

    features.extend(
        extract_features(signal, SAMPLE_RATE)
    )



# Make prediction

features = np.array(features).reshape(1, -1)

prediction = model.predict(features)[0]

probabilities = model.predict_proba(features)[0]



# Display result

class_names = {
    0: "HEALTHY",
    1: "DEGRADED",
    2: "FAULTY"
}


print("REAL-TIME PREDICTION")


print("Prediction:", class_names[prediction])

print("")
print("Prediction probabilities:")

print("Healthy:  ", round(probabilities[0] * 100, 2), "%")
print("Degraded: ", round(probabilities[1] * 100, 2), "%")
print("Faulty:   ", round(probabilities[2] * 100, 2), "%")

