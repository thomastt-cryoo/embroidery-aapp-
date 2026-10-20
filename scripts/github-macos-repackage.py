"""Reuse a built universal app, optionally refreshing only its native Dock icon."""
import hashlib
import json
import os
from pathlib import Path
import plistlib
import re
import shutil
import struct
import subprocess
import zipfile

root = Path(__file__).resolve().parent.parent
assert os.environ.get('GITHUB_ACTIONS') == 'true' and os.uname().sysname == 'Darwin'
run_id = os.environ['SOURCE_BUILD_RUN']
assert run_id.isdigit()
source = root / 'received/Embrova-macOS.zip'
work = root / 'replay'
work.mkdir()
with zipfile.ZipFile(source) as z:
    assert z.testzip() is None
    assert sorted(z.namelist()) == ['Install Embrova.pkg', 'LICENSE.txt', 'NOTICE.txt', 'START HERE.txt']
    package = work / 'source.pkg'
    package.write_bytes(z.read('Install Embrova.pkg'))
assert package.read_bytes().startswith(b'xar!')
subprocess.run(['pkgutil', '--expand-full', package, work / 'expanded'], check=True)
apps = list((work / 'expanded').rglob('Embrova.app'))
assert len(apps) == 1
app = apps[0]
info = plistlib.loads((app / 'Contents/Info.plist').read_bytes())
assert info['CFBundleName'] == 'Embrova'
assert info['CFBundleIdentifier'] == 'io.github.thomasttcryoo.embroiderystudio'
binary = app / 'Contents/MacOS' / info['CFBundleExecutable']
icon_name = info['CFBundleIconFile']
if not icon_name.endswith('.icns'):
    icon_name += '.icns'
icon = app / 'Contents/Resources' / icon_name
icon_sha = hashlib.sha256(icon.read_bytes()).hexdigest()
desired_icon = root / 'app/src-tauri/icons/icon.icns'
source_environment = (root / 'received/evidence/environment.txt').read_text()
source_commits = re.findall(r'^[a-f0-9]{40}$', source_environment, re.M)
assert len(source_commits) == 1, 'Original source commit evidence is missing'
arches = subprocess.check_output(['lipo', '-archs', binary], text=True).split()
assert {'arm64', 'x86_64'} <= set(arches)
subprocess.run(['codesign', '--verify', '--deep', '--strict', '--all-architectures', app], check=True)
original_binary_sha = hashlib.sha256(binary.read_bytes()).hexdigest()


def manifest():
    return {str(p.relative_to(app)): (str(p.readlink()) if p.is_symlink() else hashlib.sha256(p.read_bytes()).hexdigest(), p.lstat().st_mode & 0o7777)
            for p in app.rglob('*') if p.is_symlink() or p.is_file()}


def unsigned_content(architecture, tag):
    """Hash every executable/asset byte, excluding only signature metadata."""
    thin = work / (tag + '-' + architecture)
    subprocess.run(['lipo', binary, '-thin', architecture, '-output', thin], check=True)
    data = thin.read_bytes()
    assert data[:4] == b'\xcf\xfa\xed\xfe', 'Expected a 64-bit little-endian Mach-O slice'
    commands = struct.unpack_from('<I', data, 16)[0]
    offset = 32
    edits = []
    signature_offset = None
    for _ in range(commands):
        command, size = struct.unpack_from('<II', data, offset)
        assert size >= 8 and offset + size <= len(data)
        if command == 0x1d:  # LC_CODE_SIGNATURE
            signature_offset, signature_size = struct.unpack_from('<II', data, offset + 8)
            assert signature_offset + signature_size <= len(data)
            edits.append((offset + 8, 8))
        elif command == 0x19 and data[offset + 8:offset + 24].rstrip(b'\0') == b'__LINKEDIT':
            # Its file/memory extent may grow when a resource seal is renewed.
            edits.extend([(offset + 32, 8), (offset + 48, 8)])
        offset += size
    assert signature_offset is not None and signature_offset >= offset
    normalized = bytearray(data[:signature_offset])
    for location, size in edits:
        normalized[location:location + size] = b'\0' * size
    return hashlib.sha256(normalized).hexdigest()


changed_files = []
code_hashes = {}
if icon_sha != hashlib.sha256(desired_icon.read_bytes()).hexdigest():
    assert os.environ.get('REFRESH_NATIVE_ICON') == '1', 'Native icon differs; explicit icon refresh was not selected'
    before = manifest()
    code_hashes = {a: unsigned_content(a, 'before') for a in arches}
    shutil.copy2(desired_icon, icon)
    subprocess.run(['codesign', '--force', '--sign', '-', '--preserve-metadata=identifier,entitlements,requirements,flags', '--timestamp=none', app], check=True)
    subprocess.run(['codesign', '--verify', '--deep', '--strict', '--all-architectures', app], check=True)
    assert {a: unsigned_content(a, 'after') for a in arches} == code_hashes, 'Re-signing altered executable code or embedded runtime assets'
    after = manifest()
    assert before.keys() == after.keys(), 'Icon refresh added or removed application files'
    changed_files = [p for p in before if before[p] != after[p]]
    allowed = {str(icon.relative_to(app)), str(binary.relative_to(app)), 'Contents/_CodeSignature/CodeResources'}
    assert set(changed_files) <= allowed, 'Icon refresh changed an unrelated runtime file'
    icon_sha = hashlib.sha256(icon.read_bytes()).hexdigest()
assert icon_sha == hashlib.sha256(desired_icon.read_bytes()).hexdigest()
out = root / 'out/evidence'
out.mkdir(parents=True)
record = {'sourceBuildRun': run_id, 'sourceZipSha256': hashlib.sha256(source.read_bytes()).hexdigest(),
          'applicationSourceCommit': source_commits[0], 'nativeIconSha256': icon_sha,
          'binarySha256': hashlib.sha256(binary.read_bytes()).hexdigest(), 'architectures': arches,
          'originalBinarySha256': original_binary_sha, 'executableCodeAndEmbeddedAssetsUnchanged': True,
          'normalizedCodeHashes': code_hashes, 'changedFiles': changed_files,
          'applicationRebuilt': False, 'applicationFilesModified': bool(changed_files),
          'nativeIconRefreshed': bool(changed_files), 'originalSignature': 'verified strict, all architectures',
          'finalSignature': 'verified strict, all architectures; ad-hoc'}
(out / 'repackaging-source.json').write_text(json.dumps(record, indent=2) + '\n')
with Path(os.environ['GITHUB_ENV']).open('a') as f:
    f.write('RECOVERED_APP=' + str(app) + '\n')
