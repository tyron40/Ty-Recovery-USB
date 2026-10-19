"""Read-only platform detection and recovery routing. Python 3.8+, stdlib only."""
import argparse
import hashlib
import json
import platform
import subprocess
import sys
import urllib.parse
import urllib.request
import webbrowser
from pathlib import Path

ROOT = Path(__file__).resolve().parent
ALLOWED_HOSTS = {'support.microsoft.com', 'learn.microsoft.com',
                 'support.apple.com', 'support.google.com', 'ubuntu.com'}


def read_text(path):
    try:
        return Path(path).read_text(errors='replace').strip()
    except OSError:
        return ''


def run(args):
    try:
        return subprocess.check_output(args, timeout=5, stderr=subprocess.DEVNULL,
                                       text=True).strip()
    except (OSError, subprocess.SubprocessError):
        return ''


def parse_release(text):
    # Never source os-release or lsb-release as executable shell input.
    result = {}
    for line in text.splitlines():
        key, sep, value = line.partition('=')
        if sep and not key.startswith('#'):
            result[key.strip()] = value.strip().strip('\"\'')
    return result


def detect(system=None, machine=None, reader=read_text, runner=run):
    system = platform.system() if system is None else system
    machine = platform.machine() if machine is None else machine
    result = {'system': system, 'architecture': machine, 'route': 'unknown',
              'scope': 'Running environment only; not an offline disk OS scan.'}
    if system == 'Darwin':
        arm = machine == 'arm64' or runner(['sysctl', '-n', 'hw.optional.arm64']) == '1'
        result.update(route='mac-apple-silicon' if arm else 'mac-intel',
                      model=runner(['sysctl', '-n', 'hw.model']))
    elif system == 'Linux':
        release = parse_release(reader('/etc/os-release'))
        lsb = parse_release(reader('/etc/lsb-release'))
        version = reader('/proc/version').lower()
        result.update(distribution=release.get('PRETTY_NAME', 'Unknown Linux'),
                      manufacturer=reader('/sys/class/dmi/id/sys_vendor'),
                      model=reader('/sys/class/dmi/id/product_name'))
        if 'microsoft' in version:
            result.update(route='unknown', note='WSL detected. Use the Windows launcher on the host.')
        elif lsb.get('CHROMEOS_RELEASE_NAME') or release.get('ID') in {'chromeos', 'chromiumos'}:
            result.update(route='chromeos', board=lsb.get('CHROMEOS_RELEASE_BOARD', 'unknown'))
        else:
            result['route'] = 'ubuntu' if release.get('ID') == 'ubuntu' else 'linux'
            result['note'] = 'Live USBs, containers and VMs describe their own OS, not the computer installation.'
    elif system == 'Windows':
        result.update(route='windows', note='Use Start-Recovery.cmd for Windows model detection.')
    return result


def valid_url(url):
    p = urllib.parse.urlsplit(url)
    return (p.scheme == 'https' and p.hostname in ALLOWED_HOSTS
            and not p.username and not p.password and p.port in (None, 443))


def validate_catalog(catalog):
    if catalog.get('schemaVersion') != 1 or not isinstance(catalog.get('routes'), list):
        raise ValueError('Unsupported catalog schema')
    seen = set()
    for route in catalog['routes']:
        if not isinstance(route, dict):
            raise ValueError('Invalid route')
        key = route.get('id')
        if not isinstance(key, str) or not key or key in seen:
            raise ValueError('Invalid or duplicate route ID')
        seen.add(key)
        if not isinstance(route.get('instructions'), str):
            raise ValueError('Missing recovery instructions')
        if route.get('url') is not None and not valid_url(route['url']):
            raise ValueError('Non-official destination in catalog')
    if 'unknown' not in seen:
        raise ValueError('Missing unknown-system fallback')
    return catalog


def load_catalog(url=None, digest=None):
    if url:
        p = urllib.parse.urlsplit(url)
        if p.scheme != 'https' or p.netloc != 'raw.githubusercontent.com' or not p.path.startswith('/tyron40/Ty-Recovery-USB/'):
            raise ValueError('Only this repository raw HTTPS catalog is allowed')
        if not digest or len(digest) != 64 or any(c not in '0123456789abcdefABCDEF' for c in digest):
            raise ValueError('A trusted SHA-256 digest is required for a cloud catalog')
        with urllib.request.urlopen(url, timeout=15) as response:
            if response.geturl() != url:
                raise ValueError('Catalog redirects are not accepted')
            raw = response.read(1024 * 1024 + 1)
        if len(raw) > 1024 * 1024:
            raise ValueError('Catalog too large')
        if hashlib.sha256(raw).hexdigest() != digest.lower():
            raise ValueError('Catalog SHA-256 mismatch')
    else:
        raw = (ROOT / 'catalog.json').read_bytes()
    return validate_catalog(json.loads(raw))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--detect-only', action='store_true')
    parser.add_argument('--catalog-url', help='Optional data-only GitHub catalog URL')
    parser.add_argument('--sha256', help='Trusted digest for that exact catalog')
    args = parser.parse_args()
    report = detect()
    print(json.dumps(report, indent=2))
    if args.detect_only:
        return 0
    catalog = load_catalog(args.catalog_url, args.sha256)
    route = next((r for r in catalog['routes'] if r['id'] == report['route']), None)
    if route is None:
        route = next(r for r in catalog['routes'] if r['id'] == 'unknown')
    print('\n' + route['instructions'])
    print('\nThis assistant does not erase disks or install operating systems.')
    if route.get('url'):
        print('Official instructions: ' + route['url'])
        if sys.stdin.isatty() and input('Open official instructions? [y/N] ').lower() == 'y':
            if not webbrowser.open(route['url']):
                print('No browser opened. Use the URL above on a working device.')
    return 0


if __name__ == '__main__':
    try:
        sys.exit(main())
    except (ValueError, OSError) as exc:
        print('Recovery stopped: ' + str(exc), file=sys.stderr)
        sys.exit(1)
