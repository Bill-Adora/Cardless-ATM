import os
import sys
import argparse
import time

import pandas as pd
import numpy as np
from sklearn.datasets import load_files
import tensorflow as tf
from face_functions import get_model_filenames
from face_functions import load_model
from face_functions import load_data


def main(args):

	with tf.Graph().as_default():

		with tf.Session() as sess:

			# create output directory if it doesn't exist
			output_dir = os.path.expanduser(args.output_dir)
			if not os.path.isdir(output_dir):
				os.makedirs(output_dir)

			# load the model
			print("Loading trained model...\n")
			meta_file, ckpt_file = get_model_filenames(os.path.expanduser(args.trained_model_dir))
			load_model(args.trained_model_dir, meta_file, ckpt_file)

			# grab all image paths and labels
			print("Finding image paths and targets...\n")
			data = load_files(args.data_dir, load_content=False, shuffle=False)
			labels_array = data['target']
			paths = data['filenames']

			# Get input and output tensors
			images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
			embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
			phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

			image_size = images_placeholder.get_shape()[1]
			embedding_size = embeddings.get_shape()[1]

			# Run forward pass to calculate embeddings
			print('Generating embeddings from images...\n')
			start_time = time.time()
			batch_size = args.batch_size
			nrof_images = len(paths)
			nrof_batches = int(np.ceil(1.0*nrof_images / batch_size))
			emb_array = np.zeros((nrof_images, embedding_size))
			for i in range(nrof_batches):
				start_index = i*batch_size
				end_index = min((i+1)*batch_size, nrof_images)
				paths_batch = paths[start_index:end_index]
				images = load_data(paths_batch, do_random_crop=False, do_random_flip=False, image_size=image_size, do_prewhiten=True)
				feed_dict = { images_placeholder:images, phase_train_placeholder:False}
				emb_array[start_index:end_index,:] = sess.run(embeddings, feed_dict=feed_dict)

			time_avg_forward_pass = (time.time() - start_time) / float(nrof_images)
			print("Forward pass took avg of %.3f[seconds/image] for %d images\n" % (time_avg_forward_pass, nrof_images))

			print("Finally saving embeddings and labels to: %s" % (output_dir))

			# save the labels and embeddings as csv files to disk
			np.savetxt(os.path.join(output_dir, "reps.csv"), emb_array, delimiter=',')
			np.savetxt(os.path.join(output_dir, "labels.csv"), paths, fmt='%s', delimiter=',')


def parse_arguments(argv):
	parser = argparse.ArgumentParser(description="Batch-represent face embeddings from a given data directory")
	parser.add_argument('-d', '--data_dir', type=str,
		help='directory of images with structure as seen at the top of this file.')
	parser.add_argument('-o', '--output_dir', type=str,
		help='directory containing aligned face patches with file structure as seen at the top of this file.')
	parser.add_argument('-m', '--trained_model_dir', type=str, help='Load a trained model before training starts.')
	parser.add_argument('--batch_size', type=int, help='Number of images to process in a batch.', default=50)

	return parser.parse_args(argv)


if __name__ == "__main__":
	main(parse_arguments(sys.argv[1:]))
