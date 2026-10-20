"""Packaging control-flow tests with fixtures; never claims native Mac validation."""
import contextlib
import hashlib
import io
import json
import os
from pathlib import Path
import plistlib
import random
import runpy
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile


class CompressionCheckpointTests(unittest.TestCase):
    def exercise(self, checkpoint):
        with tempfile.TemporaryDirectory() as folder:
            work = Path(folder)
            app = work / 'Embrova.app'
            app.mkdir()
            out = work / 'out'
            raw = b'xar!' + random.Random(1).randbytes(10000)
            compact = b'xar!' + random.Random(2).randbytes(1000)

            def tool(args, **kwargs):
                argv = list(map(str, args))
                if argv[0] == 'ditto':
                    Path(argv[-1]).mkdir(parents=True, exist_ok=True)
                elif argv[0] == 'pkgbuild':
                    if '--analyze' in argv:
                        Path(argv[-1]).write_bytes(plistlib.dumps([{'BundleIsRelocatable': True}]))
                    else:
                        Path(argv[-1]).write_bytes(raw)
                elif len(argv) > 1 and argv[1].endswith('m2-macos-recompress.py'):
                    if checkpoint != 'missing':
                        target, evidence = map(Path, argv[-2:])
                        target.write_bytes(compact)
                        evidence.write_text(json.dumps({
                            'result': 'pass', 'decodedPayloadByteIdentical': True,
                            'nativeExpandFullIdentical': True, 'pkgBytes': len(compact),
                            'pkgSha256': hashlib.sha256(compact).hexdigest() if checkpoint == 'valid' else '0' * 64,
                        }))
                    raise subprocess.TimeoutExpired(argv, 900)
                return subprocess.CompletedProcess(argv, 0, '', '')

            argv = ['m2-macos-etsy.py', 'package', '--app', str(app), '--mode', 'fixture', '--pkg-only', '--out', str(out)]
            with patch.object(sys, 'argv', argv), patch.dict(os.environ, {'RUNNER_TEMP': folder}), \
                 patch('subprocess.run', side_effect=tool), patch.object(Path, 'symlink_to'), \
                 contextlib.redirect_stdout(io.StringIO()):
                runpy.run_path(str(Path(__file__).with_name('m2-macos-etsy.py')), run_name='__main__')
            selected = json.loads((out / 'evidence/mac-selected-package.json').read_text())
            records = json.loads((out / 'evidence/mac-package-candidates.json').read_text())
            with zipfile.ZipFile(out / 'Embrova-macOS.zip') as z:
                self.assertIsNone(z.testzip())
                actual = z.read('Install Embrova.pkg')
            return raw, compact, actual, selected, records

    def test_timeout_retains_already_verified_complete_checkpoint(self):
        raw, compact, actual, selected, records = self.exercise('valid')
        self.assertEqual(actual, compact)
        self.assertTrue(selected['nativeExtractionVerified'])
        self.assertTrue(any('timed out' in item.get('error', '') for item in records))

    def test_changed_checkpoint_cannot_be_delivered_as_verified(self):
        raw, compact, actual, selected, records = self.exercise('changed')
        self.assertEqual(actual, raw)
        self.assertNotIn('nativeExtractionVerified', selected)
        self.assertTrue(any('Invalid compression checkpoint' in item.get('error', '') for item in records))

    def test_timeout_without_checkpoint_retains_complete_original(self):
        raw, compact, actual, selected, records = self.exercise('missing')
        self.assertEqual(actual, raw)
        self.assertNotIn('nativeExtractionVerified', selected)


if __name__ == '__main__':
    unittest.main()
