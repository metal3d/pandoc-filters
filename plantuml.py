#!/usr/bin/python
from pandocfilters import toJSONFilter, RawBlock, Para, Image, Str
from subprocess import Popen, PIPE
import os
import hashlib
import shutil

def plantuml_call(content, filetype="png"):
    p = Popen(["plantuml", "-t%s" % filetype, "-p"], stdin=PIPE, stdout=PIPE)
    (child_stdin, child_stdout) = (p.stdin, p.stdout)
    child_stdin.write(content.encode('utf-8'))
    child_stdin.close()
    p.wait()
    if p.returncode == 0:
        return child_stdout.read()
    return None

def plant(key, value, fmt, meta):
    if key == "CodeBlock":
        [[ident, classes, keyvals], code] = value

        if "plantuml" in classes:
            caption = ""
            for c in keyvals:
                if c[0] == "caption":
                    caption = c[1]

            m = hashlib.md5()
            m.update(code)
            h = m.hexdigest()

            filetype="png"
            if fmt == "latex":
                filetype = "eps"

            f = "/tmp/%s.%s" % (h, filetype)

            if not os.path.exists(f):
                code = plantuml_call(code, filetype)
                if code is not None:
                    open(f , "w").write(code)

            return Para([Image([Str(caption)], [f, caption])])


if __name__ == "__main__":
    toJSONFilter(plant)

