import black
import argparse
import sys

MARK = """\
# fmt: {}  # bm12
"""


from itertools import chain

def parse_range(rng):
    parts = rng.split('-')
    if 1 > len(parts) > 2:
        raise ValueError("Bad range: '%s'" % (rng,))
    parts = [int(i) for i in parts]
    start = parts[0]
    end = start if len(parts) == 1 else parts[1]
    if start > end:
        end, start = start, end
    return range(start, end + 1)

def parse_range_list(rngs):
    return sorted(set(chain(*[parse_range(rng) for rng in rngs.split(',')])))


def insert_marks(lines, ranges):
    activated = False
    yield '# bm12'
    yield "# fmt: off"

    for lnum, line in enumerate(lines, start=1):
        if lnum in ranges and not activated:
            activated = True
            yield '# bm12'
            yield "# fmt: on"
        elif lnum not in ranges and activated:
            activated = False
            yield '# bm12'
            yield "# fmt: off"
        yield line





def main(argv):
    parser = argparse.ArgumentParser(description='Apply black only to some specific lines of a file.')
    parser.add_argument('filename', metavar='filename', type=str,
                    help='filename to process')
    parser.add_argument('--ranges', dest='ranges', metavar='ranges', help='')
    res = parser.parse_args(argv).ranges
    res = '1-21'
    ranges = parse_range_list(res)

    with open('setup.py', 'r') as f:
        s = f.read()
    
    
    s = '\n'.join(insert_marks(s.splitlines(), ranges))
    res = s
    res = black.format_str(s, mode=black.FileMode())
    
    def filtermark(gen):
        try:
            for l in gen:
                if l.strip().endswith('# bm12'):
                    next(gen)
                    continue
                yield l
        except StopIteration:
            return
    
    lines = res.splitlines()
    
    re_lines = list(filtermark(iter(lines)))
    for i,l in enumerate(re_lines, start=1):
        print(f"{i:02}", l)
    
if __name__ == '__main__':
    main(sys.argv)
