"""
Apply black only on mdified files
"""

__version__ = '0.0.3'

import black
import argparse
import sys

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


def filtermark(gen):
    try:
        for l in gen:
            if l.strip().endswith('# bm12'):
                next(gen)
                continue
            yield l
    except StopIteration:
        return


def darken_file(filename, ranges, dry_run):
    with open(filename, 'r') as f:
        s = f.read()
    
    s = '\n'.join(insert_marks(s.splitlines(), ranges))
    res = s
    res = black.format_str(s, mode=black.FileMode())
    
    lines = res.splitlines()
   
    re_lines = list(filtermark(iter(lines)))
    
    if not dry_run:
        with open(filename, 'w') as f:
            f.write('\n'.join(re_lines))
    else:
        for i,l in enumerate(re_lines, start=1):
            print(f"{i:02}", l)



def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    parser = argparse.ArgumentParser(prog='darken', description='Apply black only to some specific lines of a file.')
    parser.add_argument('--ranges', help='which lines to apply darken to')
    parser.add_argument('--since', help='comitish')
    parser.add_argument('--dry-run', help='', action='store_true')
    parser.add_argument('filename', nargs='?', help='filename to process')
    parsed = parser.parse_args(argv)
    print(parsed)

    res = parsed.ranges
    if res:
        ranges = parse_range_list(res)
    if parsed.since:
        from collections import defaultdict
        dct = defaultdict(lambda:[])
        print('trying to extract changes since', parsed.since)
        import subprocess
        sub = subprocess.run(['git','diff', '-U0', parsed.since], stdout=subprocess.PIPE)
        current_file = None
        for line in  sub.stdout.decode().splitlines():
            if line.startswith('+++'):
                current_file = line[5:]
                continue
            if line.startswith('@@'):
                res,add = line.split('@@')[1][1:-1].split(' ')
                from_,lenght,*_ = add.split(',')+['1']
                print(current_file, int(from_), int(from_)+int(lenght) )
                dct[current_file].append((int(from_), int(from_)+int(lenght)))


            else:
                continue

        for k,v in dct.items():
            if k == 'dev/null':
                continue
            ranges = set(chain(*[range(start,stop+1) for start,stop in v]))
            print(k,ranges)
            try:
                darken_file(k[1:], ranges,  parsed.dry_run)
            except: 
                pass
        sys.exit()

    filename = parsed.filename

    darken_file(filename, ranges,  parsed.dry_run)

    
if __name__ == '__main__':
    main()
