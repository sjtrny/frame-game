import os
import re

original_image_path = "./imgs"

src_image_route = "/assets/imgs/"
kps_image_route = "/assets/imgs_kps/"


def glob_re(pattern, strings):
    return list(filter(re.compile(pattern).match, strings))


def sort_images(list_of_images):
    sort_order = lambda x: int(x.split("-")[0].split("frame")[1])
    return list(sorted(list_of_images, key=sort_order))
