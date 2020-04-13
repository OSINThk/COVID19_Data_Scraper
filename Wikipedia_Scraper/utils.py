import re


def sanitize_text(d):
    RE = re.compile(r"""\[\[(File|Category):[\s\S]+\]\]|
        \[\[[^|^\]]+\||
        \[\[|
        \]\]|
        \'{2,5}|
        (<s>|<!--)[\s\S]+(</s>|-->)|
        {{[\s\S\n]+?}}|
        <ref>[\s\S]+</ref>|
        ={1,6}""", re.VERBOSE)
    x = RE.sub('', d)
    while '[' in x:
        startidx = x.index('[')
        endidx = x.rindex(']')
        x = x[:startidx] + x[endidx + 1:]
    x = x.replace('†', "").strip()
    return x


def sanitize_digit(d):
    try:
        x = ''.join(c for c in d if c.isdigit())
        if x:
            return str(int(x))
        else:
            return "0"
    except:
        return "0"
