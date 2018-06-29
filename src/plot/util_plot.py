#!/usr/bin/env python
# Plot results of DEMUD selections for comparison

import sys, os
import numpy as np
import csv
import matplotlib.pyplot as plt
import math

color_list = [
	'xkcd:green',
	'xkcd:blue',
	'xkcd:red',
	'xkcd:green',
	'xkcd:blue',
	'xkcd:red',
	'xkcd:purple',
	'xkcd:brown',
	'xkcd:light blue',
	'xkcd:pink',
	'xkcd:teal',
	'xkcd:orange',
	'xkcd:light green',
	'xkcd:magenta',
	'xkcd:yellow',
	'xkcd:grey',
	'xkcd:violet',
	'xkcd:dark green',
	'xkcd:cyan',
	'xkcd:hot pink',
	'xkcd:aquamarine',
	'xkcd:royal purple']
shape_list = ['.']*3 + ['x']*3 + ['+']*3
line_list = ['-']*3 + ['--']*3

def calc_auc(x_list, y_list, n_sel, perfect_auc):
    # Start with 0 items discovered in all rounds
    disc_list = [0] * n_sel
    for (x,y) in zip(x_list, y_list):
        # Update from round x going forward, y discoveries
        disc_list[x:] = [y] * (n_sel-x)
    auc = sum(disc_list) * 100.0 / perfect_auc
    return auc


def get_legend_name(s):
    if 'cnn' in s:
        if 'static' in s:
            return 'SVD-CNN'
        else:
            return 'DEMUD-CNN'
    else: # assume pixel run
        if 'sift' in s:
            if 'static' in s:
                return 'SVD-SIFT'
            else:
                return 'DEMUD-SIFT'
        elif 'static' in s:
            return 'SVD-pixel'
        else:
            return 'DEMUD-pixel'

        
def gen_auc(result_dir, result_dir_list, rand_x, n_selections):

    # Oracle - perfect discovery, starting with 1 class on round 0
    n_classes = len(rand_x)
    perfect_disc = range(0,n_classes+1) + [n_classes] * \
                   (n_selections-n_classes)

    result_dir_list.sort()
    
    # put DEMUD first, then SVD
    result_dir_list = [d for d in result_dir_list if 'static' not in d] + \
        [d for d in result_dir_list if 'static' in d] 

    result_csv_list = []
    for a_folder in result_dir_list:
        curr_path = os.path.join(result_dir, a_folder)
        curr_csv = [t for t in os.listdir(curr_path) \
                    if t.startswith('selections')]
        if len(curr_csv) == 0: continue  # Skip incomplete results
        curr_csv = curr_csv[0]
        result_csv_list.append(os.path.join(curr_path, curr_csv))

    result_coord_list = []
    result_auc = {}
    for a_result in result_csv_list:
        curr_file = open(a_result, 'r')
        csv_reader = csv.reader(curr_file)
        csv_list = list(csv_reader)
        csv_list.pop(0)

        a_x_list = []
        a_y_list = []
        seen_classes = []
        for (sel_count, a_selection) in enumerate(csv_list):
            selection_id = int(a_selection[0])
            if a_selection[2].count('-') == 1:
                #assuming <image-class.jpg>
                temp = a_selection[2].split('-')[1].split('.')
            else:
                #assuming <class_image.jpg>
                temp = a_selection[2].split('_');
            if len(temp) == 1:
                class_id = "none"
            else:
                class_id = temp[0]
            if class_id not in seen_classes:
                seen_classes.append(class_id)
                # Use sel_count+1 since x axis in plot is 
                # "number of selected" not "index of selected"
                a_x_list.append(sel_count+1)
                a_y_list.append(len(seen_classes))
        result_coord_list.append([a_x_list, a_y_list])
        result_auc[a_result] = calc_auc(a_x_list, a_y_list, n_selections, sum(perfect_disc))
        print a_result.split('/')[-2], '\t%.2f' % result_auc[a_result]

    # Random - one discovery per rand_x entry
    rand_y = range(1,n_classes+1)  

    # AUC for random
    # Use x+1 since x axis in plot is 
    # "number of selected" not "index of selected"
    result_auc['rand'] = calc_auc([int(math.ceil(x+1)) for x in rand_x], rand_y, 
                                  n_selections, sum(perfect_disc))
    print 'Random\t%.2f' % result_auc['rand']

    return result_coord_list, result_auc


def gen_plot(result_dir_list, result_coord_list, rand_x, n_selections, title, outfile):

    plt.figure(1)
    plot_list = []

    result_dir_list.sort()
    # put DEMUD first, then SVD
    result_dir_list = [d for d in result_dir_list if 'static' not in d] + \
        [d for d in result_dir_list if 'static' in d] 

    # Plot perfect performance
    # Random - one discovery per rand_x entry
    n_classes = len(rand_x)
    rand_y = range(1,n_classes+1)  
    plot_list.append(plt.plot(rand_y, rand_y,
                              color="xkcd:cyan",# marker=".", 
                              linestyle="-.", label="Oracle"))

    for i in range(len(result_coord_list)):
        plot_list.append(plt.plot(result_coord_list[i][0], 
                                  result_coord_list[i][1], 
                                  color=color_list[i],
                                  marker=shape_list[i], 
                                  linestyle=line_list[i],
                                  label=get_legend_name(result_dir_list[i])))

    # Use rand_x+1 since x axis in plot is 
    # "number of selected" not "index of selected"
    plot_list.append(plt.plot([r+1 for r in rand_x], rand_y, 
                              color="xkcd:black", marker=".", 
                              linestyle=":", label="Random"))

    plt.legend(loc=4)
    plt.xlim([1,n_selections])
    plt.ylim([1,n_classes])

    plt.title(title)
    plt.xlabel('Number of selected examples')
    plt.ylabel('Number of classes discovered')

    plt.savefig(outfile)
    plt.show()
