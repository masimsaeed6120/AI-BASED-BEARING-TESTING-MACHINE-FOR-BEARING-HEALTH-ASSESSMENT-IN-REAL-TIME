import pandas as pd
import numpy as np
import glob
import os
from scipy.stats import kurtosis, skew
from scipy.fft import rfft, rfftfreq


SAMPLE_RATE = 500

folders = {
    "healthy": 0,
    "degraded": 1,
    "faulty": 2
}

output_file = "features.csv"


def extract_features(signal):

    mean = np.mean(signal)
    std = np.std(signal)

    rms = np.sqrt(np.mean(signal ** 2))

    peak = np.max(np.abs(signal))

    peak_to_peak = np.max(signal) - np.min(signal)

    crest_factor = peak / rms if rms != 0 else 0

    kurtosis_value = kurtosis(signal)

    if not np.isfinite(kurtosis_value):
        kurtosis_value = 0.0

    skewness_value = skew(signal)

    if not np.isfinite(skewness_value):
        skewness_value = 0.0


    fft_values = np.abs(rfft(signal))

    frequencies = rfftfreq(len(signal), 1 / SAMPLE_RATE)


    fft_values[0] = 0

    dominant_frequency = frequencies[np.argmax(fft_values)]

    spectral_energy = np.sum(fft_values ** 2)

    return [
        mean,
        std,
        rms,
        peak,
        peak_to_peak,
        crest_factor,
        kurtosis_value,
        skewness_value,
        dominant_frequency,
        spectral_energy
    ]



all_features = []

for folder, label in folders.items():

    pattern = f"data/{folder}/*.csv"

    files = sorted(glob.glob(pattern))

    print("\n====================================")
    print("CLASS:", folder.upper())
    print("LABEL:", label)
    print("====================================")

    for file in files:

        if os.path.basename(file) == "healthy_test_500hz.csv":
            continue

        print("Processing:", file)

        df = pd.read_csv(file)

        row = {
            "file": os.path.basename(file),
            "label": label
        }

        for axis in ["ax", "ay", "az"]:

            features = extract_features(df[axis].values)

            names = [
                "mean",
                "std",
                "rms",
                "peak",
                "peak_to_peak",
                "crest_factor",
                "kurtosis",
                "skewness",
                "dominant_frequency",
                "spectral_energy"
            ]

            for name, value in zip(names, features):

                row[f"{axis}_{name}"] = value

        all_features.append(row)



features_df = pd.DataFrame(all_features)

features_df.to_csv(output_file, index=False)


print("Total recordings:", len(features_df))
print("Total features:", len(features_df.columns))

print("\nClass distribution:")
print(features_df["label"].value_counts().sort_index())

print("\nSaved as:")
print(output_file)