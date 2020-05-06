#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created april 2020
    by Juliette MILLET
   Script to print new ABX accuracy scores for models (using Perceptimatic database)
"""

def get_score_model(filename, name_column):
    dico_native = {}
    f_in = open(filename, 'r')
    ind = f_in.readline().replace('\n', '').split(',')
    for line in f_in:
        new_line = line.replace('\n', '').split(',')
        dico_native[new_line[ind.index('filename')]] = float(int(float(new_line[ind.index(name_column)]) > 0))

    return dico_native

def compute_score( dico_model):
    val_french = []
    val_english = []
    result_french = 0
    result_english = 0
    for k in dico_model.keys():
        if 'FR' in k:
            val_french.append(1)
            result_french += dico_model[k]
        else:
            val_english.append(1)
            result_english += dico_model[k]
    result_french = result_french/sum(val_french)
    result_english = result_english/sum(val_english)

    return result_english, result_french

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to print normal ABX accuracy (unweighted) using perceptimatic database')
    parser.add_argument('file_results', metavar='f_res', type=str,
                        help='file with outputs humans and model(s) \'s distances')
    parser.add_argument('type_model', metavar='column_mod', type=str,
                        help='columns names of the models you want to evaluate (you can put multiple names separated by a column)')


    args = parser.parse_args()



    for mod in args.type_model.split(','):
        dico_model = get_score_model(filename=args.file_results, name_column=mod)
        en, fr = compute_score(dico_model=dico_model)
        print('score', mod)
        print('french', fr, 'english', en)