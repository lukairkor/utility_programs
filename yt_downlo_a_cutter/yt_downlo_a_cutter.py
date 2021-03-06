#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import pytube
from moviepy.video.io.VideoFileClip import VideoFileClip
from moviepy.audio.io.AudioFileClip import AudioFileClip
import enquiries
import os
import datetime
import re
import sys
from moviepy.editor import preview
from os.path import isfile, join
from os import listdir

# information about video
def video_info(youtube):
    conversion = datetime.timedelta(seconds=youtube.length)
    # video description
    print('\nVideo description: ', youtube.description)
    print('Rating', youtube.rating)
    print('Length', conversion )
    print('Views', youtube.views, "\n") 
    
    # chosing video format/available media formats
    itagi = youtube.streams.filter(file_extension='mp4')
    
    # listing all avilible video formats
    for x in range(len(itagi)):
        # remove specific character from string
        result = re.sub(r"[<>\"]", "", str(itagi[x]), flags=re.I)
        # delete part of strings that started with words "vcode or acode" to end
        exp = re.compile('vcodec')
        if re.search(exp, str(itagi[x])):
            pos = re.search(" vcodec", str(itagi[x])).start()
            result = result[:pos-8]
        else:
            pos = re.search(" acodec", str(itagi[x])).start()
            result = result[:pos-8]
        
        print(result)
    
    # print("\nstart\n",itagi,"\nstop\n")
    itag = input('Choose itag (only number e.g. 18):\n')
    yt1 = youtube.streams.get_by_itag(int(itag)) 
    filesize = yt1.filesize
    return filesize

# calculate downloaded percent
def progress(chunk, file_handle, bytes_remaining):
    global filesize
    os.system('clear')
    remaining = (100 * bytes_remaining) / filesize
    step = 100 - int(remaining)
    print("Completed:", step, "%") # show the percentage of completed download
    
# downloading video
def down_yt_vid(youtube, path, kind):
    if kind == 0:        
        video = youtube.streams.filter().first().download(path)
    elif kind == 1:
        video = youtube.streams.filter(only_audio = True).first().download(path)
    rename_file(video)
    # video_play(video)

# rename file
def rename_file(video):
    options = ['Yes', 'No']
    choice = enquiries.choose('Do you want rename file?: ', options)
    if choice == options[0]:    
        new_name = input("Enter new name (without extension):\n")
        os.rename(video, new_name +'.mp4')
        return new_name
    elif choice == options[1]:  
        return video
        
    
# convert time from h.m.s to sec
def time_conver(time_tex):
    x = re.findall("[0-9]+", time_tex)
    h = int(x[0]) * 3600
    m = int(x[1]) * 60
    s = int(x[2])
    suma = h + m + s
    return(suma)

# convert time from sec to h.m.s
def time_conver_from_secon(clip):
    # convert time from sec to h.m.s
    sec = clip.duration
    # mins = (clip.duration % 3600) / 60
    m, s = divmod(sec, 60)
    h, m = divmod(m, 60)    
    m = str(int(m))
    h = str(int(h))
    s = str(int(s))

    print("Duration : "+h+"."+m+"."+s )
    # convert back to seconds
    print("\nInput begining and the end of file as: 0.0.0")
    print("Begining:")
    start = input()
    start = time_conver(start)
    stop = input("The end:\n")
    stop = time_conver(stop)
    
    return start, stop
    
# cropping video    
def cropp_video(name, path):
    source_path = path + "/" + name
    options = ['Cut Video [only]: ', 'Cut Audio and convert to mp3']
    choice = enquiries.choose('Choose one of these options: ', options)
    # cut only video into video
    if choice == options[0]:
        clip = VideoFileClip(source_path)  
        start, stop = time_conver_from_secon(clip)
        clip = VideoFileClip(source_path).subclip(start, stop)
        print(start, stop)        
        # num = 0  
        name = rename_file(name)  
        print(name)    
        source_path = path + "/" + name
        clip.write_videofile(name + ".mp4", bitrate="4000k",
                              threads=1, preset='ultrafast', codec='h264')
    # cut audio and video into only audio           
    elif choice == options[1]:  
        clip = AudioFileClip(source_path)  
        start, stop = time_conver_from_secon(clip)
        clip = AudioFileClip(source_path).subclip(start, stop)
        print(start, stop)
        name = rename_file(name)
        print(name)
        source_path = path + "/" + str(name)
        clip.write_audiofile(name + ".mp3")
        
    input("\nPress any key to continue..")    

# preview video
def video_play(name):  
    clip = VideoFileClip(name)
    # looping video 3 times
    clip.preview(fps = 20)

# main loop
if __name__ == "__main__":
    assert ('linux' in sys.platform), "This code runs on Linux only."
    path = os.getcwd()
    
    options = ['Download Video', 'Crop file', 'Close']
    while(True):
        os.system('clear')
        choice = enquiries.choose('Choose one of these options: ', options)
        if choice == options[0]:
            # url = "https://www.youtube.com/watch?v=wELOA2U7FPQ&t=8430s"
            url = input("Enter url of video:\n")
            url = str(url)
            try:
                youtube = pytube.YouTube(url, on_progress_callback=progress)
                
                filesize = video_info(youtube)
                # video_play(url)
                optionss = ['Download Video', 'Download only sound', 'Back']
                choice = enquiries.choose('Choose one of these options: ', optionss)
                print(choice)    
                if choice == optionss[0]:
                    down_yt_vid(youtube, path, 0)
                elif choice == optionss[1]:
                    down_yt_vid(youtube, path, 1)  
                elif choice == optionss[2]:
                    continue
            # pytube.exceptions.RegexMatchError:
            except pytube.exceptions.RegexMatchError:
              print('The Regex pattern did not return any matches for the video: {}'.format(url))      
            except pytube.exceptions.ExtractError:
              print ('An extraction error occurred for the video: {}'.format(url))      
            except pytube.exceptions.VideoUnavailable:
              print('The following video is unavailable: {}'.format(url))
            input("\nPress any key to continue..")
        elif choice == options[1]:
            # list files in folder
            dirs = os.listdir(path)
            for file in dirs:
                if isfile(join(path, file)):
                    print(file)
            # type file name from above list
            file = input("Enter file name from files above:\n")
            try:
                open(file)
                cropp_video(file, path)
            except IOError:
                input("\nCant find this file.\nPress any key to try again..")
        elif choice == options[2]:
            print("See you soon!")
            break



