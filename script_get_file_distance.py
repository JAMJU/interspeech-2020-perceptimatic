#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created december 2019
    by Juliette MILLET
   Script to convert features into distance for the triplets we are interested in
   The files we are dealing with are supposed to have the following indexes: index	#file	onset	offset	#phone	prev-phone	next-phone	speaker
   It can be of h5f format (need to precise it) but otherwise needs to be .fea files, with the indexes above (you need to convert your files with space as separator)
"""
import os
import numpy as np
from dtw_experiments import compute_dtw_norm, compute_dtw
from joblib import Parallel, delayed
import itertools
import sys



def get_frames_rep(folder_soumission, language, filename, time_begin_s, time_end_s):
    f = open(os.path.join(folder_soumission, language,'1s', filename + '.fea'), 'r')
    previous_time = 0
    rep = []
    begin = False
    separator = ' '
    for line in f:
        new_line = [el for el in line.replace('\n', '').split(separator) if el != '']
        #print(new_line)

        current_time = float(new_line[0])
        if not begin:
            if time_begin_s > previous_time and time_begin_s <= current_time:
                begin = True

                rep.append([float(a) for a in new_line[1:]])
        else:
            if not (time_end_s >= previous_time and time_end_s < current_time):
                rep.append([float(a) for a in new_line[1:]])
            else:
                f.close()
                out = np.asarray(rep)
                #print(out.shape)
                return out
        previous_time = current_time
    print('Time error')


class Features_Accessor(object):
    """ Class to decode the hf5 files """
    def __init__(self, times, features):
        self.times = times
        self.features = features

    def get_features_from_raw(self, items):
        features = {}
        for ix, f, on, off in zip([1], items['file'],
                                  items['onset'], items['offset']):
            f=str(f)
            t = np.where(np.logical_and(self.times[f] >= on,
                                        self.times[f] <= off))[0]
            # if len(t) == 0:
            #     raise IOError('No features found for file {}, at '
            #                   'time {}-{}'.format(f, on, off))
            features[ix] = self.features[f][t, :]
        return features

def get_frames_rep_hdf5(file_hdf5, time_hdf5, filename, time_begin_s, time_end_s):
    """ Get right extract of filename between time_begin and time_end"""
    get_features = Features_Accessor(time_hdf5, file_hdf5).get_features_from_raw
    return get_features(dict({'file': [filename], 'onset': [time_begin_s], 'offset': [time_end_s]}))[1]


def get_dictionnary(filename):
    f = open( filename , 'r')
    ind = f.readline().replace('\n', '').split('\t')
    dico_corres = {}
    dico_corres['index'] = ind
    for line in f:
        new_line = line.replace('\n', '').split('\t')
        dico_corres[new_line[ind.index('index')]] = new_line
    f.close()
    return dico_corres

def compute_delta(folder_soumission, dico_corres_english, dico_corres_french, language, indexTGT, indexOTH, indexX, distance, adaptive_average = False):
    ind = dico_corres_english['index']
    if language == 'english':
        dico_corres = dico_corres_english
    else:
        dico_corres = dico_corres_french

    func_to_use = get_frames_rep
    #print(dico_corres[indexTGT][ind.index('#file')])
    TGT = func_to_use(folder_soumission = folder_soumission, language=language,
                         filename=dico_corres[indexTGT][ind.index('#file')],
                         time_begin_s=float(dico_corres[indexTGT][ind.index('onset')]),
                         time_end_s=float(dico_corres[indexTGT][ind.index('offset')]))
    #print(dico_corres[indexOTH][ind.index('#file')])
    OTH = func_to_use(folder_soumission=folder_soumission, language=language,
                         filename=dico_corres[indexOTH][ind.index('#file')],
                         time_begin_s=float(dico_corres[indexOTH][ind.index('onset')]),
                         time_end_s=float(dico_corres[indexOTH][ind.index('offset')]))
    #print(dico_corres[indexX][ind.index('#file')])
    X = func_to_use(folder_soumission=folder_soumission, language=language,
                         filename=dico_corres[indexX][ind.index('#file')],
                         time_begin_s=float(dico_corres[indexX][ind.index('onset')]),
                         time_end_s=float(dico_corres[indexX][ind.index('offset')]))

    if not adaptive_average:
        TGT_X = compute_dtw(x = TGT, y = X, dist_for_cdist=distance, norm_div=True)
        OTH_X = compute_dtw(x = OTH, y = X, dist_for_cdist=distance, norm_div=True)
    else:
        TGT_X = compute_dtw_norm(x=TGT, y=X, dist_for_cdist=distance, norm_div=True)
        OTH_X = compute_dtw_norm(x=OTH, y=X, dist_for_cdist=distance, norm_div=True)
    return OTH_X - TGT_X


def compute_delta_hdf5( dico_corres_english, dico_corres_french, language, indexTGT, indexOTH,
                       indexX, distance, file_hdf5_english, time_hdf5_english, file_hdf5_french, time_hdf5_french,adaptive_average = False):
    func_to_use = get_frames_rep_hdf5
    ind = dico_corres_english['index']
    if language == 'english':
        dico_corres = dico_corres_english
        file_hdf5 = file_hdf5_english
        time_hdf5  = time_hdf5_english
    else:
        dico_corres = dico_corres_french
        file_hdf5 = file_hdf5_french
        time_hdf5 = time_hdf5_french
    TGT = func_to_use(file_hdf5= file_hdf5, time_hdf5 = time_hdf5,
                      filename=dico_corres[indexTGT][ind.index('#file')],
                      time_begin_s=float(dico_corres[indexTGT][ind.index('onset')]),
                      time_end_s=float(dico_corres[indexTGT][ind.index('offset')]))
    # print(dico_corres[indexOTH][ind.index('#file')])
    OTH = func_to_use(file_hdf5= file_hdf5, time_hdf5 = time_hdf5,
                      filename=dico_corres[indexOTH][ind.index('#file')],
                      time_begin_s=float(dico_corres[indexOTH][ind.index('onset')]),
                      time_end_s=float(dico_corres[indexOTH][ind.index('offset')]))
    # print(dico_corres[indexX][ind.index('#file')])
    X = func_to_use(file_hdf5= file_hdf5, time_hdf5 = time_hdf5,
                    filename=dico_corres[indexX][ind.index('#file')],
                    time_begin_s=float(dico_corres[indexX][ind.index('onset')]),
                    time_end_s=float(dico_corres[indexX][ind.index('offset')]))

    if not adaptive_average:
        TGT_X = compute_dtw(x=TGT, y=X, dist_for_cdist=distance, norm_div=True)
        OTH_X = compute_dtw(x=OTH, y=X, dist_for_cdist=distance, norm_div=True)
    else:
        TGT_X = compute_dtw_norm(x=TGT, y=X, dist_for_cdist=distance, norm_div=True)
        OTH_X = compute_dtw_norm(x=OTH, y=X, dist_for_cdist=distance, norm_div=True)
    return OTH_X - TGT_X

def to_parallel(line, ind, folder_soumission, dico_english, dico_french, distance, file_out, adaptive_average = False):
    out = open(file_out, 'a')
    new_line = line.replace('\n', '').split('\t')
    filename = new_line[ind.index('filename')]
    delta = compute_delta(folder_soumission=folder_soumission, dico_corres_english=dico_english,
                          dico_corres_french=dico_french,
                          language='french' if 'FR' in filename else 'english',
                          indexTGT=new_line[ind.index('TGT_item')],
                          indexOTH=new_line[ind.index('OTH_item')], indexX=new_line[ind.index('X_item')],
                          distance=distance, adaptive_average=adaptive_average)
    out.write('\t'.join(new_line) + '\t' + str(delta) + '\n')
    out.close()


def to_parallel_hdf5(line, ind, file_hdf5_english, time_hdf5_english, file_hdf5_french,time_hdf5_french, dico_english, dico_french, distance, file_out, adaptive_average = False):
    out = open(file_out, 'a')
    new_line = line.replace('\n', '').split('\t')
    filename = new_line[ind.index('filename')]
    delta = compute_delta_hdf5(dico_corres_english  = dico_english, dico_corres_french = dico_french, language ='french' if 'FR' in filename else 'english' ,
                               indexTGT=new_line[ind.index('TGT_item')],
                               indexOTH=new_line[ind.index('OTH_item')], indexX=new_line[ind.index('X_item')],
                               distance = distance, file_hdf5_english = file_hdf5_english,
                               time_hdf5_english = time_hdf5_english, file_hdf5_french = file_hdf5_french,
                               time_hdf5_french = time_hdf5_french,adaptive_average = adaptive_average)
    out.write('\t'.join(new_line) + '\t' + str(delta) + '\n')
    out.close()


def compute_all_results(file_list_triplet, folder_soumission, file_out, distance, english_list, french_list, option_hdf5 = False, adaptive_average = False):
    f = open(file_list_triplet, 'r')
    ind = f.readline().replace('\n', '').split('\t')

    dico_english = get_dictionnary(english_list)
    dico_french = get_dictionnary(french_list)
    lines = f.readlines()
    args_f = [line for line in lines]
    f.close()
    print(args_f[0])

    if option_hdf5:
        # we decode the hdf5
        for fili in os.listdir(os.path.join(folder_soumission, 'english')):
            fili = os.path.join(folder_soumission, 'english',  fili)
            feature_group = '/features/'
            times_english = {}
            features_english = {}
            t_english, f_english = h5features.read(fili, feature_group)
            times_english.update(t_english)
            features_english.update(f_english)
            break

        for fili in os.listdir(os.path.join(folder_soumission, 'french')):
            fili = os.path.join(folder_soumission, 'french', fili)
            feature_group = '/features/'
            times_french = {}
            features_french= {}
            t_french, f_french = h5features.read(fili, feature_group)
            times_french.update(t_french)
            features_french.update(f_french)
            break

        Parallel(n_jobs=-1, backend="threading")(
            map(delayed(to_parallel_hdf5), args_f, itertools.repeat(ind, len(args_f)),
                itertools.repeat(features_english, len(args_f)), itertools.repeat(times_english, len(args_f)),
                itertools.repeat(features_french, len(args_f)), itertools.repeat(times_french, len(args_f)),
                itertools.repeat(dico_english, len(args_f)),
                itertools.repeat(dico_french, len(args_f)), itertools.repeat(distance, len(args_f)),
                itertools.repeat(file_out, len(args_f)), itertools.repeat(adaptive_average, len(args_f))))

    # to comment
    #to_parallel(args_f[0], ind, folder_soumission, dico_english, dico_french, distance, file_out, option_hdf5, adaptive_average)
    # to uncomment
    else:

        Parallel(n_jobs=-1, backend="threading")(
            map(delayed(to_parallel), args_f, itertools.repeat(ind, len(args_f)),
                itertools.repeat(folder_soumission, len(args_f)), itertools.repeat(dico_english, len(args_f)),
                itertools.repeat(dico_french, len(args_f)), itertools.repeat(distance, len(args_f)), itertools.repeat(file_out, len(args_f))
                , itertools.repeat(adaptive_average,len(args_f))))


def compute_scores(file_out):
    f = open(file_out, 'r')
    count_french = 0
    count_english = 0
    score_french = 0
    score_english = 0
    for line in f:
        new_line = line.replace('\n', '').split('\t')
        score = float(new_line[-1])
        filename = new_line[0]
        if 'FR' in filename:
            score_french += 0. if score > 0 else 1.
            count_french += 1
        else:
            score_english += 0. if score > 0 else 1.
            count_english += 1
    print('error french:', score_french/float(count_french)*100., 'error english:', score_english/float(count_english)*100.)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to compute ABX delta values for a certain list of triplets, and compute new ABX error')
    parser.add_argument('folder_soumission', metavar='f_do', type=str,
                        help='The file with items you want to check')
    parser.add_argument('file_list', metavar='f_ok', type=str,
                        help='The file with the list of triplets')
    parser.add_argument('file_out', metavar='f_ok', type=str,
                        help='The file out')
    parser.add_argument('distance', metavar='d', type=str,
                        help='distance use in dtw, you have the choice between kl, cosine, and euclidean')
    parser.add_argument('english_list', metavar='f_ok', type=str,
                        help='file with onset and offset of english triplet')
    parser.add_argument('french_list', metavar='f_ok', type=str,
                        help='The file with the onset and offset of french triplet')
    parser.add_argument('hdf5', metavar='h',type = str,
                        help='True if the files are hdf5 format or not, put False otherwise')
    parser.add_argument('adaptive_average', metavar='h', type=str,
                        help='True if use of adaptive average method or not for the dtw, put False otherwise')


    args = parser.parse_args()
    adapt = True if args.adaptive_average == 'True' else False
    hdf5_use = True if args.hdf5 == 'True' else False

    if hdf5_use:
        try:
            import h5features
        except ImportError:
            sys.path.insert(0, os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(
                    os.path.realpath(__file__))))), 'h5features'))
            import h5features

    compute_all_results(file_list_triplet=args.file_list, folder_soumission=args.folder_soumission, file_out=args.file_out,
                        distance= args.distance, english_list=args.english_list,
                        french_list=args.french_list, option_hdf5=hdf5_use, adaptive_average=adapt)


    compute_scores(file_out=args.file_out)