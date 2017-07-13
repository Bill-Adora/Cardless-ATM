import os
from scipy import misc
import re
import numpy as np
import tensorflow as tf
from numpy import array
from detect_face import create_mtcnn
from detect_face import detect_face

def getRep(inputImage):

	img = load_and_align_data(inputImage)
	image = array(img).reshape(1, 160, 160, 3)

	with tf.Graph().as_default():

		with tf.Session() as sess:

			# load the model
			print("Loading trained model...\n")
			meta_file, ckpt_file = get_model_filenames(os.path.expanduser("/home/bill/Flask-ATM/app/Face_Recognizer/model/Resnet-v1/"))
			print(os.path.expanduser("/home/bill/Flask-ATM/app/Face_Recognizer/model/Resnet-v1/"))
			load_model("/home/bill/Flask-ATM/app/Face_Recognizer/model/Resnet-v1/", meta_file, ckpt_file)

			# Get input and output tensors
			images_placeholder = tf.get_default_graph().get_tensor_by_name("input:0")
			embeddings = tf.get_default_graph().get_tensor_by_name("embeddings:0")
			phase_train_placeholder = tf.get_default_graph().get_tensor_by_name("phase_train:0")

			# Run forward pass to calculate embeddings
			print('Generating embeddings from image...\n')
			feed_dict = { images_placeholder:image, phase_train_placeholder:False}
			emb_array = sess.run(embeddings, feed_dict=feed_dict)
			return emb_array

def get_model_filenames(model_dir):
	files = os.listdir(model_dir)
	meta_files = [s for s in files if s.endswith('.meta')]

	if len(meta_files)==0:
		print('No meta file found in the model directory (%s)' % model_dir)
	elif len(meta_files)>1:
		print('There should not be more than one meta file in the model directory (%s)' % model_dir)
	meta_file = meta_files[0]
	meta_files = [s for s in files if '.ckpt' in s]
	max_step = -1

	for f in files:
		step_str = re.match(r'(^model-[\w\- ]+.ckpt-(\d+))', f)
		if step_str is not None and len(step_str.groups())>=2:
			step = int(step_str.groups()[1])
			if step > max_step:
				max_step = step
				ckpt_file = step_str.groups()[0]
		return meta_file, ckpt_file


def load_and_align_data(img):

	print("Loading and aligning images...")
	minsize = 20 # minimum size of face
	threshold = [ 0.6, 0.7, 0.7 ]  # three steps's threshold
	factor = 0.709 # scale factor
	image_size = 160
	margin = 44
	gpu_memory_fraction = 0.4

	print('Creating networks and loading parameters')
	with tf.Graph().as_default():
		gpu_options = tf.GPUOptions(per_process_gpu_memory_fraction=gpu_memory_fraction)
		sess = tf.Session(config=tf.ConfigProto(gpu_options=gpu_options, log_device_placement=False))
		with sess.as_default():
			pnet, rnet, onet = create_mtcnn(sess, None)

	img_size = np.asarray(img.shape)[0:2]
	bounding_boxes, _ = detect_face(img, minsize, pnet, rnet, onet, threshold, factor)
	det = np.squeeze(bounding_boxes[0,0:4])
	bb = np.zeros(4, dtype=np.int32)
	bb[0] = np.maximum(det[0]-margin/2, 0)
	bb[1] = np.maximum(det[1]-margin/2, 0)
	bb[2] = np.minimum(det[2]+margin/2, img_size[1])
	bb[3] = np.minimum(det[3]+margin/2, img_size[0])
	cropped = img[bb[1]:bb[3],bb[0]:bb[2],:]
	aligned = misc.imresize(cropped, (image_size, image_size), interp='bilinear')
	image = prewhiten(aligned)
	return image


def prewhiten(x):
	mean = np.mean(x)
	std = np.std(x)
	std_adj = np.maximum(std, 1.0/np.sqrt(x.size))
	y = np.multiply(np.subtract(x, mean), 1/std_adj)
	return y


def load_model(model_dir, meta_file, ckpt_file):
	model_dir_exp = os.path.expanduser(model_dir)
	saver = tf.train.import_meta_graph(os.path.join(model_dir_exp, meta_file))
	saver.restore(tf.get_default_session(),
					os.path.join(model_dir_exp, ckpt_file))


def load_data(image_paths, do_random_crop, do_random_flip, image_size, do_prewhiten=True):
	nrof_samples = len(image_paths)
	images = np.zeros((nrof_samples, image_size, image_size, 3))
	for i in range(nrof_samples):
		img = misc.imread(image_paths[i])
		if img.ndim == 2:
			img = to_rgb(img)
		if do_prewhiten:
			img = prewhiten(img)
		img = crop(img, do_random_crop, image_size)
		img = flip(img, do_random_flip)
		images[i, :, :, :] = img
	return images


def crop(image, random_crop, image_size):
	if image.shape[1]>image_size:
		sz1 = int(image.shape[1]//2)
		sz2 = int(image_size//2)
		if random_crop:
			diff = sz1-sz2
			(h, v) = (np.random.randint(-diff, diff+1), np.random.randint(-diff, diff+1))
		else:
			(h, v) = (0,0)
			image = image[(sz1-sz2+v):(sz1+sz2+v),(sz1-sz2+h):(sz1+sz2+h),:]
	return image


def flip(image, random_flip):
	if random_flip and np.random.choice([True, False]):
		image = np.fliplr(image)
	return image
