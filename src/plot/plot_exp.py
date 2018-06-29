#!/usr/bin/env python
# Plot results of DEMUD selections for comparison

import sys, os
from util_plot import gen_plot, gen_auc

# directory of DEMUD results
result_dir = "/DEMUD/results"

# optional title
title = ''

# name of output plot file
outfile = 'plot.pdf'

n_selections=300

# Random discovery rate - calculate

rand_x = []

if __name__ == "__main__":
    # Select results of interest
    # Adjust these conditions to match the results you want to plot
    # The current example looks for result files that are k=50, are from msl, 
    # and are either fc6 or pixel-based.
    result_dir_list = [f for f in os.listdir(result_dir) \
                           if (not f.startswith('.') and 'k=50-' in f and 
                   'msl' in f and ('fc6' in f or 'img' in f))]

    # Generate the plot and AUC values
    result_coord_list, result_auc = gen_auc(result_dir, result_dir_list, 
                                            rand_x, n_selections)

    raw_input('Proceed to plot? (Any key to continue, Ctrl-c to quit)')
    gen_plot(result_dir_list, result_coord_list, rand_x, n_selections, title, outfile)
