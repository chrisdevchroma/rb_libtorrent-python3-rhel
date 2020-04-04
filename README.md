# rb_libtorrent-rhel
Forked from https://src.fedoraproject.org/rpms/rb_libtorrent.git to build for RHEL/CentOS 8

## How to build
See https://github.com/chrisdevchroma/build-packages-docker/blob/master/rb_libtorrent.sh for a automated script.

### Manual build
1. Install the Development tools (includes rpm-build)
```bash
sudo dnf group install "Development Tools"
```
2. Install rpmdevtools (for spectool)
```bash
sudo dnf install rpmdevtools
```
3. Install rb_libtorrent build dependencies
```bash
sudo dnf install boost-devel boost-python3-devel chrpath python3-devel
```
4. Build & install dependency asio-devel -> see https://github.com/chrisdevchroma/asio-rhel
5. Clone repo with git and cd into the folder
```bash
cd rb_libtorrent-rhel
```
6. Create build/SOURCES dir
```bash
mkdir -p build/SOURCES
```
7. Download rb_libtorrent source tarball with spectool
```bash
spectool -g -C build/SOURCES rb_libtorrent.spec
```
8. Copy patches into build/SOURCES
```bash
cp *.patch *COPYING* *README*.Fedora build/SOURCES
```
9. Build package with rpmbuild
```bash
rpmbuild --define "_topdir `pwd`/build" -ba rb_libtorrent.spec
```
10. Install rb_libtorrent and rb_libtorrent-python3 packages
```bash
sudo dnf install ./build/RPMS/x86_64/rb_libtorrent-[[:digit:]]*.el8.x86_64.rpm
sudo dnf install ./build/RPMS/x86_64/rb_libtorrent-python3-[[:digit:]]*.el8.x86_64.rpm
```
