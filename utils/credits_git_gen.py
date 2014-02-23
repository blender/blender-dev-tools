import os
import subprocess

class GitCommit:
    __slots__ = (
        "sha1",
        # to extract more info
        "_git_dir",
        )
    def __init__(self, sha1, git_dir):
        self.sha1 = sha1
        self._git_dir = git_dir

    def _log_format(self, format, args=()):
        sha1 = self.sha1.decode('ascii')
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "log",
            "-1",  # only this rev
            sha1,
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
        return self._log_format("%an")

    @property
    def body(self):
        return self._log_format("%B")

    @property
    def files(self):
        return [f for f in self._log_format("format:", args=("--name-only",)).split(b"\n") if f]

    @property
    def files_status(self):
        return [f.split(None, 1) for f in self._log_format("format:", args=("--name-status",)).split(b"\n") if f]


class GitCommitIter:
    __slots__ = (
        "_path",
        "_git_dir",
        "_process",
        )

    def __init__(self, path):
        self._path = path
        self._git_dir = os.path.join(path, ".git")
        self._process = None

    def __iter__(self):
        cmd = (
            "git",
            "--git-dir",
            self._git_dir,
            "log",
            "--format=%H",
            ),
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


if __name__ == __main__:
    for c in GitCommitIter("."):
        print(c.sha1, c.author)
        print(c.body)
        for f in c.files_status:
            print('  ', f)

