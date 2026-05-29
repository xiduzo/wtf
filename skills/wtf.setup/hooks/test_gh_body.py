#!/usr/bin/env python3
"""Regression test for gh-body.py — self-contained, no network, no real `gh`.

Runs the helper as a subprocess against a *stub* `gh` placed first on PATH, so
it exercises the real argv-building and UTF-8 re-encoding without touching
GitHub. Guards the three things that are easy to regress when editing the
helper: (1) correct `gh` subcommand + flag forwarding per verb, (2) bodies
written UTF-8 no-BOM / LF with emoji & accents intact, (3) temp-file cleanup
and error codes.

Run:  python3 skills/wtf.setup/hooks/test_gh_body.py
Exits non-zero if any check fails.
"""
import os
import subprocess
import sys
import tempfile

HELPER = os.path.join(os.path.dirname(os.path.abspath(__file__)), "gh-body.py")

# A body that breaks naive shells: emoji, em-dash, accents, CRLF, leading BOM.
INPUT_BYTES = ("﻿" + "# Título 🎯\r\nLínea con café ☕ — fin\r\n").encode("utf-8")
# What the helper must hand to gh: same text, no BOM, LF only.
EXPECTED_BYTES = ("# Título 🎯\nLínea con café ☕ — fin\n").encode("utf-8")

_results = []


def check(name, ok, info=""):
    _results.append((name, bool(ok), info))


class StubGh:
    """Context manager: writes a stub `gh` to PATH; records argv + captured
    --body-file/--notes-file bytes; emits a known body on `view ... -q`."""

    def __enter__(self):
        self.work = tempfile.mkdtemp(prefix="ghbody-regress-")
        self.tmpd = os.path.join(self.work, "tmp")
        os.makedirs(self.tmpd)
        bindir = os.path.join(self.work, "bin")
        os.makedirs(bindir)
        self.log = os.path.join(self.work, "argv.log")
        self.cap = os.path.join(self.work, "capture.bin")
        stub = (
            f"#!{sys.executable}\n"
            "import sys, os\n"
            "open(os.environ['GH_LOG'], 'a', encoding='utf-8')"
            ".write('\\t'.join(sys.argv[1:]) + '\\n')\n"
            "a = sys.argv[1:]\n"
            "for fl in ('--body-file', '--notes-file'):\n"
            "    if fl in a:\n"
            "        open(os.environ['GH_CAP'], 'wb').write(open(a[a.index(fl)+1], 'rb').read())\n"
            "if 'view' in a and '-q' in a:\n"
            "    sys.stdout.buffer.write(os.environ['GH_BODY_OUT'].encode('utf-8')); sys.exit(0)\n"
            "print('https://example.com/fake/1'); sys.exit(0)\n"
        )
        ghp = os.path.join(bindir, "gh")
        with open(ghp, "w") as fh:
            fh.write(stub)
        os.chmod(ghp, 0o755)
        self.env = dict(os.environ)
        self.env["PATH"] = bindir + os.pathsep + self.env["PATH"]
        self.env["TMPDIR"] = self.tmpd
        self.env["GH_LOG"] = self.log
        self.env["GH_CAP"] = self.cap
        self.env["GH_BODY_OUT"] = EXPECTED_BYTES.decode("utf-8")
        return self

    def __exit__(self, *exc):
        import shutil
        shutil.rmtree(self.work, ignore_errors=True)

    def helper_temps(self):
        return {f for f in os.listdir(self.tmpd) if f.startswith("wtf-ghbody-")}

    def run(self, args, body_input=None):
        for f in (self.log, self.cap):
            if os.path.exists(f):
                os.remove(f)
        extra = []
        if body_input is not None:
            bf = os.path.join(self.work, "writetool.md")
            with open(bf, "wb") as fh:
                fh.write(body_input)
            extra = ["--body-file", bf]
        proc = subprocess.run(
            [sys.executable, HELPER] + args + extra, env=self.env, capture_output=True
        )
        argv = []
        if os.path.exists(self.log):
            first = open(self.log).read().strip().split("\n")[0]
            argv = first.split("\t") if first else []
        cap = open(self.cap, "rb").read() if os.path.exists(self.cap) else None
        return proc.returncode, proc.stdout, proc.stderr, argv, cap


def main():
    with StubGh() as gh:
        # read
        rc, out, err, argv, _ = gh.run(["read", "42"])
        path = out.decode().strip()
        check("read -> issue view 42 --json body -q .body", argv[:3] == ["issue", "view", "42"], argv[:3])
        check("read prints an existing temp path", os.path.isfile(path), path)
        if os.path.isfile(path):
            raw = open(path, "rb").read()
            check("read file no BOM / LF only / emoji intact",
                  not raw.startswith(b"\xef\xbb\xbf") and b"\r\n" not in raw and "🎯".encode() in raw)
        _, _, _, argv, _ = gh.run(["read", "7", "--pr"])
        check("read --pr -> pr view", argv[:3] == ["pr", "view", "7"], argv[:3])

        # create
        before = gh.helper_temps()
        rc, out, err, argv, cap = gh.run(
            ["create", "--title", "🎯 Epic: x", "--label", "epic", "--label", "p1", "--milestone", "M3"],
            body_input=INPUT_BYTES,
        )
        check("create -> issue create", argv[:2] == ["issue", "create"], argv[:2])
        check("create emoji title + both labels", "🎯 Epic: x" in argv and argv.count("--label") == 2)
        check("create forwards unknown flag --milestone", "--milestone" in argv and argv[argv.index("--milestone") + 1] == "M3")
        check("create body re-encoded no-BOM/LF/emoji/accent", cap == EXPECTED_BYTES, repr(cap))
        check("create cleans its temp body file", gh.helper_temps() == before)
        rc, out, err, argv, cap = gh.run(["create", "--pr", "--title", "x", "--base", "feature/1-x"], body_input=EXPECTED_BYTES)
        check("create --pr --base -> pr create with --base", argv[:2] == ["pr", "create"] and "--base" in argv)
        rc, out, err, argv, cap = gh.run(["create", "--title", "x", "--base", "main"], body_input=EXPECTED_BYTES)
        check("issue create drops --base + warns", "--base" not in argv and "base is only valid" in err.decode())

        # edit
        before = gh.helper_temps()
        rc, out, err, argv, cap = gh.run(["edit", "99", "--add-label", "x"], body_input=INPUT_BYTES)
        check("edit -> issue edit 99", argv[:3] == ["issue", "edit", "99"], argv[:3])
        check("edit body re-encoded + passthrough --add-label", cap == EXPECTED_BYTES and "--add-label" in argv)
        check("edit cleans its temp body file", gh.helper_temps() == before)
        rc, out, err, argv, cap = gh.run(["edit", "5", "--pr"], body_input=EXPECTED_BYTES)
        check("edit --pr -> pr edit", argv[:3] == ["pr", "edit", "5"])

        # comment
        before = gh.helper_temps()
        rc, out, err, argv, cap = gh.run(["comment", "5"], body_input=INPUT_BYTES)
        check("comment -> issue comment 5", argv[:3] == ["issue", "comment", "5"], argv[:3])
        check("comment body re-encoded no-BOM/LF/emoji/em-dash", cap == EXPECTED_BYTES, repr(cap))
        check("comment cleans its temp body file", gh.helper_temps() == before)
        rc, out, err, argv, cap = gh.run(["comment", "9", "--pr"], body_input=EXPECTED_BYTES)
        check("comment --pr -> pr comment 9", argv[:3] == ["pr", "comment", "9"])

        # review
        before = gh.helper_temps()
        rc, out, err, argv, cap = gh.run(["review", "12", "--request-changes"], body_input=INPUT_BYTES)
        check("review -> pr review 12", argv[:3] == ["pr", "review", "12"], argv[:3])
        check("review forwards verdict + body re-encoded", "--request-changes" in argv and cap == EXPECTED_BYTES)
        check("review cleans its temp body file", gh.helper_temps() == before)

        # release
        before = gh.helper_temps()
        nf = os.path.join(gh.work, "notes.md")
        with open(nf, "wb") as fh:
            fh.write(INPUT_BYTES)
        for f in (gh.log, gh.cap):  # release uses --notes-file, so it bypasses gh.run(); clear the append-log first
            if os.path.exists(f):
                os.remove(f)
        rc = subprocess.run([sys.executable, HELPER, "release", "v9.9.9", "--title", "R", "--notes-file", nf],
                            env=gh.env, capture_output=True).returncode
        argv = open(gh.log).read().strip().split("\n")[0].split("\t")
        cap = open(gh.cap, "rb").read()
        check("release -> release create v9.9.9", argv[:3] == ["release", "create", "v9.9.9"], argv[:3])
        check("release uses --notes-file + --title + notes re-encoded", "--notes-file" in argv and "--title" in argv and cap == EXPECTED_BYTES)
        check("release cleans its temp notes file", gh.helper_temps() == before)

        # error paths
        rc, *_ = gh.run(["create", "--title", "x"], body_input=b"caf\xe9")  # invalid UTF-8
        check("non-UTF-8 body -> exit 3", rc == 3, f"rc={rc}")
        rc = subprocess.run([sys.executable, HELPER], env=gh.env, capture_output=True).returncode
        check("no subcommand -> exit 2", rc == 2, f"rc={rc}")
        rc, *_ = gh.run(["edit", "1", "--body-file", os.path.join(gh.work, "nope.md")])
        check("missing body file -> exit 2", rc == 2, f"rc={rc}")

    passed = sum(1 for _, ok, _ in _results if ok)
    for name, ok, info in _results:
        print(("PASS " if ok else "FAIL ") + name + ("" if ok else f"   <-- {info}"))
    print(f"\n{passed}/{len(_results)} checks passed")
    return 0 if passed == len(_results) else 1


if __name__ == "__main__":
    sys.exit(main())
