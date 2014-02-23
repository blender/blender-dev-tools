#!/usr/bin/env python3

# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

import os
import subprocess


# -----------------------------------------------------------------------------
# Generic git read-only classes for extracting info

class GitCommit:
    __slots__ = (
        "sha1",
        # to extract more info
        "_git_dir",

        # cached values
        "_author",
        "_date",
        "_body",
        "_files",
        "_files_status",
        )
    def __init__(self, sha1, git_dir):
        self.sha1 = sha1
        self._git_dir = git_dir

        self._author = \
        self._date = \
        self._body = \
        self._files = \
        self._files_status = \
        None


    def _log_format(self, format, args=()):
        # sha1 = self.sha1.decode('ascii')
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "log",
            "-1",  # only this rev
            self.sha1,
            "--format=" + format,
            ) + args
        # print(" ".join(cmd))

        p = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            )
        return p.stdout.read()

    @property
    def author(self):
        ret = self._author
        if ret is None:
            content = self._log_format("%an")[:-1]
            ret = content.decode("utf8", errors="ignore")
            self._author = ret
        return ret

    @property
    def date(self):
        ret = self._date
        if ret is None:
            import datetime
            ret = datetime.datetime.fromtimestamp(int(self._log_format("%ct")))
            self._date = ret
        return ret

    @property
    def body(self):
        ret = self._body
        if ret is None:
            content = self._log_format("%B")[:-1]
            ret = content.decode("utf8", errors="ignore")
            self._body = ret
        return ret

    @property
    def files(self):
        ret = self._files
        if ret is None:
            ret = [f for f in self._log_format("format:", args=("--name-only",)).split(b"\n") if f]
            self._files = ret
        return ret

    @property
    def files_status(self):
        ret = self._files_status
        if ret is None:
            ret = [f.split(None, 1) for f in self._log_format("format:", args=("--name-status",)).split(b"\n") if f]
            self._files_status = ret
        return ret


class GitCommitIter:
    __slots__ = (
        "_path",
        "_git_dir",
        "_sha1_range",
        "_process",
        )

    def __init__(self, path, sha1_range):
        self._path = path
        self._git_dir = os.path.join(path, ".git")
        self._sha1_range = sha1_range
        self._process = None

    def __iter__(self):
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "log",
            self._sha1_range,
            "--format=%H",
            )
        # print(" ".join(cmd))

        self._process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            )
        return self

    def __next__(self):
        sha1 = self._process.stdout.readline()[:-1]
        if sha1:
            return GitCommit(sha1, self._git_dir)
        else:
            raise StopIteration


if 0 and __name__ == "__main__":
    for c in GitCommitIter("/src/blender", "HEAD~10..HEAD"):
        print(c.sha1, c.author, c.date)
        print(c.body)
        for f in c.files_status:
            print('  ', f)


# -----------------------------------------------------------------------------
# Class for generating credits

class CreditUser:
    __slots__ = (
        "commit_total",
        "year_min",
        "year_max",
        )
    def __init__(self):
        self.commit_total = 0


class Credits:
    __slots__ = (
        "users",
        )
    def __init__(self):
        self.users = {}

    def process_commit(self, c):
        author = c.author
        year = c.date.year
        cu = self.users.get(author)
        if cu is None:
            cu = self.users[author] = CreditUser()
            cu.year_min = year
            cu.year_max = year

        cu.commit_total += 1
        cu.year_min = min(cu.year_min, year)
        cu.year_max = max(cu.year_max, year)

    def process(self, commit_iter):
        for i, c in enumerate(commit_iter):
            self.process_commit(c)
            if not (i % 100):
                print(i)

    def write(self, filepath,
              is_main_credits=True,
              contrib_companies=()):

        # patch_word = "patch", "patches"
        commit_word = "commit", "commits"

        with open(filepath, 'w', encoding="ascii", errors='xmlcharrefreplace') as file:
            file.write("<h3>Individual Contributors</h3>\n\n")
            for author, cu in sorted(self.users.items()):
                file.write("%s, %d %s %s<br />\n" %
                           (author,
                            cu.commit_total,
                            commit_word[cu.commit_total > 1],
                            ("" if not is_main_credits else (
                             ("- %d" % cu.year_min) if cu.year_min == cu.year_max else
                             ("(%d - %d)" % (cu.year_min, cu.year_max))))))
            file.write("\n\n")

            # -------------------------------------------------------------------------
            # Companies, hard coded
            if is_main_credits:
                file.write("<h3>Contributions from Companies & Organizations</h3>\n")
                file.write("<p>\n")
                for line in contrib_companies:
                    file.write("%s<br />\n" % line)
                file.write("</p>\n")

                import datetime
                now = datetime.datetime.now()
                fn = __file__.split("\\")[-1].split("/")[-1]
                file.write("<p><center><i>Generated by '%s' %d/%d/%d</i></center></p>\n" %
                           (fn, now.year, now.month, now.day))


if 1 and __name__ == "__main__":

    def is_credit_commit_valid(c):
        ignore_dir = (
            b"blender/extern/",
            b"blender/intern/opennl/",
            b"blender/intern/moto/",
            )

        if not any(f for f in c.files if not f.startswith(ignore_dir)):
            return False

        return True

    # TODO, there are for sure more companies then are currently listed.
    # 1 liners for in html syntax
    contrib_companies = (
        "<b>Unity Technologies</b> - FBX Exporter",
        "<b>BioSkill GmbH</b> - H3D compatibility for X3D Exporter, "
        "OBJ Nurbs Import/Export",
        "<b>AutoCRC</b> - Improvements to fluid particles, vertex color baking",
        )

    credits = Credits()
    # commit_range = "HEAD~10..HEAD"
    commit_range = "HEAD"
    citer = GitCommitIter("/src/blender", commit_range)
    credits.process((c for c in citer if is_credit_commit_valid(c)))
    credits.write("credits.html",
        is_main_credits=True,
        contrib_companies=contrib_companies)

