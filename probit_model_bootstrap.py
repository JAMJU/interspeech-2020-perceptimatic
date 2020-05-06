#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created january 2020
    by Juliette MILLET
    script to compute a probit model based on output file with one line = one stimuli-individual and
    with a sampling of answers to have a equilibrated probit model. all languages together
"""

import pandas as pd
from statsmodels.formula.api import probit
import random as rd

def get_dico_corres_file(data_file):
    dico ={}
    f = open(data_file, 'r')
    ind = f.readline().replace('\n', '').split(',')
    count = 0
    for line in f:

        newline = line.replace('\n', '').split(',')
        if newline[ind.index('filename')] in dico:
            dico[newline[ind.index('filename')]].append(count)
        else:
            dico[newline[ind.index('filename')]] = [count]
        count += 1
    f.close()
    return dico


def sample_lines(dico_line_files):
    # we sample three results per filename
    list_lines = []
    for filename in dico_line_files:
        list_lines = list_lines + [dico_line_files[filename][rd.randrange(0,stop= len(dico_line_files[filename]))],
                                   dico_line_files[filename][rd.randrange(0, stop=len(dico_line_files[filename]))],
                                   dico_line_files[filename][rd.randrange(0, stop=len(dico_line_files[filename]))]]
    return list_lines




def model_probit_binarized(data_file,  model, lines_sampled): # for the model, you have to add the +

    data = data_file.copy()
    data = data.iloc[lines_sampled]

    data['binarized_answer']  = (data['binarized_answer']+ 1.)/2 # we transform -1 1 into 0 1


    # we fit the probit model
    # we predict human answers thanks to delta values, which stimulus was heard first, how many stimuli were heard (+ intercept for individual and language)
    model_probit = probit("binarized_answer ~ TGT_first_code + nb_stimuli + C(individual)" + model + "*constant_fr" + model + "*constant_eng + constant_fr + constant_eng", data)
    result_probit = model_probit.fit()
    return model_probit.loglike(result_probit.params)

def iteration_model(filename, nb_it, outfile):
    dico_lines = get_dico_corres_file(filename)

    f = open(filename, 'r')
    ind = f.readline().replace('\n', '').split(',')
    list_names = [name for name in ind[ind.index('language_code') + 1:]]
    f.close()

    out = open(outfile, 'w')
    out.write('nb,' + ','.join(list_names) + '\n')
    data = pd.read_csv(filename, sep=',', encoding='utf-8')

    # we create constants for the different intercept and for the interaction language and use of delta
    data['constant_fr'] = pd.Series([1. if data.iloc[x, 1] == 'french' else 0. for x in range(len(data.index)) ], index=data.index)
    data['constant_eng'] = pd.Series([1. if data.iloc[x, 1] == 'english' else 0. for x in range(len(data.index))], index=data.index)
    for i in range(nb_it):
        out.write(str(i) + ',')
        # we sample
        list_sampled = sample_lines(dico_lines)
        list_log = []
        for mod in list_names:
            print(mod)
            log = model_probit_binarized(data_file=data, model='+ ' + mod, lines_sampled=list_sampled)
            list_log.append(str(log))
        out.write(','.join(list_log))

        out.write('\n')



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to analyze output from humans vs model\'s outputs and sample the results. '
                    'This script might crash when the probit model cannot converge, you will need to '
                    'relaunch it with a different output file to obtain the amount of iteration wanted')
    parser.add_argument('file_models_and_humans', metavar='files_models_and_humans', type=str,
                        help='file with outputs humans and models distances')
    parser.add_argument('outfile', metavar='f_do', type=str,
                        help='file with log likelihood answers')
    parser.add_argument('nb_it', metavar='f_do', type=int,
                        help='number of sampling')

    args = parser.parse_args()


    iteration_model(filename=args.file_models_and_humans, nb_it=args.nb_it, outfile=args.outfile)