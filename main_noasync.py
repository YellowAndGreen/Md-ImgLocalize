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

# TODO: 使用Async来加速
import argparse
import os
import re
import random
import string
import urllib.request
import logging
import time

def create_folder(folder="out"):
    if not os.path.exists(folder):
        os.mkdir(folder)


def download_images(url_dict, folder_path, user_agent):
    """
    Download the images from the links obtained from the markdown files to the "destination folder"
    The user-agent can be specified in order to circumvent some simple potential connection block
    """
    for url, name in url_dict.items():
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', user_agent)]
        urllib.request.install_opener(opener)
        save_name = folder_path + "\\" + name
        try:
            urllib.request.urlretrieve(url, save_name)
        except Exception as e:
            logging.exception(f"Error when downloading {url}")
        # time.sleep(random.randint(0, 2))


def open_and_read(filename):
    """
    Open and reads the file received and returns the content
    """
    url_dict = {}
    try:
        with open(os.path.join(os.getcwd(), filename), "r", encoding="utf-8") as current_opened_file:
            print(f"\nOpened file: {filename}")
            logging.info(f"Opened file: {filename}\n")
            return current_opened_file.read()
    except Exception as e:
        logging.exception(f"Error when opening file {filename}")


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
        for url in re.findall(regex, file_data):
            random_name = "".join([random.choice(string.hexdigits) for i in range(10)])
            if url[0] not in url_dict.keys():
                url_dict[url[0]] = random_name + url[1]
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
        self.regex = r"(?:\(|\[)(?P<url>(?:https?\:(?:\/\/)?)(?:\w|\-|\_|\.|\?|\/)+?\/(?P<end>(?:\w|\-|\_)+\.(?:png|jpg|jpeg|gif|bmp|svg)))(?:\)|\])"
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
                # log_file_creator.write(f"{filename} ignored (not '.md')\n")
                logging.info(f"Skipped file: {filename}\n")
                print(f"Skipped file: {filename}")
                continue
            # Open and read each file
            file_data = open_and_read(filename)
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
        download_images(all_img_dict, self.out_folder_path, self.user_agent)
        print("\n\n\nfiles and the downloaded images on the folder:")
        print(f"{self.out_folder_path}")


if __name__ == "__main__":
    time0 = time.time()
    print("\n\n\nStarting..\n")
    # Initialize the convert class with target markdown files directory from args
    args = parse_args()
    localizer = MdImageLocal(md_path=args.md_path, log=args.log, modify_source=args.modify_source)
    localizer.run()
    print(f"time consumed:{time.time()-time0}")
    print("\nPress enter to close.")
    input()
