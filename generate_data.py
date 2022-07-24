import copyreg
import os
import pickle

import cv2 as cv
import numpy as np
from PIL import Image
from sklearn.neighbors import NearestNeighbors

from util import glob_re, original_image_path, sort_images

N_NEIGHBORS = 5
DEG_QUANT_F = 1
DECIMALS = 0

MAX_IMG_WIDTH = 1080
MAX_IMG_HEIGHT = 1080


def patch_keypoint_pickling():
    # Create the bundling between class and arguements to save for Keypoint class
    # See : https://stackoverflow.com/questions/50337569/pickle-exception-for-cv2-boost-when-using-multiprocessing/50394788#50394788
    def _pickle_keypoint(keypoint):  #  : cv2.KeyPoint
        return cv.KeyPoint, (
            keypoint.pt[0],
            keypoint.pt[1],
            keypoint.size,
            keypoint.angle,
            keypoint.response,
            keypoint.octave,
            keypoint.class_id,
        )

    # KeyPoint (float x, float y, float _size, float _angle=-1, float _response=0, int _octave=0, int _class_id=-1)

    # Apply the bundling to pickle
    copyreg.pickle(cv.KeyPoint().__class__, _pickle_keypoint)


def angle(p1, p2):
    if np.allclose(p1, p2):
        return 0

    x1 = np.array([0, 1])
    x2 = p2 - p1
    dp = np.dot(x1, x2 / np.linalg.norm(x2))
    return np.arccos(dp)


def get_hashes(kps):
    neigh = NearestNeighbors(n_neighbors=1 + N_NEIGHBORS)

    kp_array = np.array([kp.pt for kp in kps])

    hashes = []

    try:
        neigh.fit(kp_array)
        _, knn_inds = neigh.kneighbors(kp_array)

        for i in range(len(kps)):

            kp1 = kps[i]
            kp1_pt = np.array(kp1.pt)

            for j in range(0, 1 + N_NEIGHBORS):

                if i != knn_inds[i, j]:

                    kp2 = kps[knn_inds[i, j]]
                    kp2_pt = np.array(kp2.pt)

                    np.linalg.norm(kp1_pt - kp2_pt)

                    a1 = kp1.angle / DEG_QUANT_F
                    a2 = kp2.angle / DEG_QUANT_F
                    a12 = np.rad2deg(angle(kp1_pt, kp2_pt)) / DEG_QUANT_F

                    pair_str = f"{a1:.{DECIMALS}f}|{a2:.{DECIMALS}f}|{a12:.{DECIMALS}f}|{kp1.size:.{DECIMALS}f}|{kp2.size:.{DECIMALS}f}"

                    hashes.append(pair_str)
    except:
        pass

    return hashes


patch_keypoint_pickling()

source_filenames = sort_images(glob_re(f"frame.*", os.listdir("./imgs")))

sift = cv.SIFT_create()

hash_dict = {}

for image_filename in source_filenames:
    print(image_filename)

    name = image_filename.split(".")[0]
    type = image_filename.split(".")[-1]

    # Convert, scale down and transfer image
    im = Image.open(f"{original_image_path}/{image_filename}")
    source_img = cv.cvtColor(np.array(im), cv.COLOR_RGB2BGR)

    # Save small version for web
    im.thumbnail((MAX_IMG_WIDTH, MAX_IMG_HEIGHT))
    im.save(f"./assets/imgs/{name}.jpg", quality=50, progressive=True, optimize=True)

    # Exract keypoints
    gray = cv.cvtColor(source_img, cv.COLOR_BGR2GRAY)
    kps = sift.detect(gray, None)

    hash_dict[f"{name}.jpg"] = get_hashes(kps)

    # Generate keypoint image
    kp_img = cv.drawKeypoints(
        source_img,
        kps,
        source_img,
        flags=cv.DRAW_MATCHES_FLAGS_DRAW_RICH_KEYPOINTS,
    )

    pil_image = Image.fromarray(cv.cvtColor(kp_img, cv.COLOR_BGR2RGB))
    pil_image.thumbnail((MAX_IMG_WIDTH, MAX_IMG_HEIGHT))
    pil_image.save(
        f"./assets/imgs_kps/{name}-kps.jpg", quality=50, progressive=True, optimize=True
    )

with open("kp_data.pickle", "wb") as file:
    pickle.dump(hash_dict, file)
