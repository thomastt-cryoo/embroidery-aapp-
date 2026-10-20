"""Lossless encoding of ICNS PNG frames; retains all sizes, colours and pixels."""
import hashlib
import io
import json
from pathlib import Path
import struct
import subprocess
import tempfile
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
path = ROOT / 'app/src-tauri/icons/icon.icns'
tool = next((ROOT / 'reports/M2/build-artifacts/tools/verified-x86_64-pc-windows-msvc').rglob('oxipng.exe'))
original = path.read_bytes()
assert original[:4] == b'icns' and int.from_bytes(original[4:8], 'big') == len(original)


def pixels(data):
    with Image.open(io.BytesIO(data)) as im:
        return (im.size, hashlib.sha256(im.convert('RGBA').tobytes()).hexdigest(), im.info.get('icc_profile', b''))


frames = []; cache = {}; position = 8; records = []
with tempfile.TemporaryDirectory(prefix='embrova-icon-encoding-') as folder:
    while position < len(original):
        kind = original[position:position+4]
        length = int.from_bytes(original[position+4:position+8], 'big')
        data = original[position+8:position+length]
        assert length >= 8 and len(data) == length-8
        position += length
        result = data
        if data.startswith(b'\x89PNG\r\n\x1a\n'):
            digest = hashlib.sha256(data).hexdigest()
            if digest not in cache:
                temp = Path(folder) / (digest+'.png')
                temp.write_bytes(data)
                subprocess.run([tool, '-o', '4', '--strip', 'eXIf,tIME,tEXt,iTXt,zTXt', '--threads', '2', temp],
                               check=True, capture_output=True)
                optimized = temp.read_bytes()
                assert pixels(optimized) == pixels(data), 'An icon frame changed pixels or profile'
                cache[digest] = optimized if len(optimized) < len(data) else data
            result = cache[digest]
        frames.append(kind+struct.pack('>I', len(result)+8)+result)
        records.append({'kind': kind.decode(), 'beforeBytes': len(data), 'afterBytes': len(result),
                        'pixelsUnchanged': True, 'allResolutionsRetained': True})
assert position == len(original)
encoded = b''.join(frames)
encoded = b'icns'+struct.pack('>I', len(encoded)+8)+encoded
path.write_bytes(encoded)
out = ROOT / 'reports/embrova-branding'
out.mkdir(exist_ok=True)
(out / 'icon-lossless-encoding.json').write_text(json.dumps({'beforeBytes':len(original),
    'afterBytes':len(encoded), 'savedBytes':len(original)-len(encoded), 'frames':records,
    'sourceArtworkCropped':False, 'colourQuantization':False, 'resolutionsRemoved':False},indent=2)+'\n')
print('ICNS lossless encoding:',len(original),'->',len(encoded),'bytes; every frame/pixel/profile retained')
