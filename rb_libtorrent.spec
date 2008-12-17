%{!?python_sitelib: %global python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}
%{!?python_sitearch: %global python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

Name:		rb_libtorrent
Version:	0.13.1
Release:	6%{?dist}
Summary:	A C++ BitTorrent library aiming to be the best alternative

Group:		System Environment/Libraries
License:	BSD
URL:		http://www.rasterbar.com/products/libtorrent/

## TODO: Source0 Should use SourceForge's file-mirroring URL upon update to
## version 0.14+.
Source0:	http://mirror.thecodergeek.com/src/libtorrent-rasterbar-0.13.1.tar.gz
Source1:	%{name}-README-renames.Fedora
Source2:	%{name}-COPYING.Boost
Source3:	%{name}-COPYING.zlib
## Sent upstream via the libtorrent-discuss ML.
## Message-Id: <1216701448.24546.11.camel@tuxhugs>
Source4: 	%{name}-python-setup.py

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	asio-devel
BuildRequires:	boost-devel
BuildRequires:	libtool
BuildRequires:	python-devel
BuildRequires:	python-setuptools
BuildRequires:	zlib-devel
## Necessary for 'rename'...
BuildRequires:	util-linux-ng

## The following is taken from it's website listing...mostly.
%description
%{name} is a C++ library that aims to be a good alternative to all
the other BitTorrent implementations around. It is a library and not a full
featured client, although it comes with a few working example clients.

Its main goals are to be very efficient (in terms of CPU and memory usage) as
well as being very easy to use both as a user and developer. 


%package 	devel
Summary:	Development files for %{name}
Group:		Development/Libraries
License:	BSD and zlib and Boost
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig
## Same include directory. :(
Conflicts:	libtorrent-devel
## Needed for various headers used via #include directives...
Requires:	boost-devel
Requires:	openssl-devel

%description	devel
The %{name}-devel package contains libraries and header files for
developing applications that use %{name}.

The various source and header files included in this package are licensed
under the revised BSD, zlib/libpng, and Boost Public licenses. See the various
COPYING files in the included documentation for the full text of these
licenses, as well as the comments blocks in the source code for which license
a given source or header file is released under.


#package	examples
#Summary:	Example clients using %{name}
#Group:		Applications/Internet
#License:	BSD
#Requires:	%{name} = %{version}-%{release}

#description	examples
#The %{name}-examples package contains example clients which intend to
#show how to make use of its various features. (Due to potential
#namespace conflicts, a couple of the examples had to be renamed. See the
#included documentation for more details.)


%package	python
Summary:	Python bindings for %{name}
Group:		Development/Languages
License:	Boost
Requires:	%{name} = %{version}-%{release}

%description	python
The %{name}-python package contains Python language bindings (the 'libtorrent'
module) that allow it to be used from within Python applications.


%prep
%setup -q -n "libtorrent-rasterbar-%{version}"
## The RST files are the sources used to create the final HTML files; and are
## not needed.
rm -f docs/*.rst
## Ensure that we get the licenses installed appropriately.
install -p -m 0644 COPYING COPYING.BSD
install -p -m 0644 %{SOURCE2} COPYING.Boost
install -p -m 0644 %{SOURCE3} COPYING.zlib
## Finally, ensure that everything is UTF-8, as it should be.
iconv -t UTF-8 -f ISO_8859-15 AUTHORS -o AUTHORS.iconv
mv AUTHORS.iconv AUTHORS
## Install the necessary build script for the python bindings module...
install -p -m 0755 %{SOURCE4} bindings/python/setup.py


%build
## XXX: Even with the --with-asio=system configure option, the stuff in
## the local include directory overrides that of the system. We don't like
## local copies of system code. :)
rm -rf include/libtorrent/asio*
## FIXME: The examples currently fail to build (missing Makefile.in)
%configure --disable-static --with-zlib=system		\
	--with-boost-date-time=mt 			\
	--with-boost-thread=mt				\
	--with-boost-regex=mt				\
	--with-boost-program_options=mt			\
	--with-boost-filesystem=mt			\
	--with-asio=system
## Use the system libtool to ensure that we don't get unnecessary RPATH
## hacks in our final build.
make %{?_smp_mflags} LIBTOOL=%{_bindir}/libtool
## Finally, build the python module.
pushd bindings/python
	CFLAGS="%{optflags}" %{__python} setup.py build
	## Fix the interpreter for the example clients
	sed -i -e 's:^#!/bin/python$:#!/usr/bin/python:' {simple_,}client.py 
popd


%check
make check


%install
rm -rf %{buildroot}
## Ensure that we preserve our timestamps properly.
export CPPROG="%{__cp} -p"
make install DESTDIR=%{buildroot} INSTALL="%{__install} -c -p"
## Do the renaming due to the somewhat limited %%_bindir namespace. 
#rename client torrent_client %{buildroot}%{_bindir}/*
#install -p -m 0644 %{SOURCE1} ./README-renames.Fedora
## Install the python binding module.
pushd bindings/python
	%{__python} setup.py install -O1 --skip-build --root %{buildroot}
popd 


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig


%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README
%exclude %{_libdir}/*.la
%{_libdir}/libtorrent-rasterbar.so.*
## Unfortunately (even with the "--disable-static" option to the %%configure
## invocation) our use of the system libtool creates static libraries at build
## time, so we must exclude them here.
%exclude %{_libdir}/*.a

%files	devel
%defattr(-,root,root,-)
%doc COPYING.Boost COPYING.BSD COPYING.zlib docs/ 
%{_libdir}/pkgconfig/libtorrent-rasterbar.pc
%{_includedir}/libtorrent/
%{_libdir}/libtorrent-rasterbar.so

## Build failures...
#files examples
#doc COPYING README-renames.Fedora
#{_bindir}/*torrent*

%files	python
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING.Boost bindings/python/{simple_,}client.py
%{python_sitearch}/libtorrent-%{version}-py?.?.egg-info
%{python_sitearch}/libtorrent.so


%changelog
* Wed Dec 17 2008 Benjamin Kosnik  <bkoz@redhat.com> - 0.13.1-6
- Rebuild for boost-1.37.0.

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.13.1-5
- Fix locations for Python 2.6

* Sat Nov 29 2008 Ignacio Vazquez-Abrams <ivazqueznet+rpm@gmail.com> - 0.13.1-4
- Rebuild for Python 2.6

* Thu Nov 20 2008 Peter Gordon <peter@thecodergeek.com>
- Update Source0 URL, for now.

* Wed Sep  3 2008 Tom "spot" Callaway <tcallawa@redhat.com> - 0.13.1-3
- fix license tag

* Mon Jul 14 2008 Peter Gordon <peter@thecodergeek.com> - 0.13.1-2
- Add python bindings in a -python subpackage. 

* Mon Jul 14 2008 Peter Gordon <peter@thecodergeek.com> - 0.13.1-1
- Update to new upstream release (0.13.1): Contains an incompatible ABI/API
  bump.
- Drop GCC 4.3 patch (fixed upstream):
  - gcc43.patch
- Disable building the examples for now. (Attempted builds fail due to missing
  Makefile support.) 
- Drop the source permissions and pkgconfig file tweaks (fixed upstream).

* Sat Feb 09 2008 Peter Gordon <peter@thecodergeek.com> - 0.12.1-1
- Update to new upstream bug-fix release (0.12.1)
- Rebuild for GCC 4.3
- Drop security fix patch (merged upstream):
  - svn1968-bdecode_recursive-security-fix.patch
- Add GCC 4.3 build fixes (based on patch from Adel Gadllah, bug 432778):
  + gcc43.patch

* Mon Jan 28 2008 Peter Gordon <peter@thecodergeek.com> - 0.12-3
- Add upstream patch (changeset 1968) to fix potential security vulnerability:
  malformed messages passed through the bdecode_recursive routine could cause
  a potential stack overflow.
  + svn1968-bdecode_recursive-security-fix.patch

* Fri Aug 03 2007 Peter Gordon <peter@thecodergeek.com> - 0.12-2
- Rebuild against new Boost libraries.

* Thu Jun 07 2007 Peter Gordon <peter@thecodergeek.com> - 0.12-1
- Update to new upstream release (0.12 Final)
- Split examples into a subpackage. Applications that use rb_libtorrent
  don't need the example binaries installed; and splitting the package in this
  manner is a bit more friendly to multilib environments.  

* Sun Mar 11 2007 Peter Gordon <peter@thecodergeek.com> - 0.12-0.rc1
- Update to new upstream release (0.12 RC).
- Forcibly use the system libtool to ensure that we remove any RPATH hacks.

* Sun Jan 28 2007 Peter Gordon <peter@thecodergeek.com> - 0.11-5
- Fix installed pkgconfig file: Strip everything from Libs except for
  '-ltorrent', as its [libtorrent's] DSO will ensure proper linking to other
  needed libraries such as zlib and boost_thread. (Thanks to Michael Schwendt
  and Mamoru Tasaka; bug #221372)

* Sat Jan 27 2007 Peter Gordon <peter@thecodergeek.com> - 0.11-4
- Clarify potential licensing issues in the -devel subpackage:
  + COPYING.zlib
  + COPYING.Boost
- Add my name in the Fedora-specific documentation (README-renames.Fedora) and
  fix some spacing issues in it.
- Strip the @ZLIB@ (and thus, the extra '-lz' link option) from the installed
  pkgconfig file, as that is only useful when building a statically-linked
  libtorrent binary. 
- Fix conflict: The -devel subpackage should conflict with the -devel
  subpackage of libtorrent, not the main package.
- Preserve timestamps in %%install.

* Wed Jan 17 2007 Peter Gordon <peter@thecodergeek.com> - 0.11-3
- Fix License (GPL -> BSD)
- Don't package RST (docs sources) files.
- Only make the -devel subpackage conflict with libtorrent-devel.
- Rename some of the examples more appropriately; and add the
  README-renames.Fedora file to %%doc which explains this.

* Fri Jan 05 2007 Peter Gordon <peter@thecodergeek.com> - 0.11-2
- Add Requires: pkgconfig to the -devel subpackage since it installs a .pc
  file. 

* Wed Jan 03 2007 Peter Gordon <peter@thecodergeek.com> - 0.11-1
- Initial packaging for Fedora Extras 
