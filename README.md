# Markdown-ImageLocalize
[中文README](./README_ZH.md) 

This code is adapted from [Img_link_to_local_markdown](https://github.com/xZaR3y4p/Img_link_to_local_markdown)

This is a python script that scans all the markdown files of a folder looking for images links, 
and substitutes the urls of the markdown files for local file names, 
and download the images.

# Why?🛠️
Offline markdown files are a reliable way to store and organize information.
When copying from the web the text is copied directly, but images are copied as links.
If the link expires in the future, or you are offline, you lose the information.
It would be great to have every picture added as a link downloaded to local storage.

# Features⭐
+ Support both `<img>` and `![]()` labels.
+ Add more options to custom the behaviors(e.g. whether to modify source markdown files).
+ Download images in Async mode, which performs well to decrease exec time:

    |  vanilla code   | async code  |
    |  ----  | ----  |
    | 28.420s  | 5.236s |
+ Support loop traversal of markdown files.


# Usage🚀
1. Install Python on your computer.
2. Clone this Repo `git clone https://github.com/YellowAndGreen/Md-ImgLocalize.git`.
3. Install aiohttp `pip install aiohttp` .
4. Change to the Repo's directory and run `python main.py --md_path=[md_path]`:
    + specify `md_path` as your markdown files directory
    + use `--log` to save log file
    + use `--modify_source` to modify source markdown files directly, this option create image folders under markdown file directory



## What image extensions are searched?
Png, jpg, jpeg, gif, bmp, and svg, because these are the ones Obsidian currently supports. 

Feel free to add more if you need, editing this portion of the regex  pattern "png|jpg|jpeg|gif|bmp|svg".

## Feel free to submit a Pull Request or Issues😃!