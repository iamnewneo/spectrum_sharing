import h5py
import numpy as np
import pandas as pd
from tqdm import tqdm
import scipy.signal as sig
from scipy.fft import fft, fftfreq
from sklearn.ensemble import RandomForestClassifier

from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score, f1_score, auc, roc_curve
from joblib import Parallel, delayed


def preprocess_signal(x):
    i = np.array([real[0] for real in x])
    q = np.array([imag[1] for imag in x])
    i_max = i.max()
    q_max = q.max()
    i_min = i.min()
    q_min = q.min()
    i_mean = i.mean()
    q_mean = q.mean()
    i_range = i_max - i_min
    q_range = q_max - q_min
    num_pts_away_q = (q > 1e-6).sum()
    num_pts_away_q += (q < -1e-6).sum()
    num_pts_away_i = (i > 1e-6).sum()
    num_pts_away_i += (i < -1e-6).sum()
    temp = {
        "i_max": i_max,
        "q_max": q_max,
        "i_min": i_min,
        "q_min": q_min,
        "i_mean": i_mean,
        "q_mean": q_mean,
        "i_range": i_range,
        "q_range": q_range,
        "num_pts_away_q": num_pts_away_q,
        "num_pts_away_i": num_pts_away_i,
    }
    return temp


def get_matlab_arrays(file_path):
    arrays = {}
    with h5py.File(file_path, "r") as f:
        for k, v in f.items():
            arrays[k] = np.array(v)


arrays = get_matlab_arrays(file_path)

y = arrays["group1_radarStatusSubset_1"]
y = y.reshape(200)


X_preprocessed = Parallel(n_jobs=4)(
    delayed(preprocess_signal)(x) for x in tqdm(arrays["group1_waveformSubset_1"])
)
df = pd.DataFrame(X_preprocessed)
