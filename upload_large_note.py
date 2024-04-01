from telegraph import Telegraph
import requests
import os,argparse
import json,sys
import time
from PIL import Image
from PIL import ImageFile
from shutil import copyfile
import imageio
from PIL import Image, ImageSequence
from tqdm import tqdm
import concurrent.futures
from split_imgs_html import split

token = "TODO"      
telegraph = Telegraph(access_token=token)
telegraph._telegraph.session.proxies = {'https':'socks5h://localhost:7890'}
inputfile = input("path: ")
htmls = split(inputfile,250)
for html in htmls:
    with open(html,'r') as h:
        content = h.read()
    response = telegraph.create_page(
    title= os.path.basename(html).split(".")[0],
    html_content= content,
    author_name = 'Jade',
    author_url='',
    )
    print(f"\n[ * ] Telegraph 笔记创建成功: {response['url']} ")
