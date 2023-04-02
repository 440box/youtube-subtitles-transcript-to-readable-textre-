# Download a list of youtube files and save in drive folder
<ol>
<li>Make a modifiable copy with File -> Open a Copy in colab</li>
<li>Mount your drive by clicking the drive icon in the file explorer on the left</li>
<li>Modify the youtube in yt_urls</li>
<li>Change output_folder to the folder you wish to store mp3's</li>
<li>Run cells, et voila, you have youtube playlist as mp3's in your drive</li>
</ol>


# note: you can test this notebook by just running the cells in order below


# 1.1 Install software

!pip install --upgrade yt_dlp
!apt -y install ffmpeg lame

#@title 1.2 Prepare Folders
import subprocess, os, sys

try:
    from google.colab import drive
    print("Google Colab detected. Using Google Drive.")
    is_colab = True
    #@markdown If you connect your Google Drive, you can save the final image of each run on your drive.
    google_drive = True #@param {type:"boolean"}

except:
    is_colab = False
    google_drive = False
    print("Google Colab not detected.")

if is_colab:
    if google_drive is True:
        drive.mount('/content/drive')
        root_path = '/content/drive/MyDrive/music/'
    else:
        root_path = '/content'
else:
    root_path = os.getcwd()

# a. Change the URLs which one you want to download from youtube 

# b. change output_folder name to something like /content/drive/MyDrive/music/name_this_folder_how_you_want

# Change the URLs which one you want to download from youtube
youtube = 'https://www.youtube.com/watch?v=igY_2A6DjV4' #@param {type:"string"}

yt_urls = ['youtube']

# change this to /content/drive/My Drive/folder_you_want
output_folder = '/content/drive/My Drive/music/subs/' #@param {type:"string"}

import os
def my_mkdirs(folder):
  if os.path.exists(folder)==False:
    os.makedirs(folder)
my_mkdirs('/content/tmp/')

my_mkdirs(output_folder)

# DOWNLOAD if you want only mp3 sound

# download youtube videos and save it co /content/tmp
for ind,url in enumerate(yt_urls):
  !yt-dlp --restrict-filenames --trim-filenames 25 $url -f 'bestaudio[ext=m4a]' -o 'tmp/%(title)s.m4a'
  
  # !yt-dlp --skip-download --write-auto-sub  $url -o '/content/drive/My Drive/music/AIsubs/%(title)s.vtt'

## for username, password and twofactor use options
# -u, --username USERNAME
#       Login with this account ID
# -p, --password PASSWORD
#       Account password. If this option is left out, yt-dlp will ask interactively
# -2, --twofactor TWOFACTOR
#       Two-factor authentication code

## To list the available subtitles on a YouTube video with yt-dlp:
# yt-dlp --list-subs VIDEOURL
# If the video has subtitles it will print them out including their available formats:
# Language Name    Formats
# en       English vtt, ttml, srv3, srv2, srv1, json3
## Choosing the language and saving it as a subtitle format file:
# yt-dlp --write-subs en --sub-format json3 VIDEOURL # or --skip-download --write-auto-sub
# Or as default will be a .vtt file
# !yt-dlp --restrict-filenames --trim-filenames 25 --skip-download --write-auto-sub --write-subs en $url -o 'tmp/%(title)s.vtt'

# This one if you want subtitles only, you can skip this if you dont need this

# download youtube subtitles and save it co /content/tmp
for ind,url in enumerate(yt_urls):
  
  !yt-dlp --restrict-filenames --skip-download --write-auto-sub  $url -o '/content/drive/My Drive/music/subs/%(title)s.vtt'


## To list the available subtitles on a YouTube video with yt-dlp:
# yt-dlp --list-subs VIDEOURL
# If the video has subtitles it will print them out including their available formats:
# Language Name    Formats
# en       English vtt, ttml, srv3, srv2, srv1, json3
## Choosing the language and saving it as a subtitle format file:
# yt-dlp --write-subs en --sub-format json3 VIDEOURL  # or --skip-download --write-auto-sub
# Or as default will be a .vtt file
# !yt-dlp --restrict-filenames --trim-filenames 25 # or --skip-download --write-auto-sub --write-subs en $url -o 'tmp/%(title)s.vtt'

# Replace quality of music output . 128k below to 256k if you want a better quality and don't care about space and than CONVERT to mp3

# convert to mp3 and prepare to move it to drive
import glob
files = glob.glob('/content/tmp/*')
for file in files:
  out_file = f'{output_folder}{file[13:-1]}.mp3'
  file = file.replace(' ','\ ')
  out_file = out_file.replace(' ','\ ')
  !ffmpeg -i $file -vn -ab 128k -ar 44100 -y $out_file
# now yoy can download it from /content/


remove timestaps and other shit from vtt subtitles files and make it readable as anormal text (this section not ready yet , need to make it better)



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


def remove_tags(text):
    """
    Remove vtt markup tags
    """
    tags = [
        r'</c>',
        r'<c(\.color\w+)?>',
        r'<\d{2}:\d{2}:\d{2}\.\d{3}>',

    ]

    for pat in tags:
        text = re.sub(pat, '', text)

    # extract timestamp, only kep HH:MM
    text = re.sub(
        r'(\d{2}:\d{2}):\d{2}\.\d{3} --> .* align:start position:0%',
        r'\g<1>',
        text
    )

    text = re.sub(r'^\s+$', '', text, flags=re.MULTILINE)
    return text

def remove_header(lines):
    """
    Remove vtt file header
    """
    pos = -1
    for mark in ('##', 'Language: en',):
        if mark in lines:
            pos = lines.index(mark)
    lines = lines[pos+1:]
    return lines


def merge_duplicates(lines):
    """
    Remove duplicated subtitles. Duplacates are always adjacent.
    """
    last_timestamp = ''
    last_cap = ''
    for line in lines:
        if line == "":
            continue
        if re.match('^\d{2}:\d{2}$', line):
            if line != last_timestamp:
                yield line
                last_timestamp = line
        else:
            if line != last_cap:
                yield line
                last_cap = line


def merge_short_lines(lines):
    buffer = ''
    for line in lines:
        if line == "" or re.match('^\d{2}:\d{2}$', line):
            yield '\n' + line
            continue

        if len(line+buffer) < 80:
            buffer += ' ' + line
        else:
            yield buffer.strip()
            buffer = line
    yield buffer


def main():
    vtt_file_name = sys.argv[1]
    txt_name =  re.sub(r'.vtt$', '.txt', vtt_file_name)
    with open(vtt_file_name) as f:
        text = f.read()
    text = remove_tags(text)
    lines = text.splitlines()
    lines = remove_header(lines)
    lines = merge_duplicates(lines)
    lines = list(lines)
    lines = merge_short_lines(lines)
    lines = list(lines)

    with open(txt_name, 'w') as f:
        for line in lines:
            f.write(line)
            f.write("\n")



if __name__ == "__main__":
    main()


