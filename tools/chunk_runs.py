"""
Splits a runs_XXXX.txt-style file into fixed-size chunks, so you don't have
to count lines by hand before sending a batch. Chunks never span across two
different entry labels -- each chunk stays within one label, even if that
means the last chunk of an entry is smaller than the target size.

Produces ONE output file marked at two levels at once:
  - small "----- chunk N -----" markers at your translation-batch size
    (e.g. every 15 lines) -- copy one of these at a time for translation
  - bigger "===== REVIEW CHECKPOINT ===== " markers every few chunks,
    at roughly your review-batch size (e.g. every 50 lines) -- once you
    hit one of these, everything back to the previous checkpoint is one
    review-sized batch to bring me

Usage:
    python chunk_runs.py <runs_file.txt> <small_size> <review_size> <output_file.txt>

Example:
    python chunk_runs.py runs_0002.txt 15 50 chunks_0002.txt
"""
import sys, re, io

HEADER_RE = re.compile(r'^#####\s+(\S+)\s+\(.*\)\s*(?:#####)?\s*$')
RUN_RE = re.compile(r'^\[(\d+)\]\s?(.*)$')


def parse_lines_by_label(path):
    """Returns [(label, [(idx, full_text), ...]), ...] in file order,
    where full_text preserves multi-line ("gap") runs as one string."""
    sections = []
    current_label = None
    current_runs = []
    current_idx = None
    current_lines = []

    def flush_run():
        if current_idx is not None:
            current_runs.append((current_idx, '\n'.join(current_lines).rstrip()))

    def flush_section():
        flush_run()
        if current_label is not None and current_runs:
            sections.append((current_label, list(current_runs)))

    with io.open(path, encoding='utf-8') as f:
        for raw_line in f:
            line = raw_line.rstrip('\n')
            header_match = HEADER_RE.match(line)
            if header_match:
                flush_section()
                current_label = header_match.group(1)
                current_runs = []
                current_idx = None
                current_lines = []
                continue
            run_match = RUN_RE.match(line)
            if run_match:
                flush_run()
                current_idx = int(run_match.group(1))
                text = re.sub(r'\s*<==.*$', '', run_match.group(2))
                current_lines = [text]
                continue
            if line.strip() == '':
                continue
            if current_idx is not None:
                current_lines.append(line)
    flush_section()
    return sections


def main():
    in_path, small_size, review_size, out_path = sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4]
    sections = parse_lines_by_label(in_path)

    out = io.open(out_path, 'w', encoding='utf-8')
    chunk_num = 0
    lines_since_checkpoint = 0
    checkpoint_num = 0
    for label, runs in sections:
        for start in range(0, len(runs), small_size):
            chunk = runs[start:start + small_size]
            chunk_num += 1
            first_idx, last_idx = chunk[0][0], chunk[-1][0]
            out.write(f'----- chunk {chunk_num} -- {label} (runs {first_idx}-{last_idx}, {len(chunk)} lines) -----\n')
            for idx, text in chunk:
                out.write(f'[{idx}] {text}\n')
            out.write('\n')
            lines_since_checkpoint += len(chunk)
            if lines_since_checkpoint >= review_size:
                checkpoint_num += 1
                out.write(f'===== REVIEW CHECKPOINT {checkpoint_num} -- everything since the last checkpoint is one review batch =====\n\n')
                lines_since_checkpoint = 0
    if lines_since_checkpoint > 0:
        checkpoint_num += 1
        out.write(f'===== REVIEW CHECKPOINT {checkpoint_num} (final, partial) -- everything since the last checkpoint is one review batch =====\n')
    out.close()
    print(f'Wrote {chunk_num} translation chunks (size {small_size}) and {checkpoint_num} review checkpoints (size ~{review_size}) to {out_path}')


if __name__ == '__main__':
    main()
