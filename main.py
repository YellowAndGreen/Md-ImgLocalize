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
import sys
import logging
import os
import random
import re
import string
import time
import json
import aiohttp
import urllib.request
from typing import Dict

from utils import create_folder, is_valid_url, write_file


REGEX_PATTERN=r"(?:!\[.*?\])(?:\(|\[)(?P<url>(?:https?\:(?:\/\/)?)(?:\w|\-|\_|\.|\?|\/)+?\/(?P<end>(?:(?=_png\/|_jpg\/|_jpeg\/|_gif\/|_bmp\/|_svg\/)[^\/]+?[^()]+)|(?:[^\/()]+(?:\.png|\.jpg|\.jpeg|\.gif|\.bmp|\.svg)?)))(?:\)|\])"
COROUTINE_NUM=2
    

async def image_download(
    session: aiohttp.ClientSession,
    img_url: str,
    img_path: str,
    semaphore: asyncio.Semaphore
) -> None:
    """
    Download the image from the link and save it to img_path.
    """
    async with semaphore:
        # 如果下载图片不存在，再下载，防止重复下载文件
        if not os.path.exists(img_path):
            try:
                img = await session.get(img_url)
                content = await img.read()
                with open(img_path, 'wb') as f:
                    f.write(content)  # save img
            except aiohttp.ClientError as e:
                logging.error(f"Error when downloading {img_url}...")
        else:
            logging.info(f"Skipped file: {img_path}\n")


async def download(url_dict: Dict[str, str], out_folder_path: str, coroutine_num: int) -> None:
    """
    Download images in url_dict, use async to speed up.
    """
    semaphore = asyncio.Semaphore(coroutine_num)  # limit max coroutine numbers to 2
    # Create session which contains a connection pool
    async with aiohttp.ClientSession() as session:
        # Create all tasks
        await asyncio.gather(*[image_download(session, img_url, os.path.join(out_folder_path, img_path), semaphore)
                               for img_url, img_path in url_dict.items()])


def download_images(url_dict: Dict[str, str], folder_path: str, user_agent: str) -> None:
    """
    Download the images (not async) from the links obtained from the markdown files to the "destination folder"
    The user-agent can be specified in order to circumvent some simple potential connection block
    """
    for url, name in url_dict.items():
        if not is_valid_url(url):
            logging.warning(f"Not valid url:{url}")
            continue
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', user_agent)]
        urllib.request.install_opener(opener)
        save_name = os.path.join(folder_path,name)
        try:
            urllib.request.urlretrieve(url, save_name)
        except Exception as e:
            logging.exception(f"Error when downloading {url}")


def open_and_read(file_path: str) -> str:
    """
    Open and reads the file received and returns the content
    """
    try:
        with open(file_path, "r", encoding="utf-8") as current_opened_file:
            logging.info(f"Opened file: {file_path}")
            return current_opened_file.read()
    except Exception as e:
        logging.exception(f"Error when opening file {file_path}")


def write_image_url_json(out_folder_path: str, all_img_dict: Dict[str, str]) -> int:
    all_img_dict_json = json.dumps(all_img_dict,sort_keys=False, indent=4, separators=(',', ': '))
    write_file(out_folder_path, 'all_img_dict.json', all_img_dict_json)
    return 0


def read_image_url_json(out_folder_path: str) -> Dict[str, str]:
    with open(os.path.join(out_folder_path,'all_img_dict.json'), 'r', encoding='utf-8') as f:
        all_img_dict = json.load(f)
    return all_img_dict


def delete_image_url_json(out_folder_path: str) -> None:
    os.remove(os.path.join(out_folder_path,'all_img_dict.json'))


def create_url2local_dict(regex: str, file_data: str, file_name: str) -> Dict[str, str]:
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
    except Exception as e:
        logging.exception("Error when trying to search url's and add them to dicionary")
    return url_dict



def file_replace_url(file_data: str, url_dict: Dict[str, str], file_name: str) -> str:
    """
    Edit the markdown files, changing the url's links for a new name corresponding to the name of the local file
    images that will be downloaded later
    """
    for key, value in url_dict.items():
        file_data = file_data.replace(key, value)
        logging.info(f"replaced: {key}\nwith: {value}\non file: {file_name}\n")
    return file_data


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument('--md_path', help="markdown directory")
    parser.add_argument('--log', action='store_true', help="whether to generate log file")
    parser.add_argument('--relative', action='store_true', help="convert all absolute path to relative")
    parser.add_argument('--modify_source', action='store_true', help="whether to modify source md file directly")
    parser.add_argument('--coroutine_num', type=int, default=2, help="number of coroutine")
    parser.add_argument('--del_dict', action='store_true', help="delete all dict")
    return parser.parse_args()


class MdImageLocal:
    def __init__(self, md_path: str = os.getcwd(), out_folder_name: str = "out", user_agent: str = None,
                 log: bool = False, modify_source: bool = False) -> None:
        self.md_path = md_path  # target md dir
        self.user_agent = user_agent if user_agent else "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1"
        # Defines the folder to write the new markdown files and the downloaded images
        # if modify_source is True, out_folder_path will be set as md_path
        self.out_folder_path = os.path.abspath(md_path) if modify_source else \
            os.path.abspath(os.path.join(md_path, out_folder_name))
        self.regex = REGEX_PATTERN
        self.coroutine_num = COROUTINE_NUM
        # Create new folder to receive the downloaded imgs and edited MD files
        if not modify_source:
            create_folder(self.out_folder_path)  # create new output folder

        logging.info(f"New folder created: {self.out_folder_path}")
        

    def run(self) -> None:
        """localize images in this folder's markdown files"""
        all_img_dict = {}  # dict that collect all images' urls and paths
        # 判断是否是 .assets 文件夹，如果是的话，则 all_img_dict 置为空
        # 如果不存在 all_img_dict.json 就说明在该文件夹是第一次运行，则读取所有文件并创建 all_img_dict.json
        if self.out_folder_path[-7:]==".assets":
            all_img_dict={}
        elif not os.path.exists(os.path.join(self.out_folder_path,'all_img_dict.json')):
            # Loop throught every markdown file on this script folder
            for filename in os.listdir(self.md_path):
                if not filename.endswith(".md"):
                    logging.info(f"Skipped file: {filename}\n")
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
                logging.info(f"Closed file: {filename}\n")
            write_image_url_json(self.out_folder_path, all_img_dict)
        # 如果存在 all_img_dict.json 则直接使用其中的内容，也就是重复运行的情况下，仍能保证所有下载的文件名均相同，不会重复下载
        else:
            if args.del_dict:
                logging.warning(f"Deleting {os.path.join(self.out_folder_path,'all_img_dict.json')} ...")
                delete_image_url_json(self.out_folder_path)
                return
            logging.warning("All_img_dict.json exists, will use the existed url dict.")
            all_img_dict = read_image_url_json(self.out_folder_path)
        # Download the images listed on the dictionary of found urls for each file
        loop = asyncio.get_event_loop()
        loop.run_until_complete(download(all_img_dict, self.out_folder_path, self.coroutine_num))
        logging.warning(f"\nFiles and the downloaded images on the folder:{self.out_folder_path}")
        # 使用 noasync 的方式下载之前下载失败的图片
        fail_dict = {}
        logging.warning('Check and re-downloading fail images...')
        for url,name in all_img_dict.items():
            if not os.path.exists(os.path.join(self.out_folder_path, name)):
                fail_dict.update({url:name})
        download_images(fail_dict,self.out_folder_path,self.user_agent)
        # 打印最终未下载图片列表
        fail_dict = {}
        for url,name in all_img_dict.items():
            if not os.path.exists(os.path.join(self.out_folder_path, name)):
                fail_dict.update({url:name})
        for url, name in fail_dict.items():
            logging.warning(f"Failed to download: {url}, Save as: {name}")


    @classmethod
    def convert_absolute_to_relative(cls, md_path: str, img_folder: str) -> None:
        """
        Convert absolute image paths to relative paths in a single Markdown file.

        Args:
        - md_path (str): Path to the Markdown file.
        - img_folder (str): Path to the image folder.
        """
        with open(md_path, 'r', encoding='utf-8') as md_file:
            md_content = md_file.read()

        regex_pattern = r"!\[.*?\]\((?P<path>.*?)\)"
        matches = re.finditer(regex_pattern, md_content)

        for match in matches:
            absolute_path = match.group("path")

            if cls.is_local_image(absolute_path, img_folder):
                relative_path = os.path.relpath(absolute_path, os.path.dirname(md_path))
                md_content = md_content.replace(absolute_path, relative_path)

        with open(md_path, 'w', encoding='utf-8') as md_file:
            md_file.write(md_content)

    @classmethod
    def is_local_image(cls, path: str, img_folder: str) -> bool:
        """
        Check if an image path is local (within the specified image folder).

        Args:
        - path (str): Image path.
        - img_folder (str): Path to the image folder.

        Returns:
        - bool: True if the image path is local; False otherwise.
        """
        return os.path.isabs(path) and path.startswith(img_folder)
    

    @classmethod
    def convert_all_markdown_files_recursive(cls, folder_path: str) -> None:
        for root, dirs, files in os.walk(folder_path):
            for file_name in files:
                if file_name.endswith(".md"):
                    md_path = os.path.join(root, file_name)
                    cls.convert_absolute_to_relative(md_path, folder_path)

            for sub_dir in dirs:
                cls.convert_all_markdown_files_recursive(os.path.join(root, sub_dir))

def md_recursion(cur_path: str) -> None:
    """
    Recursively convert absolute image paths to relative paths in all Markdown files within a folder.

    Args:
    - folder_path (str): Path to the folder containing Markdown files.
    """
    filenames = os.listdir(cur_path)
    for filename in filenames:
        folder_path = os.path.join(cur_path, filename)
        if os.path.isdir(folder_path):
            md_recursion(folder_path)
        elif filename.strip() == 'out':
            continue
    MdImageLocal(md_path=cur_path, log=args.log, modify_source=args.modify_source).run()


if __name__ == "__main__":
    time0 = time.time()
    args = parse_args()        
    # Create new log file
    logging.basicConfig(filename=os.path.join(args.md_path, 'MD-Local.log') if args.log else None,
                        filemode="w",level=logging.INFO if args.log else logging.WARNING,format='%(asctime)s: %(message)s')
    logging.warning("Starting...")
    # Check args
    if not args.md_path:
        logging.warning("Please add md_path arg and rerun this file...")
        sys.exit(1)
    if args.relative:
        logging.warning("Converting to relative path...")
        MdImageLocal.convert_all_markdown_files_recursive(args.md_path)
        sys.exit(0)
    # Set coroutine_num
    COROUTINE_NUM=args.coroutine_num
    logging.warning(f'Using {COROUTINE_NUM} coroutine...')
    md_recursion(args.md_path)
    logging.warning(f"Time consumed:{time.time() - time0}")
