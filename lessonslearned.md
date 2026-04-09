# stigman - Lessons Learned

During the architectural build and testing phases of `stigman` across Ubuntu 24.04 and Ubuntu 22.04, several critical environmental edge-cases were discovered regarding Canonical's packaging logic, `apt` limitations, and OpenSCAP's deployment models.

This document serves as a historical record of the problems encountered and how they were bypassed to ensure the AI agent could function autonomously.

---

### 1. The Shifting Name of SCAP Packages (Ubuntu 24.04)
**Problem:** The initial software design assumed the presence of an `ssg-ubuntu2404` apt package based on standard SCAP naming conventions.
**Discovery:** Ubuntu does not name its packages after the OS release. The unified meta-package was traditionally `scap-security-guide`.
**Evolution:** Further testing revealed that Canonical split the `scap-security-guide` package in modern Ubuntu 24.04 into two explicitly defined sub-packages: `ssg-base` and `ssg-debderived`.

### 2. Bleeding-Edge Repositories Missing Datastreams (Ubuntu 24.04)
**Problem:** Even after installing `ssg-debderived` on Ubuntu 24.04, the `oscap` scanner failed because `/usr/share/xml/scap/ssg/content/ssg-ubuntu2404-ds.xml` did not exist.
**Discovery:** Because Ubuntu 24.04 (Noble Numbat) was newly released, the stable snapshot of `ssg-debderived` sitting in the official `apt` repositories was not fully up-to-date with the upstream `ComplianceAsCode` project. The XML file was simply missing.
**Solution:** We rewrote `scan.py` to become self-healing. If the system `apt` package fails to provide the datastream XML, the python script natively connects to the official `ComplianceAsCode` GitHub repository, downloads the latest release ZIP, extracts the missing XML directly into `/tmp`, and passes it to the scanner.

### 3. Invisible `apt` Locks and Repositories (Ubuntu 22.04)
**Problem:** When forcing the AI agent to install missing prerequisites, the `subprocess` call to `apt install` would silently fail. 
**Discovery:** 
1. New Ubuntu VMs automatically run an `unattended-upgrades` daemon in the background immediately after booting, which locks `/var/lib/dpkg/lock-frontend` and prevents `apt install` from running.
2. The `universe` repository (which traditionally holds OpenSCAP tools) is heavily restricted or disabled on minimal cloud server images.
**Solution:** We updated `prereqs.py` to aggressively initialize the environment prior to installation by forcing `DEBIAN_FRONTEND=noninteractive`, automatically applying `sudo add-apt-repository universe -y`, and running `sudo apt update` to flush cache systems.

### 4. Canonical's Proprietary Shift (Ubuntu 22.04)
**Problem:** Even with the `universe` repo enabled, `apt install ssg-base` completely failed to resolve on Ubuntu 22.04.
**Discovery:** Canonical fundamentally shifted their business strategy starting with Ubuntu 22.04. They purposely stripped the open-source `scap-security-guide` compliance packages out of the `apt` repositories to push enterprise users into buying "Ubuntu Pro" subscriptions and using their proprietary `usg` (Ubuntu Security Guide) tool instead.
**Solution:** We relied entirely on our GitHub release extraction fallback. Because `apt` refuses to serve the SCAP datastreams without a paid subscription, `stigman` bypasses canonical licensing by fetching the datastreams manually from the open-source community.

### 5. Monolithic Legacy Tooling (Ubuntu 22.04)
**Problem:** In an attempt to install the OpenSCAP evaluation scanner, `apt install openscap-scanner openscap-utils` failed to locate packages.
**Discovery:** While modern Linux iterations (Fedora, RHEL, Ubuntu 24.04) have broken the suite down into cleanly separated modular packages (`openscap-scanner` and `openscap-utils`), Ubuntu 22.04 utilizes an older monolithic packaging schema.
**Solution:** On Ubuntu 22.04, the entire suite—including the actual `oscap` binary executable—is packed statically into a core library package named `libopenscap8`. By reducing the prerequisite check to simply `libopenscap8`, `apt` was finally able to provide the `oscap` terminal command without failure.
