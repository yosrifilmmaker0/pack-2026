"""Photographic post: LED bloom + subtle vignette + mild clarity. usage: post.py in.png out.jpg"""
import sys, numpy as np
from PIL import Image, ImageFilter
im = Image.open(sys.argv[1]).convert('RGB'); a = np.asarray(im).astype(np.float32) / 255
lum = a @ np.array([0.2126, 0.7152, 0.0722], np.float32)
mask = np.clip((lum - 0.80) / 0.2, 0, 1)[..., None] * a
bloom = np.zeros_like(a); W = im.width
for r, w in ((W * 0.004, 0.55), (W * 0.012, 0.35), (W * 0.035, 0.25)):
    b = Image.fromarray((mask * 255).astype(np.uint8)).filter(ImageFilter.GaussianBlur(r)); bloom += np.asarray(b).astype(np.float32) / 255 * w
out = 1 - (1 - a) * (1 - np.clip(bloom * 0.8, 0, 1))            # screen blend
h, w = lum.shape; yy, xx = np.mgrid[0:h, 0:w]; d = np.sqrt(((xx - w / 2) / (w / 2)) ** 2 * 0.8 + ((yy - h / 2) / (h / 2)) ** 2)
out *= (1 - 0.28 * np.clip(d - 0.35, 0, 1) ** 1.6)[..., None]
res = Image.fromarray((np.clip(out, 0, 1) * 255).astype(np.uint8))
res = res.filter(ImageFilter.UnsharpMask(radius=2, percent=40, threshold=2))
res.save(sys.argv[2], quality=94); print('saved', sys.argv[2])
