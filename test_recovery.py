import unittest
from unittest.mock import patch
import recovery


class RoutingTests(unittest.TestCase):
    def detect(self, system, machine='x86_64', files=None, outputs=None):
        return recovery.detect(system, machine, lambda p: (files or {}).get(p, ''),
                               lambda a: (outputs or {}).get(tuple(a), ''))

    def test_apple_silicon(self):
        self.assertEqual(self.detect('Darwin', 'arm64')['route'], 'mac-apple-silicon')

    def test_rosetta(self):
        report = self.detect('Darwin', outputs={('sysctl','-n','hw.optional.arm64'): '1'})
        self.assertEqual(report['route'], 'mac-apple-silicon')

    def test_intel_mac(self):
        self.assertEqual(self.detect('Darwin')['route'], 'mac-intel')

    def test_chromeos(self):
        self.assertEqual(self.detect('Linux', files={'/etc/lsb-release': 'CHROMEOS_RELEASE_NAME=Chrome OS\nCHROMEOS_RELEASE_BOARD=example'})['route'], 'chromeos')

    def test_ubuntu(self):
        self.assertEqual(self.detect('Linux', files={'/etc/os-release': 'ID=ubuntu'})['route'], 'ubuntu')

    def test_other_linux(self):
        self.assertEqual(self.detect('Linux', files={'/etc/os-release': 'ID=fedora'})['route'], 'linux')

    def test_wsl_is_not_bare_metal(self):
        self.assertEqual(self.detect('Linux', files={'/proc/version': 'Microsoft WSL2'})['route'], 'unknown')

    def test_unknown(self):
        self.assertEqual(self.detect('FreeBSD')['route'], 'unknown')

    def test_urls(self):
        for url in ['http://support.apple.com/', 'https://support.apple.com.evil.example/', 'https://user@support.apple.com/', 'file:///etc/passwd']:
            self.assertFalse(recovery.valid_url(url))

    def test_duplicate_rejected(self):
        with self.assertRaises(ValueError):
            recovery.validate_catalog({'schemaVersion': 1, 'routes': [{'id':'unknown','instructions':''}]*2})

    def test_cloud_requires_pin_before_network(self):
        with patch('urllib.request.urlopen') as network:
            with self.assertRaises(ValueError):
                recovery.load_catalog('https://raw.githubusercontent.com/tyron40/Ty-Recovery-USB/main/catalog.json')
            network.assert_not_called()

    def test_catalog_covers_routes(self):
        routes = {r['id'] for r in recovery.load_catalog()['routes']}
        self.assertTrue({'windows','surface','mac-intel','mac-apple-silicon','chromeos','ubuntu','linux','unknown'} <= routes)


if __name__ == '__main__':
    unittest.main()
