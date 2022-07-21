import cv2 as cv
from sklearn.neighbors import NearestNeighbors
import numpy as np
import hashlib


import glob
import os
import re

def glob_re(pattern, strings):
    return list(filter(re.compile(pattern).match, strings))

source_filenames = glob_re(f"frame.*", os.listdir("./imgs"))

sift = cv.SIFT_create()

for image_filename in source_filenames:
    source_img = cv.imread(f"./imgs/{image_filename}")
    gray= cv.cvtColor(source_img,cv.COLOR_BGR2GRAY)
    kp = sift.detect(gray,None)
    img=cv.drawKeypoints(source_img,kp,source_img,flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS)
    name = image_filename.split(".")[0]
    type = image_filename.split(".")[-1]
    cv.imwrite(f"./imgs_kps/{name}-kps.{type}",img)
