import os
import re

img_directory = os.getcwd() + "/imgs/"
kps_directory = os.getcwd() + "/imgs_kps/"

src_image_route = "/src_images/"
kps_image_route = "/kps_images/"
dynamic_image_route = "/results/"


def glob_re(pattern, strings):
    return list(filter(re.compile(pattern).match, strings))
