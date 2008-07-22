# setup.py - Builds the python rb_libtorrent bindings 
#
# Copyright (C) 2008 Peter Gordon ('codergeek42') <peter@thecodergeek.com>
# Based heavily on the Deluge setuptools script, which is
#   Copyright (C) 2007 Andrew Resch ('andar') <andrewresch@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.    If not, write to:
# 	The Free Software Foundation, Inc.,
# 	51 Franklin Street, Fifth Floor
# 	Boston, MA    02110-1301, USA.
#
# In addition, as a special exception, the copyright holders give
# permission to link the code of portions of this program with the OpenSSL
# library.
# You must obey the GNU General Public License in all respects for all of
# the code used other than OpenSSL. If you modify file(s) with this
# exception, you may extend this exception to your version of the file(s),
# but you are not obligated to do so. If you do not wish to do so, delete
# this exception statement from your version. If you delete this exception
# statement from all source files in the program, then also delete it here.

import glob

from setuptools import setup, find_packages, Extension
from distutils import cmd, sysconfig
from distutils.command.build import build as _build
from distutils.command.install import install as _install
from distutils.command.install_data import install_data as _install_data

import os
import platform

python_version = platform.python_version()[0:3]

if not os.environ.has_key("CC"):
	os.environ["CC"] = "gcc"

if not os.environ.has_key("CXX"):
	os.environ["CXX"] = "gcc"

if not os.environ.has_key("CPP"):
	os.environ["CPP"] = "g++"

# The libtorrent extension
_libtorrent_compile_args = [
	"-D_FILE_OFFSET_BITS=64",
	"-DNDEBUG",
	"-DTORRENT_USE_OPENSSL=1",
	"-O2",
	"-Wno-missing-braces"
	]

cv_opt = sysconfig.get_config_vars()["CFLAGS"]

_library_dirs = [
	'../../src/.libs'
]

_include_dirs = [
	'../../include/',
	'../../include/libtorrent',
	'/usr/include/python' + python_version
	]

_libraries = [
        'torrent-rasterbar',
        'boost_python-mt'
        ]

_sources = glob.glob("src/*.cpp")

## Remove some files from the source that aren't needed
_source_removals = ["mapped_storage.cpp"]

for source in _sources:
	for rem in _source_removals:
		if rem in source:
			_sources.remove(source)
			break

libtorrent = Extension(
	'libtorrent',
	extra_compile_args = _libtorrent_compile_args,
	include_dirs = _include_dirs,
	libraries = _libraries,
	library_dirs = _library_dirs,
	sources = _sources
)

class build(_build):
    def run(self):
        _build.run(self)

class install_data(_install_data):
    def run(self):
        _install_data.run(self)

cmdclass = {
    'build': build,
    'install_data': install_data
}

setup(
    author = "Arvid Norberg",
    author_email = "",
    cmdclass=cmdclass,
    description = "Python rb_libtorrent Bindings",
    ext_modules = [libtorrent],
    fullname = "Python rb_libtorrent Bindings",
    include_package_data = False,
    license = "Boost",
    name = "libtorrent",
    url = "http://www.rasterbar.com/products/libtorrent/",
    version = "0.13.1",
)
