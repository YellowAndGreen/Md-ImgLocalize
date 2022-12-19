"""
This code is adapted from https://github.com/xZaR3y4p/Img_link_to_local_markdown
WORKFLOW:
1. choose to edit origin file or generate new file
2. create output dir(if needed)
3. find all md files in the given directory
4. for each md file, use regex to find online links, attach a random name to each link(as its value), finally a dict is obtained
5. replace the link with random initialized name, output the md file
6. download the images, save output files in the img folder
"""
import argparse
import asyncio
import logging
import os
import random
import re
import string
import time

import aiohttp


def create_folder(folder="out"):
    if not os.path.exists(folder):
        os.mkdir(folder)


async def image_download(session, img_url, img_path, semaphore):
    """
    Download the image from the link and save it to img_path.
    """
    async with semaphore:
        img = await session.get(img_url)
        content = await img.read()
        with open(img_path, 'wb') as f:
            f.write(content)  # save img


async def download(url_dict, out_folder_path):
    """
    Download images in url_dict, use async to speed up.
    """
    semaphore = asyncio.Semaphore(8)  # limit max coroutine numbers to 8
    # Create session which contains a connection pool
    async with aiohttp.ClientSession() as session:
        # Create all tasks
        await asyncio.gather(*[image_download(session, img_url, os.path.join(out_folder_path, img_path), semaphore)
                               for img_url, img_path in url_dict.items()])


def open_and_read(file_path):
    """
    Open and reads the file received and returns the content
    """
    try:
        with open(file_path, "r", encoding="utf-8") as current_opened_file:
            print(f"\nOpened file: {file_path}")
            logging.info(f"Opened file: {file_path}\n")
            return current_opened_file.read()
    except Exception as e:
        logging.exception(f"Error when opening file {file_path}")


def write_file(folder_path, file_name, file_data):
    with open(folder_path + "\\" + file_name, "w", encoding="utf-8") as file:
        file.write(file_data)


def create_url2local_dict(regex, file_data, file_name):
    """
     Find(regex) URL's for images on the received "file_data" and creates a dictionary with the url's for later download
     as keys and a random 10 digit number followed by the images names (something.jpg) in order to save the files later
     and prevent name collisions
    """
    url_dict = {}
    try:
        urls = re.findall(regex, file_data)
        urls += [[url[5:-1], url[-5:-1]] for url in re.findall("src=\"[a-zA-z]+://[^\s]*\"", file_data)]  # 匹配<img>标签的图片链接
        for url in urls:
            random_name = "".join([random.choice(string.hexdigits) for i in range(10)])
            if url[0] not in url_dict.keys():
                # 兼容微信公众号文章中图片url的下载
                # https://mmbiz.qlogo.cn/mmbiz_png/Z6bicxIx5naK3giaeiaZSkoPXHyciabECXKfBsZrLo3614gicicCF8jzVWoDlO6rYXSvgfnRnlnWx2qUDLN02nFzg3Pg/640?wx_fmt=png&tp=webp&wxfrom=5&wx_lazy=1&wx_co=1&retryload=2
                if "/mmbiz_png/" in url[0]:
                    r = re.search('/mmbiz_\w{3,4}/', url[0])
                    end = url[0].rfind("/")
                    url_dict[url[0]] = random_name + url[0][r.span()[1]:end] + ".png"
                else:
                    # 兼容图片url中 图片格式后缀带参数的url
                    # https://cdn.nlark.com/yuque/0/2021/webp/396745/1639464187563-0de4b9a4-7d0d-4824-97d0-d05b8dfc3ef6.webp?x-oss-process=image%2Fresize%2Cw_750%2Climit_0', '1639464187563-0de4b9a4-7d0d-4824-97d0-d05b8dfc3ef6.webp?x-oss-process=image%2Fresize%2Cw_750%2Climit_0
                    name = url[1]
                    ix = name.rfind("?")
                    if ix > -1:
                        name = name[:ix]
                    url_dict[url[0]] = random_name + name
    except:
        logging.exception("Error when trying to search url's and add them to dicionary")
    return url_dict


def file_replace_url(file_data, url_dict, file_name):
    """
    Edit the markdown files, changing the url's links for a new name corresponding to the name of the local file
    images that will be downloaded later
    """
    for key, value in url_dict.items():
        file_data = file_data.replace(key, value)
        print(f"\nreplaced: {key}\nwith {value}\n on file {file_name}\n")
        logging.info(f"replaced: {key}\nwith: {value}\non file: {file_name}\n")
    return file_data


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('--md_path', help="markdown directory")
    parser.add_argument('--log', action='store_true', help="whether to generate log file")
    parser.add_argument('--modify_source', action='store_true', help="whether to modify source md file directly")
    return parser.parse_args()


class MdImageLocal:
    def __init__(self, md_path=os.getcwd(), out_folder_name="out", user_agent=None, log=False, modify_source=False):
        self.md_path = md_path  # target md dir
        self.user_agent = user_agent if user_agent else "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"
        # Defines the folder to write the new markdown files and the downloaded images
        # if modify_source is True, out_folder_path will be set as md_path
        self.out_folder_path = os.path.abspath(md_path) if modify_source else \
            os.path.abspath(os.path.join(md_path, out_folder_name))
        self.regex = r"(?:\(|\[)(?P<url>(?:https?\:(?:\/\/)?)(?:\w|\-|\_|\.|\?|\/)+?\/(?P<end>(?:(?=_png\/|_jpg\/|_jpeg\/|_gif\/|_bmp\/|_svg\/)[^\/]+?[^()]+)|(?:[^\/()]+(?:\.png|\.jpg|\.jpeg|\.gif|\.bmp|\.svg)?)))(?:\)|\])"
        # Create new folder to receive the downloaded imgs and edited MD files
        if not modify_source:
            create_folder(self.out_folder_path)  # create new output folder
        # Create new log file
        logging.basicConfig(filename=os.path.join(self.out_folder_path, 'Markdown-ImageLocalize.log') if log else None,
                            filemode="w",
                            level=logging.DEBUG if log else logging.ERROR)
        logging.info(f"New folder created: {self.out_folder_path}\n")
        print(f"New folder created: {self.out_folder_path}")

    def run(self):
        all_img_dict = {}  # dict that collect all images' urls and paths
        # Loop throught every markdown file on this script folder
        for filename in os.listdir(self.md_path):
            print("\n")
            if filename[-3:] != ".md":
                logging.info(f"Skipped file: {filename}\n")
                print(f"Skipped file: {filename}")
                continue
            # Open and read each file
            file_data = open_and_read(os.path.join(self.md_path, filename))
            # Create a dictionary of images URLs for each file
            url_dict = create_url2local_dict(self.regex, file_data, filename)
            # skip if no online link in this file
            if url_dict:
                # Create a folder with md filename which contains images
                create_folder(os.path.join(self.out_folder_path, filename[:-3] + ".assets"))
                # Specify img folder
                url_dict = {key: os.path.join(filename[:-3] + ".assets", value) for key, value in url_dict.items()}
                # Edit the read content of each file, replacing the found imgs urls with local file names instead
                edited_file_data = file_replace_url(file_data, url_dict, filename)
                # Add url_dict to all_img_dict
                all_img_dict.update(url_dict)
                # Write the modified markdown files
                write_file(self.out_folder_path, filename, edited_file_data)
            else:
                logging.info(f"No url! Skipped file: {filename}\n")
                print(f"No url! Skipped file: {filename}")
            print(f"Closed file: {filename}")
            logging.info(f"Closed file: {filename}\n")
        # Download the images listed on the dictionary of found urls for each file
        loop = asyncio.get_event_loop()
        loop.run_until_complete(download(all_img_dict, self.out_folder_path))
        print("\n\n\nfiles and the downloaded images on the folder:")
        print(f"{self.out_folder_path}")


def recursion(cur_path):
    for filename in os.listdir(cur_path):
        print("\n")
        p = cur_path + "\\" + filename
        if os.path.isdir(p):
            recursion(cur_path + "\\" + filename)
        elif filename.strip() == 'out':
            continue
        else:
            MdImageLocal(md_path=cur_path, log=args.log, modify_source=args.modify_source).run()
            break


if __name__ == "__main__":
    time0 = time.time()
    print("\n\n\nStarting..\n")
    args = parse_args()
    recursion(args.md_path)
    print(f"time consumed:{time.time() - time0}")
    print("\nPress enter to close.")
    input()
