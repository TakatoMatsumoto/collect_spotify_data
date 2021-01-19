# -*- coding: utf-8 -*-

import numpy as np
import pandas as pd
import xgboost as xgb
import os
import pickle

targets = ['arousal_mean','valence_mean']

test_x = pd.read_csv('../datasets/test.csv')
sub = test_x

test_x = test_x.drop('song_id',axis=1)
dtest = xgb.DMatrix(test_x)

for target in targets:
    model_path = os.path.join('../model', f'{target}.model')

    try:
        with open(model_path, 'rb') as f:
            model = pickle.load(f)
    except FileNotFoundError:
        print("File not found")

    pred = model.predict(dtest, ntree_limit=model.best_ntree_limit)

    sub = sub.join(pd.DataFrame({f'{target}':pred}))

sub = sub[['song_id','arousal_mean','valence_mean']]
sub_path = '../output/sub' + '.csv'

sub.to_csv(sub_path)

print(sub)