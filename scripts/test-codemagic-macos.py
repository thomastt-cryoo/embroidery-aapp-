"""Local contract tests only; these never claim that a Mac build was executed."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import zipfile

spec = importlib.util.spec_from_file_location('mac_report', Path(__file__).with_name('codemagic-macos-report.py'))
report = importlib.util.module_from_spec(spec)
spec.loader.exec_module(report)


class ReportAndPackageTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.out = Path(self.temp.name)
        (self.out / 'evidence').mkdir()

    def package(self, payload=b'xar!test-only-structural-fixture'):
        path = self.out / 'Embrova-macOS.zip'
        with zipfile.ZipFile(path, 'w', zipfile.ZIP_STORED) as z:
            z.writestr('Install Embrova.pkg', payload)
            for name in ['LICENSE.txt', 'NOTICE.txt', 'START HERE.txt']:
                z.writestr(name, 'Unit test fixture; never customer delivery.')
        selected = dict(sha256=hashlib.sha256(path.read_bytes()).hexdigest(), kind='pkg', completeUniversalApplication=True)
        (self.out / 'evidence/mac-selected-package.json').write_text(json.dumps(selected))
        return path

    def test_accepts_one_complete_sealed_zip_and_reads_back_installer(self):
        path = self.package()
        result = report.validate_package(self.out)
        self.assertTrue(result['underLimit'])
        self.assertEqual(result['zipBytes'], path.stat().st_size)
        self.assertEqual((self.out / 'installers/Install Embrova.pkg').read_bytes(), b'xar!test-only-structural-fixture')

    def test_rejects_changed_zip(self):
        path = self.package()
        with path.open('ab') as f:
            f.write(b'changed')
        with self.assertRaisesRegex(AssertionError, 'changed'):
            report.validate_package(self.out)

    def test_rejects_limit_boundary_preserving_oversize_evidence(self):
        path = self.package()
        overhead = path.stat().st_size - len(b'xar!test-only-structural-fixture')
        path = self.package(b'xar!' + b'0' * (20_000_000 - overhead - 4))
        self.assertEqual(path.stat().st_size, 20_000_000)
        with self.assertRaisesRegex(AssertionError, 'exceeds Etsy limit'):
            report.validate_package(self.out)
        self.assertFalse(json.loads((self.out / 'evidence/size-gate.json').read_text())['underLimit'])
        self.assertTrue(path.exists())

    def test_explicit_owner_exception_records_target_failure_without_discarding_package(self):
        path = self.package()
        overhead = path.stat().st_size - len(b'xar!test-only-structural-fixture')
        self.package(b'xar!' + b'0' * (20_000_000 - overhead - 4))
        with patch.dict(os.environ, {'MAC_OWNER_ACCEPTED_SIZE_EXCEPTION': '1'}):
            result = report.validate_package(self.out)
        self.assertFalse(result['underLimit'])
        self.assertTrue(result['ownerAcceptedSizeException'])
        self.assertEqual(result['zipBytes'], 20_000_000)

    def test_no_run_cannot_be_reported_as_passing(self):
        self.assertFalse(report.render_report(self.out, 0))
        text = (self.out / 'M3_MACOS_RUN_REPORT.md').read_text()
        self.assertIn('INCOMPLETE / FAILED', text)
        self.assertIn('Gatekeeper consumer testing: NOT COMPLETED', text)
        self.assertIn('No customer-facing screenshots were captured', (self.out / 'MACOS_ILLUSTRATED_GUIDE_DRAFT.md').read_text())

    def test_missing_native_permissions_remain_blocked(self):
        (self.out / 'evidence/test-stages.json').write_text(json.dumps([
            dict(name='Installed native app', status='blocked', detail='Accessibility missing'),
            dict(name='Browser regression', status='pass', detail='13 exports'),
        ]))
        self.assertFalse(report.render_report(self.out, 0))
        self.assertIn('| Installed native app | blocked |', (self.out / 'M3_MACOS_RUN_REPORT.md').read_text())
        with zipfile.ZipFile(self.out / 'Mac-QA-evidence.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertNotIn('Embrova-macOS.zip', z.namelist())

    def test_verification_only_cannot_pass_without_all_native_stages(self):
        (self.out / 'evidence/run-mode.json').write_text(json.dumps({'mode': 'verification-only'}))
        (self.out / 'evidence/size-gate.json').write_text(json.dumps({'underLimit': True, 'zipBytes': 19861169}))
        stages = [dict(name='Desktop permission probe (read-only)', status='pass', detail='authorized')]
        (self.out / 'evidence/test-stages.json').write_text(json.dumps(stages))
        self.assertFalse(report.render_report(self.out, 0))
        for name in ['M3 GUI installation walkthrough', 'Ordinary CI installation from the actual customer ZIP',
                     'Installed native app functional tests']:
            stages.append(dict(name=name, status='pass', detail='test fixture'))
        (self.out / 'evidence/test-stages.json').write_text(json.dumps(stages))
        self.assertTrue(report.render_report(self.out, 0))
        text = (self.out / 'M3_MACOS_RUN_REPORT.md').read_text()
        self.assertIn('those are historical results', text)
        self.assertIn('Gatekeeper consumer testing: NOT COMPLETED', text)

    def test_rebuild_requires_package_checks_and_does_not_claim_native_tests(self):
        self.assertFalse(report.render_rebuild_report(self.out, 0))
        self.package()
        report.validate_package(self.out)
        self.assertFalse(report.render_rebuild_report(self.out, 0))
        (self.out / 'evidence/rebuild-package.passed').write_text('test fixture')
        self.assertTrue(report.render_rebuild_report(self.out, 0))
        self.assertFalse(report.render_rebuild_report(self.out, 1))
        report.render_rebuild_report(self.out, 0)
        text = (self.out / 'MACOS_REBUILD_REPORT.md').read_text(encoding='utf-8')
        self.assertIn('BUILD AND PACKAGE CHECKS PASSED', text)
        self.assertIn('does not cover installation or application use', text)
        self.assertIn('tests were not repeated', text)
        self.assertFalse((self.out / 'M3_MACOS_RUN_REPORT.md').exists())
        with zipfile.ZipFile(self.out / 'Mac-QA-evidence.zip') as z:
            self.assertIsNone(z.testzip())
            self.assertIn('MACOS_REBUILD_REPORT.md', z.namelist())
            self.assertNotIn('Embrova-macOS.zip', z.namelist())


if __name__ == '__main__':
    unittest.main()
