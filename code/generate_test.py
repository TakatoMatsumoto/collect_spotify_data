# -*- coding: utf-8 -*-

from pathlib import Path
import pandas as pd
import numpy as np
import librosa
from librosa import feature, beat, onset, effects
import os
from glob import glob
import csv

import warnings
warnings.simplefilter('ignore')

def get_feature_vector(y, sr, S, song_id):

    fn_list_i = [
    feature.chroma_stft,
    feature.spectral_centroid,
    feature.spectral_bandwidth,
    feature.spectral_rolloff,
    feature.chroma_cqt,
    feature.chroma_cens,
    feature.melspectrogram,
    feature.tonnetz,
    feature.rhythm.tempogram,
    feature.mfcc,
    onset.onset_detect,
    ]

    fn_list_ii = [
    effects.harmonic,
    effects.percussive,
    feature.rms,
    feature.zero_crossing_rate,
    ]

    feat1 = [np.mean(funct(y, sr)) for funct in fn_list_i]
    feat2 = [np.mean(funct(y)) for funct in fn_list_ii]
    feat3 = [np.std(funct(y, sr)) for funct in fn_list_i]
    feat4 = [np.std(funct(y)) for funct in fn_list_ii]

    feature_vector =  [song_id] + feat1 + feat2 + feat3 + feat4
    return feature_vector

if __name__ == '__main__':
    audio_path = "../audio" 
    audio_files = glob(audio_path + '/*.mp3')

    features = []
    print("Generating test features...")
    for file in audio_files:
        song_id = Path(file).stem
        print(song_id)
        y , sr = librosa.load(file, sr=None)
        S = np.abs(librosa.stft(y))
        feature_vector = get_feature_vector(y, sr, S, song_id)
        features.append(feature_vector)

    output = '../datasets/features_lo_fi' + '.csv'

    header = [
    'chroma_stft',
    'spectral_centroid',
    'spectral_bandwidth',
    'spectral_rolloff',
    'chroma_cqt',
    'chroma_cens',
    'melspectrogram',
    'tonnetz',
    'rhythm.tempogram',
    'mfcc',
    'onset_detect',
    'harmonic',
    'percussive',
    'rms',
    'zero_crossing_rate',
    ]

    header = ['song_id'] + [feat_name + '_mean' for feat_name in header] + [feat_name + '_std' for feat_name in header]

    with open(output, '+w') as f:
        csv_writer = csv.writer(f, delimiter = ',')
        csv_writer.writerow(header)
        csv_writer.writerows(features)

    print("Generating Done")