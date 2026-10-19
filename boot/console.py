"""Console UI for the live USB. Disk inventory is read-only."""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import recovery


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--self-test', action='store_true')
    args = parser.parse_args()
    catalog = recovery.load_catalog()
    if args.self_test:
        assert Path('/opt/ty-recovery/Recovery-Guide.html').is_file()
        compile(Path('/opt/ty-recovery/companion.py').read_text(), 'companion.py', 'exec')
        marker = 'TY_RECOVERY_BOOT_OK'
        print(marker, flush=True)
        try:
            fd = os.open('/dev/ttyS0', os.O_WRONLY | os.O_NONBLOCK)
            os.write(fd, (marker + '\n').encode())
            os.close(fd)
        except OSError:
            pass
        return
    while True:
        print('\n=== TY RECOVERY USB ===')
        print('Booted recovery environment. Internal disks are not automatically mounted.')
        print('This menu does not erase disks or install an operating system.')
        print('1. Show computer hardware\n2. List disks (read-only)\n3. Choose recovery instructions\n4. Set up networking\n5. Exit to live shell\n6. Connect to Elite Recovery website')
        try:
            choice = input('Choose: ').strip()
        except EOFError:
            return
        if choice == '1':
            report = recovery.detect()
            report['scope'] = 'Live USB OS, not the OS installed on internal storage.'
            report.pop('route', None)
            print(json.dumps(report, indent=2))
        elif choice == '2':
            subprocess.run(['lsblk', '-o', 'NAME,SIZE,TYPE,TRAN,MODEL,FSTYPE,LABEL,MOUNTPOINTS'], check=False)
            print('Labels and filesystem types are clues, not a verified installed-OS identification.')
        elif choice == '3':
            routes = catalog['routes']
            for index, route in enumerate(routes, 1):
                print(str(index) + '. ' + route.get('label', route['id']))
            try:
                index = int(input('Select the original system (0 cancels): ')) - 1
            except (ValueError, EOFError):
                continue
            if 0 <= index < len(routes):
                route = routes[index]
                print('\n' + route['instructions'])
                if route.get('url'):
                    print('Official support: ' + route['url'])
                print('This live image contains no Windows, macOS or ChromeOS installer.')
        elif choice == '4':
            subprocess.run(['nmtui'], check=False)
        elif choice == '6':
            print('Open Recovery Studio in your Elite account to create a pairing code.')
            subprocess.run([sys.executable, str(Path(__file__).resolve().parent / 'companion.py')], check=False)
        elif choice == '5':
            return


if __name__ == '__main__':
    main()
