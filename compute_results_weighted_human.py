#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created april 2020
    by Juliette MILLET
   Script to compute weighted results by human score for each filename
"""


import numpy as np

def get_score_humans(filename, name_results):
    dico_native = {}
    f_in = open(filename, 'r')
    ind = f_in.readline().replace('\n', '').split(',')
    for line in f_in:
        new_line= line.replace('\n', '').split(',')

        if new_line[ind.index('filename')] in dico_native.keys():
            dico_native[new_line[ind.index('filename')]].append((float(new_line[ind.index(name_results)]) + 1)/2) # we put every result in [0,1]
        else:
            dico_native[new_line[ind.index('filename')]] = [(float(new_line[ind.index(name_results)])+ 1)/2]
    # we mean per filename
    new_dico_native = dict()
    val = []
    for f in dico_native.keys():
        val.append( np.asarray(dico_native[f]).mean())
        new_dico_native[f] = np.asarray(dico_native[f]).mean()


    for f in dico_native.keys():

        new_dico_native[f] = new_dico_native[f]

    return new_dico_native

def get_score_model(filename, name_column):
    """
        Return four dico: two (res and std) for french, and same for english
        :param filename:
        :param name_results:
        :return:
        """

    dico_native = {}
    f_in = open(filename, 'r')
    ind = f_in.readline().replace('\n', '').split(',')
    for line in f_in:
        new_line = line.replace('\n', '').split(',')
        dico_native[new_line[ind.index('filename')]] = int(float(new_line[ind.index(name_column)]) > 0)

    return dico_native

def compute_score(dico_humans, dico_model):

    val_french = []
    val_english = []
    result_french = 0
    result_english = 0
    for k in dico_humans.keys():
        if 'FR' in k:
            val_french.append(dico_humans[k])
            result_french += dico_humans[k]*dico_model[k]
        else:
            val_english.append(dico_humans[k])
            result_english += dico_humans[k] * dico_model[k]
    result_french = result_french/sum(val_french)
    result_english = result_english/sum(val_english)

    return result_english, result_french

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to print normal ABX accuracy (unweighted) using perceptimatic database')
    parser.add_argument('file_results', metavar='f_res', type=str,
                        help='file with outputs humans and model(s) \'s distances')
    parser.add_argument('type_human', metavar='column_hum', type=str,
                        help='name of the column to use to reweight (between binarized_answer --between -1 and 1-- and correct_answer --between -3 and 3--')
    parser.add_argument('type_model', metavar='column_mod', type=str,
                        help='columns names of the models you want to evaluate (you can put multiple names separated by a column)')


    args = parser.parse_args()

    dico_human = get_score_humans(filename=args.file_results, name_results=args.type_human)

    for mod in args.type_model.split(','):
        dico_model = get_score_model(filename=args.file_results, name_column=mod)
        en, fr = compute_score(dico_humans=dico_human, dico_model=dico_model)
        print('score', mod)
        print('french', fr, 'english', en)

