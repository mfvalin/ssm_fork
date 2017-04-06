#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm/repository.py

# GPL--start
# This file is part of ssm (Simple Software Manager)
# Copyright (C) 2005-2012 Environment/Environnement Canada
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; version 2
# of the License.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
# GPL--end

"""Provides the Repository class.
"""

# system imports
import os.path
import re
import traceback
import urllib
import urlparse

#
from ssm import ext_tarfile as tarfile
from ssm import utils

class Repository:
    """Accessor for SSM repository (file, ftp, http).
    """

    def __init__(self, source):
        self.source = source
        t = source.split(None, 1)
        self.url = t[0].strip()
        if len(t) > 1:
            self.components = t[1].strip().split()
        else:
            self.components = [""]
        self.loaded_urls = None

    def get(self, package_name):
        """Download package and return TarFile object.
        """
        tarf = None
        url = self.find(package_name)
        if url:
            try:
                path, headers = urllib.urlretrieve(url)
                tarf = tarfile.open(path)
                tarf.errorlevel = 1 # exception on fatal errors
                if url.startswith("http://") or url.startswith("ftp://"):
                    # delete temp file
                    utils.remove(path)
            except:
                #traceback.print_exc()
                tarf = None
        return tarf

    def list(self):
        self.load_urls()
        return self.loaded_urls

    def find(self, package_name):
        self.load_urls()
        filename = package_name+".ssm"
        for url in self.loaded_urls:
            if filename == os.path.basename(url):
                return url
        return None

    def _load_ftp_urls(self, base_url):
        utils.print_verbose("loading urls over ftp (%s)" % (base_url,))
        pass

    def _load_http_urls(self, base_url):
        """Load urls from web site (links from apache directory
        listing).
        """
        utils.print_verbose("loading urls over http (%s)" % (base_url,))
        urls = []
        try:
            #ahref_cre = re.compile("""<a (?:.*)href="([^"]*)">""")
            ahref_cre = re.compile("""<a href="([^"]*)">""")
            f = urllib.urlopen(base_url)
            for url in ahref_cre.findall(f.read()):
                if url.endswith(".ssm"):
                    urls.append(os.path.join(base_url, url))
        except:
            traceback.print_exc()
            pass
        return urls

    def _load_file_urls(self, base_url):
        """Load urls from filesystem.
        """
        utils.print_verbose("loading urls from filesystem (%s)" % (base_url,))
        try:
            root, _, filenames = os.walk(base_url).next()
            urls = [os.path.join(root, filename) for filename in filenames]
        except:
            #traceback.print_exc()
            urls = []
        return urls

    def load_urls(self):
        """Load urls for repository url and components.
        """
        if self.loaded_urls != None:
            return

        if self.url.startswith("http://"):
            _load_urls = self._load_http_urls
        elif self.url.startswith("ftp://"):
            _load_urls = self._load_ftp_urls
        else:
            _load_urls = self._load_file_urls

        urls = []
        for comp in self.components:
            urls.extend(_load_urls(os.path.join(self.url, comp)))
        self.loaded_urls = urls
