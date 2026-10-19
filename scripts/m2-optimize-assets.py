"""Build-only lossless preview compression. Customers need no Python or tools."""
import hashlib, io, json, os, pathlib, platform, subprocess, tarfile, urllib.request, zipfile
from PIL import Image

ROOT = pathlib.Path(__file__).resolve().parent.parent
DIST = ROOT / 'editor/dist'
EVIDENCE = ROOT / 'reports/M2/etsy'
CACHE = ROOT / 'reports/M2/build-artifacts/tools'
EVIDENCE.mkdir(parents=True, exist_ok=True)
CACHE.mkdir(parents=True, exist_ok=True)
VERSION = '10.2.1'
if platform.system() == 'Windows':
    name, digest, binary = 'x86_64-pc-windows-msvc.zip', '7e940f83ee46874b73f53031f96a15834cb70b220af27391fb06fe7b4dd798e1', 'oxipng.exe'
elif platform.machine() == 'arm64':
    name, digest, binary = 'aarch64-apple-darwin.tar.gz', '7039fcfc78e8aa1ed2b57d848057a0296f082e92b3e1807ac65402d10d926764', 'oxipng'
else:
    name, digest, binary = 'x86_64-apple-darwin.tar.gz', '111883bbe42b25e01cb1ca41f39f8094e4830b173f0e42be342ecc4ca48f3131', 'oxipng'
archive = CACHE / ('oxipng-' + VERSION + '-' + name)
if not archive.exists():
    url = 'https://github.com/oxipng/oxipng/releases/download/v'+VERSION+'/'+archive.name
    archive.write_bytes(urllib.request.urlopen(url, timeout=90).read())
assert hashlib.sha256(archive.read_bytes()).hexdigest() == digest, 'Optimizer download checksum mismatch'
tool_dir = CACHE / ('verified-' + name.split('.')[0])
if not tool_dir.exists():
    tool_dir.mkdir()
    if name.endswith('.zip'):
        with zipfile.ZipFile(archive) as z:
            for entry in z.infolist():
                assert (tool_dir / entry.filename).resolve().is_relative_to(tool_dir.resolve())
            z.extractall(tool_dir)
    else:
        with tarfile.open(archive) as t:
            t.extractall(tool_dir, filter='data')
tool = next(tool_dir.rglob(binary))
if platform.system() != 'Windows': tool.chmod(0o755)
sha = lambda b: hashlib.sha256(b).hexdigest()
def pixels(p):
    with Image.open(p) as image:
        return {'dimensions': image.size, 'rgbaSha256': sha(image.convert('RGBA').tobytes()),
                'iccSha256': sha(image.info.get('icc_profile', b'')),
                'gamma': image.info.get('gamma'), 'srgb': image.info.get('srgb')}
files = sorted(p for p in DIST.rglob('*') if p.is_file())
original = {str(p.relative_to(DIST)): {'bytes':p.stat().st_size, 'sha256':sha(p.read_bytes())} for p in files}
pngs = [p for p in files if p.suffix.lower() == '.png']
before_pixels = {p:pixels(p) for p in pngs}
original_pngs = {p:p.read_bytes() for p in pngs}
subprocess.run([str(tool), '-o', '4', '--strip', 'eXIf,tIME,tEXt,iTXt,zTXt', '--threads', '2', *map(str,pngs)], check=True)
restored = []
for p in pngs:
    if pixels(p) != before_pixels[p]:
        # Reject even a metadata normalization if our strict colour/pixel check
        # cannot prove equivalence. Keep that original preview unchanged.
        p.write_bytes(original_pngs[p])
        restored.append(str(p.relative_to(DIST)))
    assert pixels(p) == before_pixels[p], 'Preview pixels or colour interpretation changed: '+str(p)
for p in files:
    if p not in before_pixels:
        assert sha(p.read_bytes()) == original[str(p.relative_to(DIST))]['sha256'], 'Non-PNG runtime asset changed'
assert len(files) == len([p for p in DIST.rglob('*') if p.is_file()]), 'Asset count changed'
result = {'optimizer':'oxipng '+VERSION,'mode':'lossless; safe metadata only; no alpha alteration',
          'fileCount':len(files),'pngCount':len(pngs),'originalBytes':sum(v['bytes'] for v in original.values()),
          'optimizedBytes':sum(p.stat().st_size for p in files),'allPreviewPixelsAndColourProfilesIdentical':True,
          'allOtherRuntimeFilesByteIdentical':True,
          'previewsRetainedUnmodifiedForStrictEquivalence':restored,
          'files':[{'path':str(p.relative_to(DIST)), 'before':original[str(p.relative_to(DIST))],
                    'afterBytes':p.stat().st_size,'afterSha256':sha(p.read_bytes())} for p in files]}
(EVIDENCE/'asset-preservation.json').write_text(json.dumps(result,indent=2)+'\n')
print('PASS: all',len(files),'assets retained;',len(pngs),'previews losslessly optimized;',
      result['originalBytes']-result['optimizedBytes'],'bytes saved; pixels, profiles, fonts, WASM and code preserved.')
