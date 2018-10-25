#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# ssm/utils.py

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

"""Provides utility functions. Does not import any non-system
packages except for ssm.globls.
"""

# system imports
import grp
import os
import os.path
import pwd
import shutil
import sys
import time
import traceback

#
from ssm import globls

class SSMException(Exception):
    pass

class SSMExitException(SSMException):
    pass

def dumps(s, path):
    open(path, "w+").write(s)

def get_profile_paths(subscribe_type):
    if subscribe_type == "user":
        login_path = os.path.expanduser("~/.login")
        profile_path = os.path.expanduser("~/.profile")
    else:
        if os.uname()[0].lower() == "irix64":
            login_path = os.path.expanduser("/etc/cshrc")
        else:
            login_path = os.path.expanduser("/etc/csh.login")
        profile_path = os.path.expanduser("/etc/profile")
    return login_path, profile_path

def get_ssmd_profile_paths(subscribe_type):
    if subscribe_type == "user":
        dir_path = os.path.expanduser("~/.ssm.d")
    else:
        dir_path = "/etc/ssm.d"
    login_path = "%s/login" % dir_path
    profile_path = "%s/profile" % dir_path
    return dir_path, login_path, profile_path
    
def get_symlinks(path):
    paths = []
    try:
        _, names, filenames = os.walk(path).next()
        names.extend(filenames)
    except:
        if globls.debug:
            traceback.print_exc()
        raise
        names = []
    for name in names:
        filename = os.path.join(path, name)
        if os.path.islink(filename):
            paths.append(os.readlink(filename))
    return paths

def get_path_timestamp(path):
    try:
        st = os.lstat(path)
        timestamp = time.strftime("%Y/%m/%dT%H:%M", time.gmtime(st.st_mtime))
    except:
        timestamp = "***"
    return timestamp

def get_terminal_size():
    """Get terminal (rows, cols) size.
    """
    import fcntl
    import termios
    import struct

    try:
      nrows, ncols, pixrows, pixcols = struct.unpack("HHHH", fcntl.ioctl(0, termios.TIOCGWINSZ, struct.pack("HHHH", 0, 0, 0, 0)))
    except IOError:  # Not a terminal?  Use some sensible default.
      nrows, ncols = 24, 80
    return nrows, ncols

def groupname(gid=None):
    try:
        if gid == None:
            gid = os.getgid()
        return grp.getgrgid(gid).gr_name
    except:
        return str(gid)

def loads(path, alt=""):
    try:
        s = open(path, "r").read()
    except:
        s = alt
    return s

def print_columns(lines, headings=None, width=80, gap=2):
    """Print lines in multiple columns, with optional headings.
    """
    if len(lines) == 0:
        return
    max_line_len = max(map(len, lines))
    nlines = len(lines)
    # ncols = (width-(ncols-1)*gap)/max_line_len
    ncols = max((width+gap)/(max_line_len+gap), 1)
    nrows = (nlines+(ncols-1))/ncols
    fmt = "%%-%ss" % max_line_len
    gapfmt = " "*gap
    for i in range(nrows):
        chars = []
        for j in range(ncols):
            k = j*nrows+i
            if k < nlines:
                chars.append(fmt % lines[k])
            if j < ncols-1:
                chars.append(gapfmt)
        print "".join(chars)

def print_error(s):
    print s
    globls.error_count += 1
    
def print_exit(s, value=1):
    print s
    sys.exit(value)

def print_verbose(s):
    if globls.verbose:
        print s

def print_warning(s):
    print s
    globls.warning_count += 1

def prompt(msg):
    return raw_input(msg+" ")

def read_control_map(path):
    """Return control files contents as map.
    """
    m = {}
    try:
        lines = open(path).read().split("\n")
    except:
        lines = []
    key = None
    for line in lines:
        t = line.split(":")
        if len(t) == 2:
            key = t[0].strip()
            value = t[1].strip()
        else:
            value = t[0].strip()
        if key != None:
            key = key.lower()
            if key in m:
                m[key] = m[key]+"\n"+value
            else:
                m[key] = value

    title = m.get("description", "***").split("\n")[:1]
    m["title"] = len(title) and title[0] or ""
    
    return m

def username(uid=None):
    if uid == None:
        uid = os.getuid()
    return pwd.getpwuid(uid).pw_name

#
# wrappers
#
def chdir(path):
    print_verbose("chdir(%s)" % path)
    os.chdir(path)
        
def chmod(path, mode):
    print_verbose("chmod(%s, 0%o)" % (path, mode))
    os.chmod(path, mode)
        
def chown(path, uid, gid):
    print_verbose("chown(%s, %s, %s)" % (path, uid, gid))
    os.chown(path, uid, gid)

def lchown(path, uid, gid):
    print_verbose("lchown(%s, %s, %s)" % (path, uid, gid))
    os.lchown(path, uid, gid)

def copy(src, dst):
    print_verbose("copy(%s, %s)" % (src, dst))
    try:
        shutil.copy(src, dst)
    except Exception:
        if globls.force:
            print_verbose("copy failed; continuing because of --force")
        else:
            raise
        
def copyfile(src, dst):
    print_verbose("copyfile(%s, %s)" % (src, dst))
    try:
        shutil.copyfile(src, dst)
    except Exception:
        if globls.force:
            print_verbose("copy failed; continuing because of --force")
        else:
            raise
        
def copytree(src, dst):
    print_verbose("copytree(%s, %s)" % (src, dst))
    try:
        shutil.copytree(src, dst)
    except Exception:
        if globls.force:
            print_verbose("copy failed; continuing because of --force")
        else:
            raise

def makedirs(path, mode=None):
    print_verbose("makedirs(%s, %s)" % (path, mode))
    if not os.path.isdir(path):
        if mode:
            os.makedirs(path, mode)
        else:
            os.makedirs(path)
        
def mkdir(path, mode=None):
    print_verbose("mkdir(%s, %s)" % (path, mode))
    if not os.path.isdir(path):
        if mode:
            os.mkdir(path, mode)
        else:
            os.mkdir(path)

# TODO: should there be a remove_link()? checks using lexists()

def remove(path, interactive=False):
    print_verbose("remove(%s)" % path)
    if os.path.exists(path) or os.path.islink(path):
        if globls.force or not interactive or raw_input("remove item (%s) (y/n)? " % path) == "y":
            os.remove(path)

def removedirs(path, interactive=False):
    print_verbose("removedirs(%s)" % path)
    if os.path.exists(path):
        if globls.force or not interactive or raw_input("Remove item (%s) [y/n]? " % path) == "y":
            os.removedirs(path)

def rename(src, dst):
    print_verbose("rename(%s, %s)" % (src, dst))
    os.rename(src, dst)
        
def rmdir(path, interactive=False):
    print_verbose("rmdir(%s)" % path)
    if os.path.exists(path):
        if globls.force or not interactive or raw_input("Remove item (%s) [y/n]? " % path) == "y":
            os.rmdir(path)

def rmtree(path, interactive=False):
    print_verbose("rmtree(%s)" % path)
    if os.path.exists(path):
        if globls.force or not interactive or raw_input("Remove item (%s) [y/n]? " % path) == "y":
            shutil.rmtree(path)

def setegid(gid):
    print_verbose("setegid(%s)" % gid)
    os.setegid(gid)

def seteuid(uid):
    print_verbose("seteuid(%s)" % uid)
    os.seteuid(uid)
        
def symlink(src, link_name):
    print_verbose("symlink(%s, %s)" % (src, link_name))
    os.symlink(src, link_name)
        
def touch(path):
    print_verbose("open(%s, \"a\")" % path)
    f = file(path, "a")
    f.close()
