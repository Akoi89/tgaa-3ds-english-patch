"""
Reformats a runs_XXXX.txt-style file (bracketed [N] entries, one per line)
into a cleaner "flowing document" layout -- entry headers kept, but the
bracket numbers stripped and consecutive runs within an entry joined into
readable paragraph text, similar in style to a normal translation script
document.

This is a pure text-reformatting tool -- it doesn't translate or alter the
actual content, just the layout. Works on whatever language the input file
is in (Japanese or your in-progress English), since it's just reorganizing
lines, not reading/understanding them.

Usage:
    python reformat_to_prose.py <runs_file.txt> <output_file.txt>
"""
import sys, re, io

HEADER_RE = re.compile(r'^#####\s+(\S+)\s+\(.*\)\s+#####\s*$')
RUN_RE = re.compile(r'^\[(\d+)\]\s?(.*)$')


def reformat(in_path, out_path):
    out_lines = []
    current_label = None
    paragraph_parts = []

    def flush_paragraph():
        if paragraph_parts:
            out_lines.append(' '.join(paragraph_parts))
            out_lines.append('')
            paragraph_parts.clear()

    with io.open(in_path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            header_match = HEADER_RE.match(line)
            if header_match:
                flush_paragraph()
                current_label = header_match.group(1)
                out_lines.append(f'--- {current_label} ---')
                continue
            run_match = RUN_RE.match(line)
            if run_match:
                text = run_match.group(1) and run_match.group(2) or run_match.group(2)
                text = re.sub(r'\s*<==\s*likely sentence/thought END\s*$', '', text)
                if text.strip():
                    paragraph_parts.append(text.strip())
                continue
            if line.strip() == '':
                continue
            # continuation of the previous run's text (multi-line runs)
            paragraph_parts.append(line.strip())
    flush_paragraph()

    io.open(out_path, 'w', encoding='utf-8').write('\n'.join(out_lines))
    print(f'Wrote {out_path}')


if __name__ == '__main__':
    reformat(sys.argv[1], sys.argv[2])
