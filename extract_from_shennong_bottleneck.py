#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created january 2020
    by Juliette MILLET
   Script to extract bottleneck features with shennong
"""

from shennong.audio import Audio
from shennong.features.processor.bottleneck import BottleneckProcessor
import os
import numpy as np

def transform_all_wavs(folder_wav, type, folder_out): # will output [timexdim}
    processor = BottleneckProcessor(weights=type)
    count = 0
    for file in os.listdir(folder_wav):
        if count % 500 == 0:
            print(count)
        count += 1
        if not file.endswith('.wav'):
            continue
        audio = Audio.load(os.path.join(folder_wav, file))

        features = processor.process(audio)
        #print(features.shape)
        #print(features)
        np.savetxt(fname = os.path.join(folder_out,file[:-4] + '.csv'), X=features._data)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to extract multilingual bottleneck features with shennong package and have them as csv file with the right format for ABX computations')
    parser.add_argument('folder_input', metavar='f_inp', type=str,
                        help='folder where the wavs are')
    parser.add_argument('folder_out', metavar='f_out', type=str,
                        help='folder where to put the output')
    parser.add_argument('type_net', metavar='type', type=str,
                        help='type of net you want to use, available:FisherMono, FisherTri, BabelMulti')


    args = parser.parse_args()

    transform_all_wavs(folder_wav=args.folder_in, type=args.type_net, folder_out=args.folder_out)