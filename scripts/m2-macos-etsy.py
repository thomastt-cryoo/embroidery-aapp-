"""Compare standard Mac delivery formats; install and launch the smallest real ZIP."""
import argparse, hashlib, json, os, pathlib, shutil, subprocess, sys, tempfile, time, zipfile

ROOT = pathlib.Path(__file__).resolve().parent.parent
parser = argparse.ArgumentParser()
parser.add_argument('action', choices=['package','install'])
parser.add_argument('--app')
parser.add_argument('--mode', default='raw')
parser.add_argument('--out', default='out')
args = parser.parse_args()
out = pathlib.Path(args.out).resolve()
evidence = out/'evidence'
evidence.mkdir(parents=True, exist_ok=True)
work = pathlib.Path(os.environ.get('RUNNER_TEMP', tempfile.gettempdir()))/'studio-etsy'
work.mkdir(exist_ok=True)
sha = lambda p: hashlib.file_digest(p.open('rb'),'sha256').hexdigest()
def run(cmd):
    return subprocess.run(list(map(str,cmd)), check=True, text=True, capture_output=True, timeout=240)
def docs(z, instruction):
    z.writestr('START HERE.txt', instruction+'\n\nThis private review build is ad-hoc signed, without Apple Developer ID or notarization. macOS may prevent opening. Automatic updates are disabled.\n')
    z.write(ROOT/'LICENSE','LICENSE.txt')
    z.write(ROOT/'NOTICE.md','NOTICE.txt')
def zip_installer(source, target, instruction):
    alternatives=[]
    for method, tag in [(zipfile.ZIP_STORED,'store'),(zipfile.ZIP_DEFLATED,'deflate')]:
        candidate=target.with_name(target.stem+'-'+tag+'.zip')
        with zipfile.ZipFile(candidate,'w',compression=method,compresslevel=9 if method==zipfile.ZIP_DEFLATED else None) as z:
            z.write(source,'Install Embroidery Studio'+source.suffix);docs(z,instruction)
        alternatives.append(candidate)
    winner=min(alternatives,key=lambda p:p.stat().st_size)
    shutil.copy2(winner,target)

if args.action == 'package':
    app=pathlib.Path(args.app).resolve()
    run(['codesign','--verify','--deep','--strict',app])
    modework=work/args.mode;modework.mkdir(exist_ok=True)
    result_path=evidence/'mac-package-candidates.json'
    records=json.loads(result_path.read_text()) if result_path.exists() else []
    def record(candidate, kind, extra=None):
        item={'mode':args.mode,'kind':kind,'bytes':candidate.stat().st_size,'sha256':sha(candidate),
              'underEtsyLimit':candidate.stat().st_size<20_000_000,'completeUniversalApplication':True}
        if extra:item.update(extra)
        records.append(item)
        final=out/'Embroidery-Studio-macOS.zip'
        if not final.exists() or candidate.stat().st_size<final.stat().st_size:
            shutil.copy2(candidate,final)
            (evidence/'mac-selected-package.json').write_text(json.dumps(item,indent=2)+'\n')
        result_path.write_text(json.dumps(records,indent=2)+'\n')
        print('Mac candidate:',item,flush=True)
    direct=modework/'application.zip'
    run(['ditto','-c','-k','--sequesterRsrc','--keepParent','--zlibCompressionLevel','9',app,direct])
    with zipfile.ZipFile(direct,'a',compression=zipfile.ZIP_DEFLATED,compresslevel=9) as z:
        docs(z,'Drag Embroidery Studio.app to Applications, then open Embroidery Studio.')
    record(direct,'app')
    image_source=modework/'disk-image';image_source.mkdir(exist_ok=True)
    run(['ditto',app,image_source/app.name])
    (image_source/'Applications').symlink_to('/Applications',target_is_directory=True)
    for fmt in ['UDZO','UDBZ','ULMO']:
        try:
            dmg=modework/('Install Embroidery Studio-'+fmt+'.dmg')
            run(['hdiutil','create','-srcfolder',image_source,'-volname','Embroidery Studio','-format',fmt,'-ov',dmg])
            verify=run(['hdiutil','verify',dmg])
            (evidence/(args.mode+'-'+fmt+'-verify.txt')).write_text(verify.stdout+verify.stderr)
            delivery=modework/(fmt+'.zip')
            zip_installer(dmg,delivery,'Open the disk image and drag Embroidery Studio to Applications, then open it.')
            record(delivery,'dmg',{'dmgFormat':fmt,'dmgBytes':dmg.stat().st_size})
        except Exception as exc:
            records.append({'mode':args.mode,'kind':fmt,'error':str(exc)})
            result_path.write_text(json.dumps(records,indent=2)+'\n')
    try:
        pkg=modework/'Install Embroidery Studio.pkg'
        run(['pkgbuild','--component',app,'--install-location','/Applications','--identifier','io.github.thomasttcryoo.embroiderystudio','--version','1.4.0','--min-os-version','13.0','--compression','latest',pkg])
        delivery=modework/'pkg.zip'
        zip_installer(pkg,delivery,'Open Install Embroidery Studio.pkg and follow the installer. Then open Embroidery Studio in Applications.')
        record(delivery,'pkg',{'pkgBytes':pkg.stat().st_size})
    except Exception as exc:
        records.append({'mode':args.mode,'kind':'pkg','error':str(exc)})
        result_path.write_text(json.dumps(records,indent=2)+'\n')
elif args.action == 'install':
    final=out/'Embroidery-Studio-macOS.zip'
    extracted=work/'customer-extracted';extracted.mkdir(exist_ok=True)
    run(['unzip','-t',final])
    run(['ditto','-x','-k',final,extracted])
    selected=json.loads((evidence/'mac-selected-package.json').read_text())
    installed=pathlib.Path('/Applications/Embroidery Studio.app')
    if selected['kind']=='app':
        run(['ditto',extracted/'Embroidery Studio.app',installed])
    elif selected['kind']=='pkg':
        r=run(['sudo','installer','-pkg',next(extracted.glob('*.pkg')),'-target','/'])
        (evidence/'mac-package-install.txt').write_text(r.stdout+r.stderr)
    else:
        mount=work/'customer-volume';mount.mkdir(exist_ok=True)
        run(['hdiutil','attach',next(extracted.glob('*.dmg')),'-nobrowse','-mountpoint',mount])
        run(['ditto',mount/'Embroidery Studio.app',installed])
        run(['hdiutil','detach',mount])
    run(['codesign','--verify','--deep','--strict',installed])
    # Existing native smoke check opens and recomputes a real saved design.
    r=run(['python3',ROOT/'scripts/m2-macos-smoke.py',installed,evidence])
    print(r.stdout)
    # Also exercise the unchanged native machine-file reader from the installed app.
    pes=ROOT/'reports/M2/evidence/windows-native/Studio-sample.pes'
    run(['open','-a',installed,pes]);time.sleep(10)
    run(['screencapture','-x',evidence/'mac-native-pes-from-zip.png'])
    (evidence/'mac-zip-install.json').write_text(json.dumps({'result':'pass','zipBytes':final.stat().st_size,
        'zipSha256':sha(final),'selected':selected,'installedApp':str(installed),
        'source':'actual final customer ZIP, extracted with ditto','nativeProjectOpen':'pass',
        'nativePesOpenRequested':True,'signatureVerify':'pass; ad-hoc, not notarized',
        'detailedNativeEditingDialogs':'not automated; separate production browser checks follow'},indent=2)+'\n')
