# This script shows how to reconstruct images from features with a trained model 
#
# Alexey Dosovitskiy, 2016
# Modified by Jake Lee, 2017/18

import sys

# uncomment and change the path to make python use specific caffe version
#sys.path.insert(0, '/home/dosovits/MATLAB/toolboxes/caffe-fr-chairs/python')
#print sys.path

import caffe
import numpy as np
import os
import patchShow
import scipy.misc
import scipy.io
import csv
import copy

print(caffe.__file__)

# set up the inputs for the net: 
image_size = (3,227,227)

# subtract the ImageNet mean
matfile = scipy.io.loadmat('ilsvrc_2012_mean.mat')
image_mean = matfile['image_mean']
topleft = ((image_mean.shape[0] - image_size[1])/2, (image_mean.shape[1] - image_size[2])/2)

#initialize the caffenet to extract the features
caffe.set_mode_gpu() # replace by caffe.set_mode_cpu() to run on a CPU [MODIFIED TO GPU]

# import features from CSV
demud_csv = 'DEMUD/results/select-cnn-*.csv'
csv_imported = np.genfromtxt(demud_csv, delimiter=",")
print '=============================================================='
print csv_imported.shape

datalength = len(csv_imported)
numzeros = 64 - (datalength % 64)
csv_imported = np.concatenate((csv_imported, np.zeros((numzeros, 4096), dtype='float32')), axis=0)
datalength = len(csv_imported)


# run recon net
net = caffe.Net('generator_fc6.prototxt', 'generator_fc6.caffemodel', caffe.TEST)
master_recon = np.asarray([])
itr = 0
while itr < datalength:
	batch = csv_imported[itr:itr+64]
	generated = net.forward(feat=batch)
	recon = copy.deepcopy(generated['deconv0'][:,::-1,topleft[0]:topleft[0]+image_size[1], topleft[1]:topleft[1]+image_size[2]])
	if master_recon.size == 0:
		master_recon = recon
	else:
		master_recon = np.concatenate((master_recon, recon), axis=0)
	itr += 64
del net

print master_recon.shape

# save results to a file

counter = 0
# output folder - must pre-exist!
folder = '/DaB/results/select/'
while counter < datalength:
	an_image = patchShow.patchShow(np.asarray([master_recon[counter]]))
	scipy.misc.imsave(folder+str(counter)+'.png', an_image)
	counter += 1

