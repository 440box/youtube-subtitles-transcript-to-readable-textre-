"""
Convert YouTube subtitles(vtt) to human readable text.
Download only subtitles from YouTube with youtube-dl:
youtube-dl  --skip-download --convert-subs vtt <video_url>
Note that default subtitle format provided by YouTube is ass, which is hard
to process with simple regex. Luckily youtube-dl can convert ass to vtt, which
is easier to process.
To conver all vtt files inside a directory:
find . -name "*.vtt" -exec python vtt2text.py {} \;
"""
import sys
import re
import argparse


def remove_markup_tags(text):
    """
    Remove VTT markup tags from text
    """
    color_tag_pattern = r'<c(\.color\w+)?>'
    end_color_tag_pattern = r'</c>'
    timestamp_pattern = r'<\d{2}:\d{2}:\d{2}\.\d{3}>'

    text = re.sub(end_color_tag_pattern, '', text)
    text = re.sub(color_tag_pattern, '', text)
    text = re.sub(timestamp_pattern, '', text)

    # extract timestamp and keep only HH:MM
    timestamp_pattern = r'(\d{2}:\d{2}):\d{2}\.\d{3} --> .* align:start position:0%'
    text = re.sub(timestamp_pattern, r'\g<1>', text)

    # remove empty lines and leading/trailing whitespace
    text = re.sub(r'^\s+$', '', text, flags=re.MULTILINE)
    return text


def remove_header(lines):
    """
    Remove VTT file header from list of lines
    """
    header_markers = ['##', 'Language: en']
    for marker in header_markers:
        if marker in lines:
            lines = lines[lines.index(marker) + 1:]
    return lines


def remove_duplicates(lines):
    """
    Remove duplicate subtitles. Duplicates are always adjacent.
    """
    last_timestamp = ''
    last_subtitle = ''
    for line in lines:
        if line == "":
            continue
        elif re.match('^\d{2}:\d{2}$', line):
            if line != last_timestamp:
                yield line
                last_timestamp = line
        else:
            if line != last_subtitle:
                yield line
                last_subtitle = line


def merge_short_lines(lines, max_line_length):
    """
    Merge short lines of text that are adjacent to longer lines.
    """
    buffer = ''
    for line in lines:
        if line == "" or re.match('^\d{2}:\d{2}$', line):
            # always output timestamp or blank lines
            yield '\n' + line
        elif len(line + buffer) < max_line_length:
            buffer += ' ' + line.strip()
        else:
            yield buffer.strip()
            buffer = line.strip()
    yield buffer.strip()


def write_lines_to_file(lines, file_name):
    with open(file_name, 'w') as f:
        for line in lines:
            f.write(line + "\n")


def main():
    parser = argparse.ArgumentParser(description='Convert VTT subtitle file to plain text')
    parser.add_argument('input_file', help='path to input VTT file')
    parser.add_argument('-o', '--output', help='path to output text file')
    parser.add_argument('-m', '--max-line-length', type=int, default=80,
                        help='maximum line length for merged text (default: 80)')
    args = parser.parse_args()

    input_file_name = args.input_file
    output_file_name = args.output or re.sub(r'\.vtt$', '.txt', input_file_name)
    max_line_length = args.max_line_length

    with open(input_file_name) as f:
        input_text = f.read()

    text = remove_markup_tags(input_text)
    lines = text.splitlines()
    lines = remove_header(lines)
    lines = remove_duplicates(lines)
    lines = merge_short_lines(lines, max_line_length)
    write_lines_to_file(lines, output_file_name)


if __name__ == "__main__":
    main()