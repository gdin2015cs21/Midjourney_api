# -*- coding:utf-8 -*-
from PIL import Image
import matplotlib.pyplot as plt


def image_cut_save(path, left, upper, right, lower, save_path):
    """
        所截区域图片保存
    :param path: 图片路径
    :param left: 区块左上角位置的像素点离图片左边界的距离
    :param upper：区块左上角位置的像素点离图片上边界的距离
    :param right：区块右下角位置的像素点离图片左边界的距离
    :param lower：区块右下角位置的像素点离图片上边界的距离
     故需满足：lower > upper、right > left
    :param save_path: 所截图片保存位置
    """
    img = Image.open(path)  # 打开图像
    box = (left, upper, right, lower)
    roi = img.crop(box)

    # 保存截取的图片
    roi.save(save_path)


if __name__ == '__main__':
    pic_path = 'james83.png'
    l_ = {
        0: [0, 0, 1024, 1024],
        1: [0, 1024, 1024, 2048],
        2: [1024, 0, 2048, 1024],
        3: [1024, 1024, 2048, 2048]
    }
    for i in l_:
        left, upper, right, lower = l_[i]
        pic_save_dir_path = f'cut{i}.png'
        image_cut_save(pic_path, left, upper, right, lower, pic_save_dir_path)
