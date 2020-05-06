#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Created january 2020
    by Juliette MILLET
    script to take a bunch of csv and merge them
"""

def get_distance_csv(csv_to_get):
    f = open(csv_to_get, 'r')
    ind = ['filename','TGT','OTH','prev_phone','next_phone','TGT_item','OTH_item','X_item','TGT_first','speaker_tgt_oth','speaker_x','distance']
    dico_dist = {}
    for line in f:
        new_line = line.replace('\n', '').split('\t')
        dico_dist[new_line[ind.index('filename')]] = new_line[ind.index('distance')]

    return dico_dist

def add_distance(filename,  list_name, list_dico, filename_out):
    f = open(filename, 'r')
    ind = f.readline().replace('\n', '').split(',')
    f_out = open(filename_out, 'w')
    f_out.write(','.join(ind + ['mod_' + name.replace(' ', '_')  for name in list_name]) + '\n')

    for line in f:
        new_line = line.replace('\n', '').split(',')
        file = new_line[ind.index('filename')]
        count = 0
        for dico in list_dico:
            new_line = new_line + [str(dico[file])]
            count += 1
        f_out.write(','.join(new_line) + '\n')


def merge_all_distance_files(file_to_add, file_humans, file_out, name_column):
    list_dico = []
    list_names = []
    list_dico.append(get_distance_csv(file_to_add))
    list_names.append(name_column)
    add_distance(filename=file_humans, list_name = list_names, list_dico=list_dico, filename_out=file_out)

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(
        description='script to compute ABX distances for a certain list of triplets')
    parser.add_argument('file_to_add', metavar='f_add', type=str,
                        help='file with model\'s delta values')
    parser.add_argument('name_column', metavar='n_add', type=str,
                        help='name of the column you add')
    parser.add_argument('file_humans', metavar='f_hum', type=str,
                        help='The file with humans results')
    parser.add_argument('file_out', metavar='f_out', type=str,
                        help='The file out')


    args = parser.parse_args()

    merge_all_distance_files(file_to_add=args.folder_distances, file_humans=args.file_humans, file_out=args.file_out, name_column=args.name_column)