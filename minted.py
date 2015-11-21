#!/usr/bin/python
from pandocfilters import toJSONFilter, RawInline, RawBlock
from subprocess import Popen, PIPE
import re

import logging

def format_go(content):
    p = Popen(["gofmt"], shell=True, stdin=PIPE, stdout=PIPE)
    (child_stdin, child_stdout) = (p.stdin, p.stdout)
    child_stdin.write(content.encode('utf-8'))
    child_stdin.close()
    p.wait()
    if p.returncode == 0:
        return child_stdout.read().decode('utf-8')

    
    logging.warn("gofmt crashed: " + str(p.returncode) + "\n" + "content: "+content)
    return content

def minted(key, value, fmt, meta):
    if key == "CodeBlock":
        [attr, code] = value
        try:
            lang = attr[1][0]
        except ValueError:
            lang = meta.get('minted-language', None)

        caption = None
        title = None

        if lang == "go":
            code = format_go(code)

        try:
            f=0
            t=0
            content = code.split("\n")
            block = None
            for a in attr[2]:
                if a[0] == "title":
                    title = a[1]
                if a[0] == "caption":
                    caption = a[1]
                if a[0] == "include":
                    content = []
                    for line in open(a[1]):
                        content.append(line.rstrip())
                if a[0] == "from":
                    f=int(a[1])
                if a[0] == "to":
                    t=int(a[1])

                if a[0] == "block":
                    #capture // START XXX to // END XXX
                    block = a[1]


            if t > 0:
                content = content[f:t]
                logging.warn(content)


            # extract block if given
            if block is not None:
                tmp = []
                add = False
                for c in content:
                    if re.match('.*START\s+'+block, c):
                        add = True
                    if re.match('.*END\s+'+block, c):
                        add = False
                    if add:
                        tmp.append(c)
                content = tmp


            # remove "OMIT" lines
            content = [ c for c in content if c.find("OMIT") < 0 ]


            # unindent and let format_go to do the job
            if lang == "go":
                for idx, c in enumerate(content):
                    content[idx] = re.sub(r"^[\t\s]+","", c)
                code = format_go("\n".join(content))
            else:
                # rebuild code
                code = "\n".join(content)


        except Exception as e:
            logging.exception(e)


        # styles
        style = meta.get("minted-block-"+lang+"-style", None)
        if style is None:
            style = meta.get("minted-block-style", None)

        bg = meta.get("minted-block-"+lang+"-bg", None)
        if bg is None:
            bg = meta.get("minted-block-bg", None)

        opt = ['tabsize=4','obeytabs']
        ff = meta.get("minted-block-fontfamily", None)
        if ff is not None:
            opt.append('fontfamily='+ff['c'][0]['c'])

        if style or bg:
            if style: opt.append('style=' + style['c'][0]['c'])
            if bg: opt.append('bgcolor=' + bg['c'][0]['c'])


        if len(opt):
            opt = '[' + ",".join(opt) + ']'
        else:
            opt = ''

        block = [
            r'\begin{minted}'+ opt +'{'+ lang + '}',
            code,
            r'\end{minted}'
        ]

        if caption is not None:
            block.insert(0, r'\begin{listing}[H]')
            block.insert(1, r'\caption' + '{' + caption + '}')
            block.append(r'\end{listing}')

        if meta.get('minted-tcolorbox', "false") == "true" and (title or caption):
            # tcolorbox, to test
            if title is not None:
                block.insert(0, r'\begin{tcolorbox}{' + title + '}')
            else:
                block.insert(0, r'\begin{tcolorbox}')

            block.append(r'\end{tcolorbox}')

        return RawBlock(fmt,"\n".join(block))

    if key == "Code":
        [_, code] = value
        lang =  meta.get("minted-language", None)
        if lang is not None:
            lang = lang['c'][0]['c']

        sep = '#'
        if lang in ('python', 'bash', 'ruby'):
            # hashtag is problematic for those languages,
            # so use slashes
            sep = '/'

        return RawInline(fmt, r'\mintinline{' + lang + '}'+ sep + code + sep)

if __name__ == "__main__":
    toJSONFilter(minted)
