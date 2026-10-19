# Ty Recovery USB

Cross-platform recovery assistant by Tyron. **The repository includes a bootable PC ISO build pipeline and a portable assistant. It is not an unattended factory-reset product.**

## Bootable PC edition

The `Build bootable recovery USB` GitHub Actions workflow builds a Debian trixie amd64 hybrid ISO with legacy BIOS and x64 UEFI bootloaders, Python, networking tools, disk inventory and this toolkit. The boot menu starts the live system after five seconds; the text recovery menu opens on the first console after automatic live login. Internal disks are not automatically mounted. This edition boots independently of the OS on the computer; it does not run the installed Windows or replace Apple/ChromeOS recovery.

The workflow publishes `Ty-Recovery-USB-amd64.iso`, `SHA256SUMS` and the package inventory to a GitHub Release **only after both diskless QEMU BIOS and UEFI smoke tests pass**. A workflow file alone is not proof that an ISO has been built: check the run and release assets. The tests check that the live environment and bundled toolkit start, not actual hardware recovery or disk installation. Secure Boot and physical hardware compatibility are not certified.

To use a published ISO:

1. Download the `.iso` and `SHA256SUMS` from the same GitHub Release. On Windows, use `Get-FileHash .\Ty-Recovery-USB-amd64.iso -Algorithm SHA256` and compare the digest. A checksum detects corruption; trust also depends on the download source.
2. Use a reputable image writer such as Rufus or balenaEtcher to write the ISO onto a USB drive. **Writing the image erases the selected USB.** Select that drive carefully. Copying the ISO as an ordinary file onto a blank USB does not make it bootable.
3. Insert it into a compatible Intel/AMD 64-bit PC and select the USB in the manufacturer's boot menu. The firmware selection may require manual action.
4. Use the text menu to view hardware, list disks, read the appropriate recovery route or configure networking. It does not wipe or reinstall the computer.

This PC image is not for ARM Windows PCs, Apple silicon Macs or standard Chromebook recovery. Intel Mac boot compatibility depends on model and firmware and is untested. Older 32-bit systems are not supported. Macs and Chromebooks retain their official recovery paths in the guide.

For maintainers, the workflow builds on a disposable privileged Debian container, then uses QEMU on the GitHub runner. `boot/build.sh` requires root, Debian trixie amd64, live-build and the dependencies listed in the workflow. Use a disposable build machine. It does not target USB hardware: it writes an ISO file into `dist/`.

## Use this version

Extract the ZIP onto a USB drive. This folder is portable source code, not bootable media. Launch it manually on a working computer:

| System | Entry point | Implemented behavior |
| --- | --- | --- |
| Windows / Surface | `Start-Recovery.cmd` | Local Windows model detection and Recovery settings launcher |
| macOS Intel or Apple silicon | `sh Start-Recovery.sh` from this folder in Terminal | Python 3 detection, including Apple silicon under Rosetta; otherwise opens the manual guide |
| Linux | `sh Start-Recovery.sh` from this folder | Python 3 distro/hardware detection and recovery instructions; otherwise manual guide |
| Chromebook / ChromeOS | Open `Recovery-Guide.html` in Files | Manual recovery guide without developer mode or Python |
| Any working desktop browser | Open `Recovery-Guide.html` | Offline system selector; official external links require internet |

Macs do not necessarily include Python 3. The HTML guide requires no installation. The `.command` wrapper is included, but USB filesystems may not preserve executable permissions; the `sh` command is the dependable entry point. Windows script policy may require approved signing. No security settings are changed.

Detection identifies the **currently running environment**, not an OS on an offline disk. A Linux live USB will report that Linux environment, and Crostini reports its Linux container rather than the ChromeOS host. WSL is routed to an unsupported-environment notice and directs you to the Windows launcher. ChromeOS detection is available in Python only if run in a native environment exposing ChromeOS release files; use the manual guide on ordinary Chromebooks.

Nothing is erased, no reset is triggered and no software package is installed by these assistants. Hardware information stays local. Python detection only: `python3 recovery.py --detect-only`. Windows detection only: `powershell -NoProfile -File .\Recovery.ps1 -DetectOnly`.

## Optional GitHub catalog fetch

The Python assistant can retrieve a **data-only instruction catalog** from this repository using `--catalog-url URL --sha256 TRUSTED_DIGEST`. Use an immutable commit URL under `https://raw.githubusercontent.com/tyron40/Ty-Recovery-USB/` and obtain the digest through a trusted review of that exact file. Hash the file with `sha256sum catalog.json` on Linux or `shasum -a 256 catalog.json` on macOS.

Downloads have a timeout and 1 MiB limit. The digest must match, schema and official destination hosts are checked, and data is never evaluated as code. A checksum is not a signature; its authenticity depends on how you obtain it. The offline catalog is the default. This is not an image downloader, executable action service, automatic updater or full signed distribution system. It does not send the hardware report to GitHub.

## What is needed for the requested automated product

1. Build separate bootable Windows PE images for supported CPU architectures using Microsoft's ADK and WinPE add-on. A normal ZIP copied to USB is not bootable. Boot selection, firmware passwords, and external-boot policy require device-specific handling.
2. Inventory storage controllers, networking, firmware mode, internal disks and encryption in the booted environment. Explicitly identify the target disk by stable identity; never default to disk 0. Exclude the boot USB and refuse ambiguous disks.
3. Match a tested manufacturer/model/architecture profile. Stop on unknown models. F11 is not a universal boot or recovery key.
4. Fetch a small versioned catalog and the selected approved packages. Verify a signed catalog against an embedded public key, reject rollback, enforce download sizes and verify package hashes before any use. Never execute arbitrary commands from a mutable GitHub JSON file. Offline network/storage drivers must be available because downloads may not work initially.
5. Show the exact target disk and loss of files, require per-device erase approval, then run a validated Windows Setup answer file or the manufacturer's supported image deployment. Keep recovery logs and fail safely after interrupted downloads or power loss. Unattended setup can automate supported stages; licensing, hardware eligibility and account setup still apply.
6. Validate each supported profile on VMs and real hardware, including multiple disks, ARM, BitLocker, Secure Boot, failed downloads and missing drivers, before claiming support.

The bundled `catalog.json` establishes a data-only route format. **The Debian live ISO builder is implemented. Signed automatic updating, target OS package downloads/verification, Windows PE/media builders and installation automation remain unimplemented.** GitHub can host source and versioned release assets; it is not a remote agent server. Large OS images should come from official sources under their license, not be bundled indiscriminately into Git.

## Recovery media coverage

| Target | What must boot on a broken computer | Included here? |
| --- | --- | --- |
| Windows / Surface | Compatible WinPE or exact OEM recovery media with needed drivers | Separate from the Debian PC live image; Windows recovery media not bundled |
| Intel Mac | Compatible Apple Recovery or supported macOS installer | Official recovery media not bundled; instructions only |
| Apple silicon Mac | Apple Recovery; supported firmware recovery when needed | Official recovery media not bundled; instructions only |
| Chromebook | Exact model recovery image or supported internet recovery | Official recovery media not bundled; instructions only |
| Ubuntu / other Linux | Appropriate architecture and hardware-compatible distribution installer or OEM image | Official recovery media not bundled; instructions only |
| Unknown system | Manufacturer-supported recovery method | No; stops without choosing an image |

One USB can carry these assistant files, but creating ChromeOS or other raw recovery media may overwrite its entire contents. Use a separate recovery drive. A PC multiboot setup is a possible future addition; it does not make Apple silicon or every Chromebook compatible with generic PC boot media.

No universal all-model support is claimed. A clean Windows install does not necessarily restore OEM apps or original factory partitions. No bypass of activation locks, organization management, firmware passwords or encryption is provided.

## Official deployment references

- https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-create-usb-bootable-drive
- https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/automate-windows-setup
- https://support.apple.com/108900

## Validation status

Bootable build 4 (commit `8fc476cdb8d27da24859c2a609d55c1a6084b9a1`) completed successfully. Both diskless QEMU BIOS and UEFI boot checks reached the bundled toolkit. Download the ISO and checksums from [the tested release](https://github.com/tyron40/Ty-Recovery-USB/releases/tag/bootable-4). These are virtual boot checks, not certification of physical USB, Secure Boot or factory-reset compatibility.

Run `python3 -m unittest -v test_recovery.py` from this folder. Routing tests cover Intel Macs, native Apple silicon and Rosetta, ChromeOS release files, Ubuntu, other Linux, WSL, unknown platforms, destination restrictions, duplicate catalogs and mandatory cloud checksums. Shell syntax and detection-only execution were checked in a Linux environment. No hardware recovery, installation, Windows launch or macOS launch has been tested.
