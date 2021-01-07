# -*- coding: utf-8 -*-
"""data.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1CZB42-sVXTCcYH8dirg_y9vzMsXDmzdP

#import
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install pytube
from pytube import YouTube
import pandas as pd
import numpy as np
from google.colab.patches import cv2_imshow
import cv2
from moviepy.video.io.ffmpeg_tools import ffmpeg_extract_subclip
import re
import pickle

"""#dataframe"""

def modifying_df(df):
  v=[]
  for i in range(len(df)):
    youtube_video_url = 'https://www.youtube.com/watch?v='+df.loc[i,'youtube_id']
    #print(youtube_video_url)
    try:
      #print('in try')
      yt_obj = YouTube(youtube_video_url)
      filters = yt_obj.streams.filter(progressive=True, file_extension='mp4')
      a=filters.get_highest_resolution()
      df.loc[i,'frames']=a.fps
      df.loc[i,'highres']=re.sub('\D','',a.resolution)
      b=filters.get_lowest_resolution()
      df.loc[i,'lowres']=re.sub('\D','',b.resolution)
    except:
      print('in except')
      continue
  return df,v

path='/content/drive/MyDrive/Project/action recognition/700_2020/validate.csv'
df=pd.read_csv(path)
df0=df.copy()
print(df.shape)
## taking only one label at a time
df=df[df['label']=='testifying'].copy()
print(df.shape)
df=df.reset_index(drop=True)
df.index.name='testifying'
df=df.drop(columns=['split','label'])
#df.head()

df,v=final_1(df)
#print(v.shape)
print(df['highres'].unique())
print(df['frames'].unique())
print(df['lowres'].unique())
print(df.isnull().sum())

df=df.dropna()
df.to_pickle('/content/drive/MyDrive/Project/action recognition/outputs/try_1.pkl')

"""#data_create"""

def pre(frame):
  frame=cv2.resize(frame,(224,224))
  return frame

def select(video_frames,frames):
  selected=[]
  if len(video_frames)>frames:
    selected=video_frames[:frames]
  else:
    selected=video_frames
    while len(selected)<frames:
      selected.append(video_frames[-1])
  return selected

def func(start,end):
  frames=300
  ffmpeg_extract_subclip("/content/yt_videomp4.mp4", start, end, targetname="yt_croped.mp4")
  cap = cv2.VideoCapture('/content/yt_croped.mp4')
  video_frames=[]
  while True:
    ret,frame=cap.read()
    if ret==True:
      video_frames.append(pre(frame))
    else:
      break
  cap.release()
  v=select(video_frames,frames)
  if len(v)!=frames:
    print('short')
  ar=np.array(v)
  print(ar.shape)
  return ar

def final(df):
  v=[]
  for i in range(len(df)):
    youtube_video_url = 'https://www.youtube.com/watch?v='+df.loc[i,'youtube_id']
    print('\n',i)
    try:
      yt_obj = YouTube(youtube_video_url)
      filters = yt_obj.streams.filter(progressive=True, file_extension='mp4')      
      start=df.loc[i,'time_start']
      end=df.loc[i,'time_end']
      filters.get_lowest_resolution().download(filename='yt_video.mp4')
      ar=func(start,end)
      v.append(ar)
    except:
      print('\n in except')
      continue

  vs=np.array(v)
  return vs

path='/content/drive/MyDrive/Projects/action recognition/outputs/try_1.pkl'
df=pd.read_pickle(path)
print(df.shape)
df=df.reset_index(drop=True)
#df.head(3)

vs=final(df)

v=vs/vs.max()

def saving(i,v):
  g=v[i*10:(i+1)*10,:,:,:,:]
  with open('/content/drive/MyDrive/Projects/action recognition/outputs/try_2_{}.pkl'.format(i+1),'wb') as f:
    pickle.dump(g,f)
  del g
  del f
  f.close()
  print('saved ',i+1)

for i in range(len(vs)//10):
  saving(i,v)

if len(vs)%10!=0:
  g=v[-(len(vs)%10):,:,:,:,:]
  with open('/content/drive/MyDrive/Projects/action recognition/outputs/try_2_{}.pkl'.format((len(vs)//10)+1),'wb') as f:
    pickle.dump(g,f)
  f.close()
  del g
  del f
  print('saved ',(len(vs)//10)+1)
