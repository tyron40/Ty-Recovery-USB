"""Boot ISO in diskless QEMU using BIOS and UEFI; require a live-system marker."""
import argparse
from pathlib import Path
import subprocess
import time

parser = argparse.ArgumentParser()
parser.add_argument('iso')
args = parser.parse_args()
iso = Path(args.iso).resolve()
if not iso.is_file():
    raise SystemExit('Missing ISO')
for mode in ('bios', 'uefi'):
    log = Path(f'boot-{mode}.log')
    cmd = ['qemu-system-x86_64', '-machine', 'q35', '-m', '2048', '-accel', 'tcg',
           '-cdrom', str(iso), '-boot', 'd', '-display', 'none', '-monitor', 'none',
           '-serial', 'file:' + str(log), '-no-reboot', '-nic', 'none']
    if mode == 'uefi':
        firmware = Path('/usr/share/OVMF/OVMF_CODE_4M.fd')
        if not firmware.is_file():
            raise SystemExit('Missing OVMF UEFI firmware')
        cmd += ['-drive', 'if=pflash,format=raw,readonly=on,file=' + str(firmware)]
    with log.open('w'):
        pass
    process = subprocess.Popen(cmd)
    try:
        deadline = time.monotonic() + 300
        while time.monotonic() < deadline:
            if 'TY_RECOVERY_BOOT_OK' in log.read_text(errors='replace'):
                print(mode + ': live toolkit started successfully', flush=True)
                break
            if process.poll() is not None:
                raise RuntimeError(mode + ': QEMU exited before boot completed')
            time.sleep(1)
        else:
            raise RuntimeError(mode + ': boot marker not found within 300 seconds')
    finally:
        process.terminate()
        try:
            process.wait(timeout=10)
        except subprocess.TimeoutExpired:
            process.kill()
            process.wait()
