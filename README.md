# Ty Recovery USB

Initial Windows recovery assistant by Tyron. **This is source code, not a bootable USB image or an unattended factory-reset product.**

## Use the first version

Download the repository ZIP from GitHub's Code menu, extract it onto a USB drive, connect it to a Windows PC, and run `Start-Recovery.cmd`. You must start it yourself. Windows policy may block scripts; use your organization's approved signing/deployment process rather than disabling protections.

It detects manufacturer, model, running Windows version and architecture locally, selects Windows or Surface guidance, and offers to open Recovery settings or official support. `powershell -NoProfile -File .\Recovery.ps1 -DetectOnly` performs detection only. It sends no hardware information to GitHub and stores no serial numbers. It does not erase disks, press boot keys, fetch software, or install Windows.

## What is needed for the requested automated product

1. Build separate bootable Windows PE images for supported CPU architectures using Microsoft's ADK and WinPE add-on. A normal ZIP copied to USB is not bootable. Boot selection, firmware passwords, and external-boot policy require device-specific handling.
2. Inventory storage controllers, networking, firmware mode, internal disks and encryption in the booted environment. Explicitly identify the target disk by stable identity; never default to disk 0. Exclude the boot USB and refuse ambiguous disks.
3. Match a tested manufacturer/model/architecture profile. Stop on unknown models. F11 is not a universal boot or recovery key.
4. Fetch a small versioned catalog and the selected approved packages. Verify a signed catalog against an embedded public key, reject rollback, enforce download sizes and verify package hashes before any use. Never execute arbitrary commands from a mutable GitHub JSON file. Offline network/storage drivers must be available because downloads may not work initially.
5. Show the exact target disk and loss of files, require per-device erase approval, then run a validated Windows Setup answer file or the manufacturer's supported image deployment. Keep recovery logs and fail safely after interrupted downloads or power loss. Unattended setup can automate supported stages; licensing, hardware eligibility and account setup still apply.
6. Validate each supported profile on VMs and real hardware, including multiple disks, ARM, BitLocker, Secure Boot, failed downloads and missing drivers, before claiming support.

The bundled `catalog.json` establishes a data-only route format. **Cloud updating, signed package verification, a WinPE builder and installation automation are not implemented in this version.** GitHub can host source and versioned release assets; it is not a remote agent server. Large OS images should come from official sources under their license, not be bundled indiscriminately into Git.

## Platform coverage

| Platform | Current implementation | Future route |
| --- | --- | --- |
| Running Windows | Local detection and recovery settings launcher | Tested WinPE installation profiles |
| Surface running Windows | Family routing; no exact image selection | Exact model/serial recovery image and drivers |
| Unbootable Windows | Not supported | Bootable WinPE media |
| Mac | Not supported | Apple-supported Recovery workflow; some firmware restores need another Mac |
| Chromebook | Not supported | Exact board/model ChromeOS recovery media |
| Linux / other systems | Not supported | Distribution-specific supported installers |

No universal all-model support is claimed. A clean Windows install does not necessarily restore OEM apps or original factory partitions. No bypass of activation locks, organization management, firmware passwords or encryption is provided.

## Official deployment references

- https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/winpe-create-usb-bootable-drive
- https://learn.microsoft.com/en-us/windows-hardware/manufacture/desktop/automate-windows-setup
- https://support.apple.com/108900

## Validation status

Catalog JSON and route shape checked during creation. Windows scripts require a real Windows test; they have not been run on a Windows PC. No reset has been attempted.
