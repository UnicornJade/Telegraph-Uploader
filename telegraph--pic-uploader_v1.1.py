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
def get_title(dir):
    tmp = dir[::-1]
    index = 0
    for i in range(len(tmp)):
        if tmp[i] == '\\' :
            index = i
            break
    return dir[-index:]

def change_size(path, max_wh):
    """
    按比例变化
    Args:
        :param path: 图片路径
        :param max_wh: 最大高/宽
    Returns:
        :return: new image
    """
    img = Image.open(path)
    w, h = img.size
    old_max = max(w,h)
    # print("source size:", w, h)
    if old_max <= 5600:
        return path
    # 按比例调整获得新尺寸
    pert = int(max_wh * 100 / old_max)
    prop_s = lambda size, p: int(size * p / 100)
    new_w = int(prop_s(w, pert))
    new_h = int(prop_s(h, pert))
    new_img = img.resize((new_w, new_h))
    new_path = str(path)[0:-4] + '_rz.jpg'
    new_img.save(new_path)
    return new_path

def gif_press(outfile):
    
    copy_one = str(outfile)[0:-4] + '_compressed.gif'
    copyfile(outfile,copy_one)
    outfile = copy_one
    # 自定义压缩尺寸 rp*rp
    rp = 250
    
    # 图片缓存空间
    image_list = []
    
    # 读取gif图片
    im = Image.open(outfile)
    
    # 提取每一帧，并对其进行压缩，存入image_list
    for frame in ImageSequence.Iterator(im):
        frame = frame.convert('RGB')
        if max(frame.size[0], frame.size[1]) > rp:
            frame.thumbnail((rp, rp))
        image_list.append(frame)
    
    # 计算帧之间的频率，间隔毫秒
    duration = (im.info)['duration'] / 1000
    
    # 读取image_list合并成gif
    imageio.mimsave(outfile, image_list, duration=duration)

    return outfile

def png_press(outfile, mb=5000, quality=75, k=0.77):

    copy_one = str(outfile)[0:-4] + '_compressed.png'
    copyfile(outfile,copy_one)
    outfile = copy_one
    o_size = os.path.getsize(outfile) // 1024  # 函数返回为字节，除1024转为kb（1kb = 1024 bit）
    # print('before_size:{} target_size:{}'.format(o_size, mb))
    if o_size <= mb:
        return outfile
    
    ImageFile.LOAD_TRUNCATED_IMAGES = True  # 防止图像被截断而报错
    
    while o_size > mb:
        im = Image.open(outfile)
        x, y = im.size
        out = im.resize((int(x*k), int(y*k)), Image.LANCZOS)  # 最后一个参数设置可以提高图片转换后的质量
        try:
            out.save(outfile, quality=quality)  # quality为保存的质量，从1（最差）到95（最好），此时为85
        except Exception as e:
            # print(e)
            break
        o_size = os.path.getsize(outfile) // 1024
        # print(o_size)
    return outfile
    
def compress_image(outfile): # 通常你只需要修改mb大小
    """不改变图片尺寸压缩到指定大小
    :param outfile: 压缩文件保存地址
    :param mb: 压缩目标，KB
    :param k: 每次调整的压缩比率
    :param quality: 初始压缩比率
    :return: 压缩文件地址，压缩文件大小
    """
    if  str(outfile)[-4:] == ".gif" or str(outfile)[-4:] == ".GIF":
        outfile = gif_press(outfile)
    else :
        outfile = png_press(outfile,mb=5000, quality=85, k=0.8)
    return outfile

def telegraph_file_upload(path_to_file):
    '''
    Sends a file to telegra.ph storage and returns its url
    Works ONLY with 'gif', 'jpeg', 'jpg', 'png', 'mp4' 
    
    Parameters
    ---------------
    path_to_file -> str, path to a local file
    
    Return
    ---------------
    telegraph_url -> str, url of the file uploaded

    >>>telegraph_file_upload('test_image.jpg')
    https://telegra.ph/file/16016bafcf4eca0ce3e2b.jpg    
    >>>telegraph_file_upload('untitled.txt')
    error, txt-file can not be processed
    '''
    file_types = {'gif': 'image/gif', 'jpeg': 'image/jpeg', 'jpg': 'image/jpg', 'png': 'image/png', 'mp4': 'video/mp4'}
    file_ext = path_to_file.split('.')[-1].lower()
    
    if file_ext in file_types:
        file_type = file_types[file_ext]
    else:
        return f'error, {file_ext}-file can not be proccessed' 
    o_size = os.path.getsize(path_to_file)
    # print("pic size:", int(o_size / 1024) ,"kb")
    if o_size >= 5120*1024:
        path_to_file = compress_image(path_to_file)
        
    with open(path_to_file, 'rb') as f:
        url = 'https://telegra.ph/upload'
        while 1:
            try:
                response = requests.post(url, files={'file': ('file', f, file_type)}, timeout=30, proxies=myproxies)
                break

            except Exception as e:
                # print(f"[ Error ] {e} \n Trying again ...")
                time.sleep(2)
                continue
    
    telegraph_url = json.loads(response.content)
    # print(telegraph_url)
    if type(telegraph_url) != type([1]):
        return ""
    telegraph_url = telegraph_url[0]['src']
    telegraph_url = f'https://telegra.ph{telegraph_url}'
    
    return telegraph_url

def bianli_pics(path):
	
    img_folder = path
    img_list = [os.path.join(nm) for nm in os.listdir(img_folder) if nm[-3:].lower() in ['jpg', 'png', 'gif']]
    ## print(img_list) 将所有图像遍历并存入一个列表
    ## ['test_14.jpg', 'test_15.jpg', 'test_9.jpg', 'test_17.jpg', 'test_16.jpg']
    pics_html = ""

    for i in tqdm(img_list):
        
        one_path = os.path.join(path,i)
        # print(one_path)
        try:
            one_path = change_size(one_path,5500)
            link = telegraph_file_upload(one_path)
        except:
            continue
        img_html = "<img src='{}' style='width: 100%; max-width: 100%; height: auto;' />".format(link)
        # print(link)
        pics_html = pics_html + "" + img_html
        time.sleep(2)
        # file = open (path + '.txt', "w",encoding = "utf-8" )
        # file.write(pics_html)
        ## ./input/test_14.jpg
		## ./input/test_15.jpg
    #print(pics_html)
    return pics_html


#   输入参数：html正文的文件路径
def upload_large_note(archive_txt,max=250):
    htmls = split(archive_txt,max)
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



def dir2telegraph(dir):
    #set your own if you need to manage and edit your artical after pubish it 
    token = "TODO"      

    telegraph = Telegraph(access_token=token)
    telegraph._telegraph.session.proxies = {'https':'socks5h://localhost:7890'}
    # telegraph.create_account(short_name= 'Kris', author_name='Kris wu', author_url='', replace_token=True)

    #you can set successly uploaded img labels here if your task fail
    #the img labels are located in the root directory ,in file : "path.txt"

    # print("Welcome!")

    # links = []
    tmp_img = "" 

    # while (1):
    # print("input folder:")
    Rootfolder = dir
    # D:\test\pics
    # print("html content:")
    html_text = '<br />'
    # Hello_Kris
    for root, dirs, files in os.walk(Rootfolder):
        print("\n",root)
        folder = root 
        biaoti = get_title(folder)
        try:
            print("Uploading folder: ",folder)
            html_imgs = bianli_pics(folder)
            print("[ + ] 图床索引构建完成 ,保存存档...")
            html_content= html_text + tmp_img + html_imgs
            archive_txt = os.path.join(folder,f"{biaoti}.txt")
            with open(archive_txt,'w') as f:
                f.write(html_content)
                print(f"[ + ] Note 存档已保存: {archive_txt} ,尝试上传Telegraph ...")
            while 1:
                try:
                    response = telegraph.create_page(
                    title= biaoti,
                    html_content= html_text + tmp_img + html_imgs,
                    author_name = 'Jade',
                    author_url='',
                    )

                    print(f"\n[ * ] Telegraph 笔记创建成功: {response['url']} ")
                    break
                except Exception as e:
                    if "CONTENT_TOO_BIG" in str(e):
                        upload_large_note(archive_txt,100)
                        print("\n* Finished!")
                        break
                    print(f"[ Error ] {e} \n Trying again ...")
                    time.sleep(2)
                    continue
            
            # links.append(response['url'])
        except Exception as e: 
                print(e)
                break
        # print("")
        # print("Here are all page links: ")
        # for link in links:
        #     print(link)

#max size 5600

def is_image_valid(file_path):
    try:
        # 使用Pillow库尝试打开图片文件
        with Image.open(file_path) as img:
            img.verify()
        return True
    except Exception as e:
        print(f"Invalid image: {file_path} - {e}")
        return False

def delete_invalid_images(folder_path):
    count_deleted = 0
    invalid_images = []

    with concurrent.futures.ThreadPoolExecutor() as executor:
        for root, _, files in os.walk(folder_path):
            image_files = [os.path.join(root, file) for file in files if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff'))]
            results = executor.map(is_image_valid, image_files)
            for file, result in tqdm(zip(image_files, results)):
                if not result:
                    invalid_images.append(file)
                else:
                    # print(f"Valid image: {file}")
                    # sys.stdout.write(f"\r\x1B[KProgress: {file} - Valid")
                    # sys.stdout.flush()
                    continue

    for image_file in invalid_images:
        try:
            os.remove(image_file)
            count_deleted += 1
            # sys.stdout.write(f"\r\x1B[KProgress: {image_file} - Invalid")
            # sys.stdout.flush()
            # print(f"Deleted invalid image: {image_file}")
        except Exception as e:
            print(f"\nError deleting image: {image_file} - {e}")

    return count_deleted

def rm_bad_pics(folder_path):
    print(f"[ + ] 正在检测图片损毁情况: {folder_path} ...")
    deleted_count = delete_invalid_images(folder_path)
    print(f"\n[ * ] Deleted {deleted_count} invalid images.")

parser = argparse.ArgumentParser()
parser.add_argument('-b','--batch')
parser.add_argument('-d','--dir')
args = parser.parse_args()

proxy = '127.0.0.1:7890'
myproxies = {
    "http": "http://%(proxy)s/" % {'proxy': proxy},
    "https": "http://%(proxy)s/" % {'proxy': proxy}
}
if args.dir:
    if os.path.exists(args.dir):
        rm_bad_pics(args.dir)
        dir2telegraph(args.dir)
    else:
        print("[ ! ] 目录不存在!")
if args.batch:
    dirs = [os.path.join(args.batch, name) for name in os.listdir(args.batch) if os.path.isdir(os.path.join(args.batch, name))]
    for dir in dirs:
        if os.path.exists(dir):
            rm_bad_pics(dir)
            dir2telegraph(dir)
        else:
            continue

