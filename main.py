import sys
import shutil
import os
from os import listdir
from os.path import isfile, join
import random
import json

from aubio import source, tempo
from numpy import median, diff


def get_file_bpm(path, params=None):
    """ Calculate the beats per minute (bpm) of a given file.
        path: path to the file
        param: dictionary of parameters
    """
    if params is None:
        params = {}
    # default:
    samplerate, win_s, hop_s = 44100, 1024, 512
    if 'mode' in params:
        if params.mode in ['super-fast']:
            # super fast
            samplerate, win_s, hop_s = 4000, 128, 64
        elif params.mode in ['fast']:
            # fast
            samplerate, win_s, hop_s = 8000, 512, 128
        elif params.mode in ['default']:
            pass
        else:
            raise ValueError("unknown mode {:s}".format(params.mode))
    # manual settings
    if 'samplerate' in params:
        samplerate = params.samplerate
    if 'win_s' in params:
        win_s = params.win_s
    if 'hop_s' in params:
        hop_s = params.hop_s

    s = source(path, samplerate, hop_s)
    samplerate = s.samplerate
    o = tempo("specdiff", win_s, hop_s, samplerate)
    # List of beats, in samples
    beats = []
    # Total number of frames read
    total_frames = 0

    while True:
        samples, read = s()
        is_beat = o(samples)
        if is_beat:
            this_beat = o.get_last_s()
            beats.append(this_beat)
            # if o.get_confidence() > .2 and len(beats) > 2.:
            #    break
        total_frames += read
        if read < hop_s:
            break

    def beats_to_bpm(beats, path):
        # if enough beats are found, convert to periods then to bpm
        if len(beats) > 1:
            if len(beats) < 4:
                print("few beats found in {:s}".format(path))
            bpms = 60./diff(beats)
            return median(bpms)
        else:
            print("not enough beats found in {:s}".format(path))
            return 0

    return beats_to_bpm(beats, path), beats[0], beats[-1]


def get_tempo(fileDir, txtDir):
    bpm, start, end = get_file_bpm(fileDir)

    with open(txtDir, 'w') as f:
        timing = start
        while timing <= end:
            f.write(f'{timing}\n')
            timing += 60/bpm


def copy_file(fileDir, oggDir):
    shutil.copy(fileDir, oggDir)


def get_dir_list(path):
    onlyfiles = [f for f in listdir(path) if isfile(join(path, f))]
    return onlyfiles


def write_json(fileNames, jsonName):
    jsonDict = {
       "author": "Hyun",
       "displayName": "나의 플레이리스트",
       "songFileNames": fileNames
    }

    with open(jsonName, "w") as outfile:
        json.dump(jsonDict, outfile)


if __name__ == "__main__":
    rootPath = sys.argv[1]
    pathList = get_dir_list(rootPath)

    musicList = [
            'zone1_1',
            'zone1_2',
            'zone1_3',
            'zone2_1',
            'zone2_2',
            'zone2_3',
            'zone3_1',
            'zone3_2',
            'zone3_3',
            'zone4_1',
            'zone4_2',
            'zone4_3',
            'zone5_1',
            'zone5_2',
            'zone5_3',
            'boss_1',
            'boss_2',
            'boss_3',
            'boss_4',
            'boss_9',
            'lobby',
            'training',
            'tutorial']

    fileNames = []
    for musicName in musicList:
        finished = False
        while not finished:
            try:
                fileDir = join(rootPath, random.choice(pathList))
                os.makedirs(os.path.dirname(
                    join("music", musicName+'.txt')), exist_ok=True)
                get_tempo(fileDir, join("music", musicName+'.txt'))
                copy_file(fileDir, join("music", musicName+'.ogg'))
                finished = True
                fileNames = fileNames + [fileDir]
            except:
                pass

    write_json(fileNames, "playlist.json")
