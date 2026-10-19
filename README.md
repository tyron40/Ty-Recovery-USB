# Ty Recovery USB

Cross-platform recovery assistant by Tyron. **This is source code, not a bootable USB image or an unattended factory-reset product.**

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

The bundled `catalog.json` establishes a data-only route format. **Signed automatic updating, OS package downloads/verification, bootable-media builders and installation automation are not implemented in this version.** GitHub can host source and versioned release assets; it is not a remote agent server. Large OS images should come from official sources under their license, not be bundled indiscriminately into Git.

## Recovery media coverage

| Target | What must boot on a broken computer | Included here? |
| --- | --- | --- |
| Windows / Surface | Compatible WinPE or exact OEM recovery media with needed drivers | No; running-system assistant only |
| Intel Mac | Compatible Apple Recovery or supported macOS installer | No; instructions only |
| Apple silicon Mac | Apple Recovery; supported firmware recovery when needed | No; instructions only |
| Chromebook | Exact model recovery image or supported internet recovery | No; instructions only |
| Ubuntu / other Linux | Appropriate architecture and hardware-compatible distribution installer or OEM image | No; instructions only |
| Unknown system | Manufacturer-supported recovery method | No; stops without choosing an image |

One USB can carry these assistant files, but creating ChromeOS or other raw recovery media may overwrite its entire contents. Use a separate recovery drive. A PC multiboot setup is a possible future addition; it does not make Apple silicon or every Chromebook compatible with generic PC boot media.

No universal all-model support is claimed. A clean Windows install does not necessarily restore OEM apps or original factory partitions. No bypass of activation locks, organization management, firmware passwords or encryption is provided.

## Official deployment references

- https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-create-usb-bootable-drive
- https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/automate-windows-setup
- https://support.apple.com/108900

## Validation status

Run `python3 -m unittest -v test_recovery.py` from this folder. Routing tests cover Intel Macs, native Apple silicon and Rosetta, ChromeOS release files, Ubuntu, other Linux, WSL, unknown platforms, destination restrictions, duplicate catalogs and mandatory cloud checksums. Shell syntax and detection-only execution were checked in a Linux environment. No hardware recovery, installation, Windows launch or macOS launch has been tested.
