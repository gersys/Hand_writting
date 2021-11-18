# https://github.com/kaonashi-tyc/zi2zi

# -*- coding: utf-8 -*-

import argparse
import sys
import glob
import numpy as np
import io, os
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
import collections
import json

SRC_PATH = './get_data/fonts/source/'
TRG_PATH = './get_data/fonts/target/'
OUTPUT_PATH = './dataset-11172/'


DEFAULT_CHARSET = "./charset/cjk.json"


def load_global_charset():
    global CN_CHARSET, JP_CHARSET, KR_CHARSET, CN_T_CHARSET
    cjk = json.load(open(DEFAULT_CHARSET))
    # CN_CHARSET = cjk["gbk"]
    # JP_CHARSET = cjk["jp"]

    # 한글 문자 리스트 로딩, 근데 1970개 밖에 없음... ;
    KR_CHARSET = cjk["kr"]

    # CN_T_CHARSET = cjk["gb2312_t"]


def draw_single_char(ch, font, canvas_size):
    image = Image.new('L', (canvas_size, canvas_size), color=255)
    drawing = ImageDraw.Draw(image)
    w, h = drawing.textsize(ch, font=font)
    drawing.text(
        ((canvas_size-w)/2, (canvas_size-h)/2),
        ch,
        fill=(0),
        font=font
    )
    flag = np.sum(np.array(image))
    
    # 해당 font에 글자가 없으면 return None
    if flag == 255 * 128 * 128:
        return None
    
    return image


def draw_example(ch, src_font, dst_font, canvas_size):
    dst_img = draw_single_char(ch, dst_font, canvas_size)
    
    # 해당 font에 글자가 없으면 return None
    if not dst_img:
        return None
    
    src_img = draw_single_char(ch, src_font, canvas_size)
    example_img = Image.new("RGB", (canvas_size * 2, canvas_size), (255, 255, 255)).convert('L')
    example_img.paste(dst_img, (0, 0))
    example_img.paste(src_img, (canvas_size, 0))   
    return example_img


def draw_handwriting(ch, src_font, canvas_size, dst_folder, label, count):
    dst_path = dst_folder + "%d_%04d" % (label, count) + ".png"
    dst_img = Image.open(dst_path)
    src_img = draw_single_char(ch, src_font, canvas_size)
    example_img = Image.new("RGB", (canvas_size * 2, canvas_size), (255, 255, 255)).convert('L')
    example_img.paste(dst_img, (0, 0))
    example_img.paste(src_img, (canvas_size, 0))
    return example_img


def font2img(src, dst, charset, char_size, canvas_size,
             x_offset, y_offset, sample_count, sample_dir, label=0, filter_by_hash=True):
    src_font = ImageFont.truetype(src, size=char_size)
    dst_font = ImageFont.truetype(dst, size=char_size)

    filter_hashes = set()
    if filter_by_hash:
        filter_hashes = set(filter_recurring_hash(charset, dst_font, canvas_size, x_offset, y_offset))
        print("filter hashes -> %s" % (",".join([str(h) for h in filter_hashes])))

    count = 0

    for c in charset:
        if count == sample_count:
            break
        e = draw_example(c, src_font, dst_font, canvas_size)
        if e:
            os.makedirs(OUTPUT_PATH, exist_ok=True)
            e.save(os.path.join(sample_dir, "%d_%04d.jpg" % (label, count)))
            count += 1
            if count % 100 == 0:
                print("processed %d chars" % count)


parser = argparse.ArgumentParser(description='Convert font to images')
parser.add_argument('--src_font', dest='src_font',default=SRC_PATH ,  help='path of the source font')
parser.add_argument('--dst_font', dest='dst_font',default=TRG_PATH , help='path of the target font')
parser.add_argument('--filter', dest='filter', type=int, default=0, help='filter recurring characters')
parser.add_argument('--charset', dest='charset', type=str, default='KR',
                    help='charset, can be either: CN, JP, KR or a one line file')
parser.add_argument('--shuffle', dest='shuffle', type=int, default=0, help='shuffle a charset before processings')
parser.add_argument('--char_size', dest='char_size', type=int, default=150, help='character size')
parser.add_argument('--canvas_size', dest='canvas_size', type=int, default=128, help='canvas size')
parser.add_argument('--x_offset', dest='x_offset', type=int, default=20, help='x offset')
parser.add_argument('--y_offset', dest='y_offset', type=int, default=20, help='y_offset')
parser.add_argument('--sample_count', dest='sample_count', type=int, default=2350, help='number of characters to draw')
parser.add_argument('--sample_dir', dest='sample_dir',default=OUTPUT_PATH , help='directory to save examples')
parser.add_argument('--label', dest='label', type=int, default=0, help='label as the prefix of examples')

args = parser.parse_args()

if __name__ == "__main__":
    load_global_charset()
    if args.charset in ['CN', 'JP', 'KR', 'CN_T']:
        charset = locals().get("%s_CHARSET" % args.charset)
    else:
        charset = [c for c in open(args.charset).readline()[:-1].decode("utf-8")]

    with open('./get_data/2350-common-hangul.txt', "r") as f:
        charset2=f.read()

    charset2=charset2.split("\n")
    charset2=charset2[:-1]

    


    src_fonts=glob.glob(SRC_PATH+'*.ttf')
    trg_fonts=glob.glob(TRG_PATH+'*.ttf')

    if args.shuffle:
        np.random.shuffle(charset)

    for src in src_fonts:
        for label,trg in enumerate(trg_fonts): 
            font2img(src, trg, charset2, args.char_size,args.canvas_size, args.x_offset, args.y_offset,args.sample_count, args.sample_dir, label , args.filter)