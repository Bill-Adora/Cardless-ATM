import os
import pickle
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from sklearn.svm import SVC
from operator import itemgetter

print("Train a new classifier.")
print("Loading embeddings.")
fname = "{}/labels.csv".format("Embeddings")
labels = pd.read_csv(fname, header=None).as_matrix()[:, 0]
labels = list(map(itemgetter(1), map(os.path.split, map(os.path.dirname, labels))))  # Get the directory.
fname = "{}/reps.csv".format("Embeddings")
embeddings = pd.read_csv(fname, header=None).as_matrix()
le = LabelEncoder().fit(labels)
labelsNum = le.transform(labels)
nClasses = len(le.classes_)
print("Training for {} classes.".format(nClasses))

# Using LinearSvm as classifier
clf = SVC(C=1, kernel='linear', probability=True)
#clf = LinearSVC(C=1, multi_class='ovr')

clf.fit(embeddings, labelsNum)

fName = "{}/classifier.pkl".format("Embeddings")
print("Saving classifier to '{}'".format(fName))
with open(fName, 'wb') as f:
    pickle.dump((le, clf), f)