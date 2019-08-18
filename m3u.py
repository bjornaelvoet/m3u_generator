#!/usr/bin/env python

import os
import sys
import argparse
import glob
import json
from mutagen.mp3 import MP3
from mutagen.easyid3 import EasyID3
import logging

def compose_m3u(dir, mp3s):

    logging.info("Processing directory '%s'..." % dir)

    glob_pattern = "*.[mM][pP]3"

    #Backup current directory and change to new root folder
    try:
        cwd = os.getcwd()
        os.chdir(dir)

        for file in glob.glob(glob_pattern):
            meta_info = {
                'filename': os.path.join(dir, file),
                'length': int(MP3(file).info.length),
                'tracknumber': EasyID3(file)['tracknumber'][0].split('/')[0],
                'artist': EasyID3(file)['artist'],
                'title': EasyID3(file)['title'],
            }

            logging.debug(meta_info)

            mp3s.append(meta_info)
    finally:
        os.chdir(cwd)

def create_m3u(m3u_filename, mp3s, root_folder):
    try:
        playlist = m3u_filename

        if len(mp3s) > 0:
            logging.info("Writing playlist '%s'..." % playlist)

            # write the playlist
            of = open(playlist, 'w')
            of.write("#EXTM3U\n")

            # sorted by order found
            for mp3 in mp3s:
                of.write("#EXTINF:%s,%s - %s\n" % (mp3['length'], mp3['artist'][0], mp3['title'][0]))
                #Remove rootfolder to achieve relative folder structure
                of.write(mp3['filename'].replace(root_folder, '') + "\n")

            of.close()
        else:
            logging.info("No mp3 files found in '%s'." % dir)

    except:
        logging.info("ERROR occured when processing directory '%s'. Ignoring." % dir)
        logging.info("Text: ", sys.exc_info()[0])

def handle_m3u(m3u_info_json):

    m3u_filename = m3u_info_json["m3u_filename"]
    root_folder = m3u_info_json["root_folder"]
    dirs = m3u_info_json["folders"]

    mp3s = []

    for dir in dirs:
        compose_m3u(os.path.join(root_folder, dir), mp3s)

        logging.debug("MP3 files found: %s", mp3s)

    create_m3u(os.path.join(root_folder, m3u_filename), mp3s, root_folder)

def main(argv=None):

    parser = argparse.ArgumentParser(description='Generates m3u files based on json input file.')
    parser.add_argument('-j', '--json', required=True, metavar='json', type=str, nargs=1,
                    help='the json file which will be used')
    loglevel_choices = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    parser.add_argument('-l', '--loglevel', required=False, metavar='loglevel', choices=loglevel_choices, nargs=1, default=["INFO"],
                    help='log level for level of verbosity, allowed values are ' + ', '.join(loglevel_choices))

    args = parser.parse_args()

    #Set logging level
    logging.basicConfig(level=args.loglevel[0])
    
    #Load json file
    with open(args.json[0], 'r') as f:
        loaded_json = json.load(f)
   
    #Iterate over all m3u info that needs to be generated
    for m3u_item in loaded_json:
        handle_m3u(m3u_item)

    return 0

# Main body
if __name__ == '__main__':
    sys.exit(main())
