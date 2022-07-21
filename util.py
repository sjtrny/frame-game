import cv2 as cv
from sklearn.neighbors import NearestNeighbors
import numpy as np
import os

img_directory = os.getcwd() + "/imgs/"
kps_directory = os.getcwd() + "/imgs_kps/"

src_image_route = "/src_images/"
kps_image_route = "/kps_images/"
dynamic_image_route = "/results/"

N_NEIGHBORS = 5
DEG_QUANT_F = 1
DECIMALS = 0

def angle(p1, p2):
    if np.allclose(p1, p2):
        return 0

    x1 = np.array([0, 1])
    x2 = p2 - p1
    dp = np.dot(x1, x2 / np.linalg.norm(x2))
    return np.arccos(dp)

def get_hashes(cv_img):

    gray = cv.cvtColor(cv_img, cv.COLOR_BGR2GRAY)

    sift = cv.SIFT_create()

    kps = sift.detect(gray, None)

    neigh = NearestNeighbors(n_neighbors=1+N_NEIGHBORS)

    kp_array = np.array([kp.pt for kp in kps])

    neigh.fit(kp_array)

    _, knn_inds = neigh.kneighbors(kp_array)

    hashes = []

    for i in range(len(kps)):

        kp1 = kps[i]
        kp1_pt = np.array(kp1.pt)

        for j in range(0, 1+N_NEIGHBORS):

            if i != knn_inds[i, j]:

                kp2 = kps[knn_inds[i, j]]
                kp2_pt = np.array(kp2.pt)

                d = np.linalg.norm(kp1_pt - kp2_pt)

                a1 = kp1.angle / DEG_QUANT_F
                a2 = kp2.angle / DEG_QUANT_F
                a12 = np.rad2deg(angle(kp1_pt, kp2_pt)) / DEG_QUANT_F

                pair_str = f"{a1:.{DECIMALS}f}|{a2:.{DECIMALS}f}|{a12:.{DECIMALS}f}|{kp1.size:.{DECIMALS}f}|{kp2.size:.{DECIMALS}f}"

                hashes.append(pair_str)

    return hashes


def get_hash_for_img(img_path):
    cvimg = cv.imread(f"./imgs/{img_path}")
    hashes = get_hashes(cvimg)
    return hashes


def get_best_match_idx(test_img_path, source_img_paths):

    hash_overlaps = []
    test_cvimg = cv.imread(f"imgs/{test_img_path}")
    test_hashes = get_hashes(test_cvimg)

    for source_img_path in source_img_paths:
        source_cvimg = cv.imread(f"./imgs/{source_img_path}")
        source_hashes = get_hashes(source_cvimg)

        hash_overlaps.append(
            len(set.intersection(set(test_hashes), set(source_hashes)))
        )

    return np.argmax(hash_overlaps)
