"""Local-only launcher and pinned-source contract tests, not live-site acceptance."""
import argparse
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location('dembrandt_local', ROOT / 'scripts/dembrandt-local.py')
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class LocalDembrandt(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.runtime = Path(self.temp.name)
        package = self.runtime / 'node_modules/dembrandt'
        package.mkdir(parents=True)
        (package / 'package.json').write_text(json.dumps({'version': '0.39.2'}))
        self.args = argparse.Namespace(url='https://owned.example', runtime=self.runtime,
            mobile=False, dark_mode=False, wcag=False, dtcg=False, design_md=False, compare=None)

    def test_ambient_cloud_and_cdp_removed(self):
        with patch.dict(os.environ, {'DEMBRANDT_KEY': 'test-placeholder', 'BROWSER_CDP_ENDPOINT': 'http://fixture.invalid'}):
            cmd, env = MODULE.command(self.args)
        self.assertNotIn('DEMBRANDT_KEY', env)
        self.assertNotIn('BROWSER_CDP_ENDPOINT', env)
        self.assertIn('--no-headed-fallback', cmd)
        self.assertNotIn('--key', cmd)

    def test_wrong_runtime_fails(self):
        (self.runtime / 'node_modules/dembrandt/package.json').write_text('{"version":"0.0.0"}')
        with self.assertRaisesRegex(ValueError, 'pinned'):
            MODULE.command(self.args)

    def test_cloud_baseline_id_rejected(self):
        self.args.compare = self.runtime / 'absent-cloud-id'
        with self.assertRaises(FileNotFoundError):
            MODULE.command(self.args)

    def test_embedded_credentials_rejected(self):
        self.args.url = 'https://user:placeholder@owned.example'
        with self.assertRaisesRegex(ValueError, 'without embedded credentials'):
            MODULE.command(self.args)

    def test_source_and_route(self):
        source = ROOT / 'upstreams/dembrandt'
        for path in ('LICENSE', 'package.json', 'docs/usage.md', 'docs/mcp.md'):
            self.assertTrue((source / path).is_file())
        self.assertIn('MIT License', (source / 'LICENSE').read_text())
        root = (ROOT / 'SKILL.md').read_text()
        bridge = (ROOT / 'references/dembrandt.md').read_text()
        self.assertIn('references/dembrandt.md', root)
        for needle in ('Hallmark', 'thresholded', 'stable/exit 0', 'semantic.primary', 'cloud-key flags', 'existing local file'):
            self.assertIn(needle, bridge)


if __name__ == '__main__':
    unittest.main()
