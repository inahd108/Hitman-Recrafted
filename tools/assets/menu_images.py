"""Turn the MenuShots screenshots into the title-screen background and the mission-browser preview frames.
Usage: python3 tools/assets/menu_images.py <scene.png> <orbit_dir>   (orbit_dir holds menu_orbit_*.png)"""
import glob
import os
import sys
from PIL import Image, ImageEnhance, ImageFilter

OUT = 'src/main/resources/assets/recrafted/textures/gui/menu'


def grade(im, warmth=1.0, contrast=1.06, saturation=1.08):
    im = ImageEnhance.Contrast(im).enhance(contrast)
    im = ImageEnhance.Color(im).enhance(saturation)
    if warmth != 1.0:
        r, g, b = im.split()
        r = r.point(lambda v: min(255, int(v * warmth)))
        b = b.point(lambda v: int(v / warmth))
        im = Image.merge('RGB', (r, g, b))
    return im


def save_small(im, path, colors=None):
    """PNG at a sane size: optionally palettised with dithering (the preview frames are small on screen)."""
    if colors:
        im = im.quantize(colors=colors, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.FLOYDSTEINBERG).convert('RGB')
    im.save(path, optimize=True)
    print(os.path.basename(path), im.size, os.path.getsize(path) // 1024, 'KB')


def main():
    os.makedirs(OUT, exist_ok=True)
    scene = Image.open(sys.argv[1]).convert('RGB')
    bg = grade(scene, warmth=1.02)
    save_small(bg, os.path.join(OUT, 'background.png'))
    frames = sorted(glob.glob(os.path.join(sys.argv[2], 'menu_orbit_*.png')), key=lambda p: int(p.rsplit('_', 1)[1][:-4]))
    for i, f in enumerate(frames):
        im = grade(Image.open(f).convert('RGB'), warmth=1.03, contrast=1.04, saturation=1.1)
        im = im.resize((1280, 720), Image.LANCZOS).filter(ImageFilter.UnsharpMask(radius=1.2, percent=40, threshold=2))
        save_small(im, os.path.join(OUT, f'preview_{i}.png'))


if __name__ == '__main__':
    main()
