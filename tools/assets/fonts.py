"""Menu fonts: Inter (SIL OFL 1.1), subset to Latin-1 plus typographic punctuation, and the
Minecraft font definitions that use them. Run from the repository root; needs fontTools."""
import json
import os
from fontTools import subset
from fontTools.ttLib import TTFont

SRC = '/usr/share/fonts/opentype/inter'
OUT = 'src/main/resources/assets/recrafted/font'
CHARS = ''.join(chr(c) for c in range(0x20, 0x7f)) + ''.join(chr(c) for c in range(0xa0, 0x100)) + '—–‘’“”•…·←→↑↓▸✕×'
FACES = {  # file in OUT -> source face
    'inter_display_bold.otf': 'InterDisplay-Bold.otf',
    'inter_semibold.otf': 'Inter-SemiBold.otf',
    'inter_medium.otf': 'Inter-Medium.otf',
    'inter_regular.otf': 'Inter-Regular.otf',
}
# font id -> (file, size in gui pixels, vertical shift)
FONTS = {
    'menu_title': ('inter_display_bold.otf', 28, 0.0),
    'menu_heading': ('inter_display_bold.otf', 15, 0.5),
    'menu_button': ('inter_semibold.otf', 12, 0.5),
    'menu_label': ('inter_semibold.otf', 7, 0.5),
    'menu_text': ('inter_regular.otf', 8, 0.5),
    'menu_small': ('inter_medium.otf', 6.5, 0.5),
}


def main():
    os.makedirs(OUT, exist_ok=True)
    opts = subset.Options()
    opts.layout_features = ['kern', 'liga']
    opts.name_IDs = ['*']
    opts.notdef_outline = True
    for out, src in FACES.items():
        f = TTFont(os.path.join(SRC, src))
        s = subset.Subsetter(opts)
        s.populate(text=CHARS)
        s.subset(f)
        f.save(os.path.join(OUT, out))
        print(out, os.path.getsize(os.path.join(OUT, out)))
    for fid, (file, size, shift) in FONTS.items():
        with open(os.path.join(OUT, fid + '.json'), 'w') as fh:
            json.dump({'providers': [{'type': 'ttf', 'file': 'recrafted:' + file, 'size': size, 'oversample': 4.0,
                                      'shift': [0.0, shift], 'skip': ''}]}, fh, indent=2)
            fh.write('\n')
    with open('/usr/share/doc/fonts-inter/copyright') as fh:
        text = fh.read()
    start = text.index('License: OFL-1.1\n')
    body = '\n'.join(l[1:] if l.startswith(' ') else l for l in text[start:].split('\n')[1:])
    body = body.split('\nLicense:')[0].replace('\n.\n', '\n\n')
    with open(os.path.join(OUT, 'inter_license.txt'), 'w') as fh:
        fh.write('Inter typeface\nCopyright (c) 2016-2023 The Inter Project Authors (https://github.com/rsms/inter)\n\n'
                 'This Font Software is licensed under the SIL Open Font License, Version 1.1.\n'
                 'The files in this folder are subsets of the original fonts.\n\n' + body.strip() + '\n')


if __name__ == '__main__':
    main()
