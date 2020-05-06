#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created january 2020
    by Juliette MILLET
    script to compute 95 confidence intervals of the log likelihood for each model
"""
import pandas as pd
import numpy as np


def mean_confidence_interval(data):
    a = np.asarray(data)
    n = len(a)
    print('len', n)
    m = np.mean(a)
    print(m)
    sorted_estimates = np.sort(a)
    conf_interval = [sorted_estimates[int(0.025 * n)], sorted_estimates[int(0.975 * n)]]
    print(conf_interval)
    return m, conf_interval[0], conf_interval[1]

def output_mean_and_confidence_interval_for_log(filename, file_output):
    all = pd.read_csv(filename, sep=',', encoding='utf-8')
    list_model = list(all)[1:]
    print(list_model)
    for mod in list_model:
        all = all[all[mod].notna()]

    out = open(file_output, 'w')
    out.write('model,mean,bound_minus,bound_sup\n')
    for model in list_model:
        print(model)
        values = all[model].values
        mean, bound_minus, bound_sup = mean_confidence_interval(data = values)
        out.write(','.join([model, str(mean), str(bound_minus), str(bound_sup)]) + '\n')
    out.close()




if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to analyze output from humans vs model\'s outputs and sample the results')
    parser.add_argument('file_result_it', metavar='f_do', type=str,
                        help='file with log lik of models')
    parser.add_argument('outfile', metavar='f_do', type=str,
                        help='file to output with mean and interval')

    args = parser.parse_args()

    output_mean_and_confidence_interval_for_log(filename=args.file_result_it, file_output=args.outfile)
