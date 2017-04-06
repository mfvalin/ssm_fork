#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm/package.py

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

"""Provides the Package class.
"""

# system imports
import os
import os.path
import re
import subprocess
import sys
import traceback

#
from ssm import globls
from ssm import utils

def special_links_walk(root):
    """Alternate to os.walk() which provide special support for
    handling symlinks with linknames starting with "./" and ending
    with "/." .
    """
    if not os.path.isdir(root):
        raise StopIteration()

    dirnames = []
    filenames = []
    for name in os.listdir(root):
        path = os.path.join(root, name)
        if os.path.islink(path):
            linkname = os.readlink(path)
            if os.path.isdir(path) and linkname[:2]+linkname[-2:] == ".//.":
                # treat as dir if restrictions met:
                # 1) has .//. signature
                # 2) has same parents or lower than path (tricky)
                dirnames.append(name)
            else:
                filenames.append(name)
        elif os.path.isdir(path):
            dirnames.append(name)
        elif os.path.isfile(path) or os.path.islink(path):
            filenames.append(name)
    yield root, dirnames, filenames

    for name in dirnames:
        path = os.path.join(root, name)
        for root2, dirnames2, filenames2 in special_links_walk(path):
            yield root2, dirnames2, filenames2

class Package:
    """Manager for a package (existent or not, although the domain
    must exist).
    """

    def __init__(self, domain, name):
        self.domain = domain
        self.name = name
        self.path = os.path.realpath(os.path.join(domain.path, name))
        self.short_name, self.version, self.platform = self.name.split("_", 2)
        self.exclude_path = os.path.join(self.path, ".ssm.d/exclude")
        self.include_path = os.path.join(self.path, ".ssm.d/include")

    # state
    def exists(self):
        return os.path.isdir(self.path)

    def get_control(self):
        m = None
        if self.exists():
            m = utils.read_control_map(self.path+"/.ssm.d/control")
        return m

    def get_exclude_cre(self):
        # default to exclude none
        return re.compile(utils.loads(self.include_path) or "(?!.*)")
        
    def get_include_cre(self):
        # default to include all
        return re.compile(utils.loads(self.include_path) or ".*")

    def get_publishable_paths(self, names, excluded_names=None):
        """Return a list of paths of publishable objects.
        """
        # TODO: support excludeable items
        try:
            exclude_cre = self.get_exclude_cre()
            include_cre = self.get_include_cre()
        except:
            if globls.debug:
                traceback.print_exc()
            utils.print_exit("error: bad include and/or exclude")
        
        paths = []
        for name in names:
            path = os.path.join(self.path, name)
            if include_cre.match(path) and not exclude_cre.match(path):
                paths.append(path)
                for root, dirnames, filenames in special_links_walk(path):
                    for dirname in dirnames:
                        path2 = os.path.join(root, dirname)
                        if include_cre.match(path2) and not exclude_cre.match(path2):
                            paths.append(path2)
                    for filename in filenames:
                        path2 = os.path.join(root, filename)
                        if include_cre.match(path2) and not exclude_cre.match(path2):
                            paths.append(path2)
        return paths

    def is_similar(self, package_name):
        """Return true if the given package name is similar to that
        of this package. Similar means "short names" and "platforms"
        match.
        """
        short_name, version, platform = package_name.split("_", 2)
        return short_name == self.short_name and platform == self.platform
        
    # operations
    def execute_script(self, step, pub_domain=None):
        """Execute script for step.
        """
        path = self.path+"/.ssm.d/"+step
        if not os.path.isfile(path):
            return
        utils.print_verbose("executing %s script" % step)
        if step in ["post-install", "pre-uninstall"]:
            cmd = [path, self.domain.path, self.path]
        elif step in ["pre-publish", "post-publish", "pre-unpublish", "post-unpublish"]:
            cmd = [path, self.domain.path, self.path, pub_domain.path]
        else:
            cmd = None

        if cmd:
            # execute cmd using new subprocess or old popen2
            try:
                from subprocess import Popen
                popen_type = "subprocess"
            except:
                try:
                    from popen2 import Popen3 as Popen
                    popen_type = "popen2"
                except:
                    raise Exception("error: no subprocess/popen support")

            if not os.access(path, os.X_OK):
                utils.print_warning("warning: setup script (%s) is not executable" % path)
                
            if True or os.environ.get("SSM_OLD_PREPOST") != None:
                if not (os.access(path, os.X_OK) and open(path).readline().startswith("#!")):
                    # emulate system()
                    cmd.insert(0, "/bin/sh")
                    sys.stderr.write("warning: using /bin/sh to run pre-/post- script\n")

            try:
                if popen_type == "subprocess":
                    p = Popen(cmd, bufsize=10000000)
                    p.wait()
                    returncode = p.returncode
                else:
                    p = Popen(cmd, bufsize=10000000)
                    status = p.wait()
                    if os.WIFEXITED(status):
                        returncode = os.WEXITSTATUS(status)
                    else:
                        returncode = -1
            except:
                returncode = -1

            if returncode != 0:
                raise Exception("error: execute script failed")
        return

    def install(self, tarf, username, groupname, clobber, force=False):
        """Install package from file.
        """
        if self.domain.is_frozen():
            raise utils.SSMExitException("error: domain is frozen")

        force = force or globls.force
        cwd = os.getcwd()

        if self.exists() and not (force or clobber):
            raise utils.SSMExitException("error: package already installed")

        try:
            utils.chdir(self.domain.path)
            for member in tarf.getmembers():
                try:
                    path = os.path.normpath(member.name)
                    if path.startswith(self.name):
                        if os.path.exists(path):
                            if not clobber:
                                utils.print_warning("warning: clobbering not enabled (%s)" % path)
                                continue
                            elif os.path.isdir(path):
                                utils.print_warning("warning: cannot clobber directory (%s)" % path)
                                continue
                            elif os.path.isfile(path):
                                utils.print_warning("warning: clobbering file (%s)" % path)
                                utils.remove(path)
                        member.uname = username
                        member.gname = groupname
                        utils.print_verbose("extracting member (%s)" % member.name)
                        tarf.extract(member)
                    elif path != ".":
                        utils.print_warning("warning: rejecting member not part of package (%s)" % path)
                except:
                    if globls.debug:
                        traceback.print_exc()
                    utils.print_error("error: could not extract file (%s)" % path)

            self.execute_script("post-install")
            self.domain.add_installed(self.path)
            self.domain.remove_broken(self.path)
        except:
            if globls.debug:
                traceback.print_exc()
            raise utils.SSMExitException("error: could not install")

        utils.chdir(cwd)

    def uninstall(self):
        """Uninstall/remove package.
        """
        if self.domain.is_frozen():
            raise utils.SSMExitException("error: domain is frozen")

        try:
            try:
                self.execute_script("pre-uninstall")
            except:
                if not globls.force:
                    raise
            if os.path.exists(self.path):
                utils.rmtree(self.path)
            self.domain.remove_installed(self.path)
            self.domain.remove_broken(self.path)
        except:
            if globls.debug:
                traceback.print_exc()
            self.domain.add_broken(self.path)
            raise utils.SSMExitException("error: could not uninstall")
