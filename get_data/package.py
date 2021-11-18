# -*- coding: utf-8 -*-
from __future__ import print_function
from __future__ import absolute_import

import argparse
import glob
import os
import pickle as pickle
import random

from numpy import e


def pickle_examples(from_dir, train_path, val_path, train_val_split=0.2, with_charid=False):
    """
    Compile a list of examples into pickled format, so during
    the training, all io will happen in memory
    """
    paths=from_dir

    # paths = glob.glob(os.path.join(from_dir, "*.png"))
    with open(train_path, 'wb') as ft:
        with open(val_path, 'wb') as fv:
            print('all data num:', len(paths))
            c = 1
            val_count = 0
            train_count = 0
            if with_charid:
                print('pickle with charid')
                for p in paths:
                    c += 1
                    label = int(os.path.basename(p).split("_")[0])
                    charid = int(os.path.basename(p).split("_")[1].split(".")[0])
                    with open(p, 'rb') as f:
                        img_bytes = f.read()
                        example = (label, charid, img_bytes)
                        r = random.random()
                        if r < train_val_split:
                            pickle.dump(example, fv)
                            val_count += 1
                            if val_count % 10000 == 0:
                                print("%d imgs saved in val.obj" % val_count)
                        else:
                            pickle.dump(example, ft)
                            train_count += 1
                            if train_count % 10000 == 0:
                                print("%d imgs saved in train.obj" % train_count)
                print("%d imgs saved in val.obj, end" % val_count)
                print("%d imgs saved in train.obj, end" % train_count)
            else:
                for p in paths:
                    c += 1
                    label = int(os.path.basename(p).split("_")[0])
                    with open(p, 'rb') as f:
                        img_bytes = f.read()
                        example = (label, img_bytes)
                        r = random.random()
                        if r < train_val_split:
                            pickle.dump(example, fv)
                            val_count += 1
                            if val_count % 10000 == 0:
                                print("%d imgs saved in val.obj" % val_count)
                        else:
                            pickle.dump(example, ft)
                            train_count += 1
                            if train_count % 10000 == 0:
                                print("%d imgs saved in train.obj" % train_count)
                print("%d imgs saved in val.obj, end" % val_count)
                print("%d imgs saved in train.obj, end" % train_count)
            return
        
        
def pickle_interpolation_data(from_dir, save_path, char_ids, font_filter):
    paths = glob.glob(os.path.join(from_dir, "*.png"))
    with open(save_path, 'wb') as ft:
        c = 0
        for p in paths:
            charid = int(p.split('/')[-1].split('.')[0].split('_')[1])
            label = int(os.path.basename(p).split("_")[0])
            if (charid in char_ids) and (label in font_filter):
                c += 1
                with open(p, 'rb') as f:
                    img_bytes = f.read()
                    example = (label, charid, img_bytes)
                    pickle.dump(example, ft)
        print('data num:', c)
        return

parser = argparse.ArgumentParser(description='Compile list of images into a pickled object for training')
parser.add_argument('--dir', dest='dir', default='./get_data/dataset-11172-2/' ,help='path of examples')
parser.add_argument('--save_dir', dest='save_dir', default='./dataset-binary/', help='path to save pickled files')
parser.add_argument('--split_ratio', type=float, default=0.1, dest='split_ratio',
                    help='split ratio between train and val')
args = parser.parse_args()

if __name__ == "__main__":
    os.makedirs(args.save_dir, exist_ok=True)
    train_path = os.path.join(args.save_dir, "train.obj")
    val_path = os.path.join(args.save_dir, "val.obj")
    pickle_examples(sorted(glob.glob(os.path.join(args.dir, "*.jpg"))), train_path=train_path, val_path=val_path,
                    train_val_split=args.split_ratio)