from datetime import datetime
import argparse
import pickle
import numpy as np
from io import BytesIO
from array import array
#import Image
from PIL import Image

from sklearn.mixture import GMM
from face_functions import *

def infer(rawImage):
	startTime = datetime.now()
	with open("/home/bill/Flask-ATM/app/Face_Recognizer/Embeddings/classifier.pkl", 'rb') as f:
		(le, clf) = pickle.load(f)
	
	image = converter(rawImage)
	reps = getRep(image)
	rep = reps[0].reshape(1, -1)
	predictions = clf.predict_proba(rep).ravel()
	maxI = np.argmax(predictions)
	person = le.inverse_transform(maxI)
	confidence = predictions[maxI]

	print("Prediction took {} seconds.".format(datetime.now() - startTime))
	print("Predict {} with {:.2f} confidence.".format(person, confidence))

	if isinstance(clf, GMM):
		dist = np.linalg.norm(rep - clf.means_[maxI])
		print("  + Distance from the mean: {}".format(dist))
	
	return person

def converter(rawImage):
	buf = BytesIO()   
	buf.write(rawImage)

	with open("/home/bill/Flask-ATM/app/Face_Recognizer/Images/Input.jpg", "wb") as f:
		f.write(buf.getvalue())

	return misc.imread('/home/bill/Flask-ATM/app/Face_Recognizer/Images/Input.jpg')

if __name__ == "__main__":
	'''image = misc.imread('Images/aliko.jpg')
	f = open("Images/aliko.jpg", "rb")
	byteImage = bytearray(f.read())
	personID = infer(byteImage)

	print (personID)'''