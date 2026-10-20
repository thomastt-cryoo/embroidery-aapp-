"""Build-only, lossless PKG payload compression; no customer reconstruction step.

Keeps pkgbuild's native pbzx/XZ container and every decoded cpio byte. A longer
compression window can reference identical runtime assets in both Mach-O slices.
Apple's native package reader and codesign must accept the result before use.
"""
import hashlib,json,lzma,pathlib,struct,subprocess,sys,tempfile,time

source,target,evidence=map(pathlib.Path,sys.argv[1:4])
def run(*args):
    result=subprocess.run(list(map(str,args)),text=True,capture_output=True,timeout=240)
    if result.returncode:raise RuntimeError(result.stdout+result.stderr)
    return result
def digest(data):return hashlib.sha256(data).hexdigest()
def decode(data):
    assert data[:4]==b'pbzx','Expected native pkgbuild latest-compression payload'
    position=12;parts=[]
    while position<len(data):
        inflated,stored=struct.unpack('>QQ',data[position:position+16]);position+=16
        chunk=data[position:position+stored];position+=stored
        assert len(chunk)==stored
        raw=chunk if stored==inflated else lzma.decompress(chunk)
        assert len(raw)==inflated
        parts.append(raw)
    assert position==len(data)
    return b''.join(parts)
def manifest(app):
    result=[]
    for path in sorted(app.rglob('*')):
        item={'path':path.relative_to(app).as_posix(),'mode':path.lstat().st_mode&0o7777}
        if path.is_symlink():item['link']=str(path.readlink())
        elif path.is_file():item['sha256']=hashlib.file_digest(path.open('rb'),'sha256').hexdigest()
        else:continue
        result.append(item)
    return result
started=time.monotonic()
with tempfile.TemporaryDirectory(prefix='studio-pkg-compression-') as folder:
    work=pathlib.Path(folder);expanded=work/'expanded'
    run('pkgutil','--expand',source,expanded)
    payload=expanded/'Payload';raw=decode(payload.read_bytes())
    # This app is below 256 MiB decoded. Installer memory remains bounded and
    # both architectures and every asset stay in the exact original cpio.
    assert len(raw)<256*1024*1024
    options={'id':lzma.FILTER_LZMA2,'dict_size':128*1024*1024,'preset':9|lzma.PRESET_EXTREME}
    # The complete format comparison established BCJ + LZMA2 as the smallest.
    # Start with that verified setting to avoid spending runner time twice.
    packed=lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_NONE,filters=[{'id':lzma.FILTER_X86},options])
    candidates=[{'filter':'X86 + LZMA2','bytes':len(packed)}];selected='X86 + LZMA2'
    if len(packed)>=19_900_000:
        alternate=lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_NONE,
            filters=[options])
        candidates.append({'filter':'LZMA2','bytes':len(alternate)})
        if len(alternate)<len(packed):packed=alternate;selected='LZMA2'
    # Larger branding assets may move the complete ZIP close to Etsy's limit.
    # Try only storage-context tuning; every decoded payload byte stays exact.
    if len(packed)>=19_950_000:
        for lc,pb in [(0,0),(4,0),(2,2)]:
            tuned=dict(options,lc=lc,lp=0,pb=pb)
            candidate=lzma.compress(raw,format=lzma.FORMAT_XZ,check=lzma.CHECK_NONE,
                filters=[{'id':lzma.FILTER_X86},tuned])
            label=f'X86 + LZMA2 lc={lc} pb={pb}'
            candidates.append({'filter':label,'bytes':len(candidate)})
            if len(candidate)<len(packed):packed=candidate;selected=label
            if len(packed)<19_950_000:break
    container=b'pbzx'+struct.pack('>QQQ',256*1024*1024,len(raw),len(packed))+packed
    assert decode(container)==raw,'Compression changed decoded payload bytes'
    payload.write_bytes(container)
    run('pkgutil','--flatten',expanded,target)
    before=work/'native-before';after=work/'native-after'
    run('pkgutil','--expand-full',source,before)
    run('pkgutil','--expand-full',target,after)
    old_app=next(before.rglob('Embrova.app'));new_app=next(after.rglob('Embrova.app'))
    files=manifest(old_app)
    assert files==manifest(new_app),'Native package extraction changed application files or permissions'
    run('codesign','--verify','--deep','--strict','--all-architectures',new_app)
    report={'result':'pass','originalPkgBytes':source.stat().st_size,'pkgBytes':target.stat().st_size,
        'decodedPayloadBytes':len(raw),'decodedPayloadSha256':digest(raw),'decodedPayloadByteIdentical':True,
        'nativeExpandFullIdentical':True,'nativeAppManifest':files,'signatureVerification':'all architectures; strict',
        'compression':'native pbzx / one XZ stream / 128 MiB dictionary / 256 MiB block limit',
        'selectedFilter':selected,'compressionCandidates':candidates,
        'customerInstallScripts':False,'seconds':round(time.monotonic()-started,2)}
    evidence.write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps({k:v for k,v in report.items() if k!='nativeAppManifest'},indent=2),flush=True)
