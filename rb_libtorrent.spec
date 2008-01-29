Name:		rb_libtorrent
Version:	0.12
Release:	3%{?dist}
Summary:	A C++ BitTorrent library aiming to be the best alternative

Group:		System Environment/Libraries
License:	BSD
URL:		http://www.rasterbar.com/products/libtorrent/

Source0:	http://www.libtorrent.org/libtorrent-%{version}.tar.gz
Source1:	%{name}-README-renames.Fedora
Source2:	%{name}-COPYING.Boost
Source3:	%{name}-COPYING.zlib

Patch0: 	%{name}-svn1968-bdecode_recursive-security-fix.patch

BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:	boost-devel
BuildRequires:	zlib-devel
BuildRequires:	libtool
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
License:	BSD and zlib/libpng License and Boost Software License
Requires:	%{name} = %{version}-%{release}
Requires:	pkgconfig
## Same pkgconfig file, and unsuffixed shared library symlink. :(
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


%package	examples
Summary:	Example clients using %{name}
Group:		Applications/Internet
License:	BSD
Requires:	%{name} = %{version}-%{release}

%description	examples
The %{name}-examples package contains example clients which intend to
show how to make use of its various features. (Due to potential
namespace conflicts, a couple of the examples had to be renamed. See the
included documentation for more details.)


%prep
%setup -q -n "libtorrent-%{version}"
## Some of the sources and docs are executable, which makes rpmlint against
## the resulting -debuginfo and -devel packages, respectively, quite angry. :]
find src/ docs/ -type f -exec chmod a-x '{}' \;
find . -type f -regex '.*\.[hc]pp' -exec chmod a-x '{}' \;
## The RST files are the sources used to create the final HTML files; and are
## not needed.
rm -f docs/*.rst
## Ensure that we get the licenses installed appropriately.
install -p -m 0644 COPYING COPYING.BSD
install -p -m 0644 %{SOURCE2} COPYING.Boost
install -p -m 0644 %{SOURCE3} COPYING.zlib
## Fix the installed pkgconfig file: we don't need linkage that the
## libtorrent DSO already ensures. 
sed -i -e 's/^Libs:.*$/Libs: -L${libdir} -ltorrent/' libtorrent.pc.in 
## SECURITY: Fix potential stack overflow in bencode_recursive with
## malformed messages. 
%patch0 -p3 -b .bdecode_recursive-security-fix 


%build
%configure --disable-static --enable-examples --with-zlib=system	\
	--with-boost-date-time=boost_date_time-mt 			\
	--with-boost-filesystem=boost_filesystem-mt			\
	--with-boost-thread=boost_thread-mt				\
	--with-boost-regex=boost_regex-mt				\
	--with-boost-program_options=boost_program_options-mt
## Use the system libtool to ensure that we don't get unnecessary RPATH
## hacks in our final build.
make %{?_smp_mflags} LIBTOOL=%{_bindir}/libtool


%check
make check


%install
rm -rf %{buildroot}
## Ensure that we preserve our timestamps properly.
export CPPROG="%{__cp} -p"
make install DESTDIR=%{buildroot} INSTALL="%{__install} -c -p"
## Do the renaming due to the somewhat limited %%_bindir namespace. 
rename client torrent_client %{buildroot}%{_bindir}/*
install -p -m 0644 %{SOURCE1} ./README-renames.Fedora 


%clean
rm -rf %{buildroot}


%post -p /sbin/ldconfig


%postun -p /sbin/ldconfig


%files
%defattr(-,root,root,-)
%doc AUTHORS ChangeLog COPYING README
%{_libdir}/libtorrent.so.*
%exclude %{_libdir}/*.la
## Unfortunately (even with the "--disable-static" option to the %%configure
## invocation) our use of the system libtool creates static libraries at build
## time, so we must exclude them here.
%exclude %{_libdir}/*.a


%files devel
%defattr(-,root,root,-)
%doc COPYING.Boost COPYING.BSD COPYING.zlib docs/ 
%{_libdir}/pkgconfig/libtorrent.pc
%{_includedir}/libtorrent/
%{_libdir}/libtorrent.so

%files examples
%doc COPYING README-renames.Fedora
%{_bindir}/*torrent*


%changelog
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
