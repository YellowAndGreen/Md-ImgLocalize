# utils.py
import os
import shutil
import requests

def create_folder(folder: str) -> None:
    """
    Create a folder if it doesn't exist.

    Parameters:
    - folder (str): The path of the folder to be created.
    """
    if not os.path.exists(folder):
        os.mkdir(folder)


def delete_folder(folder):
    """递归地删除目录及其所有内容"""
    if os.path.exists(folder):
        shutil.rmtree(folder)


def is_valid_url(url: str) -> bool:
    """
    Check the validity of a URL.

    Parameters:
    - url (str): The URL to be checked.

    Returns:
    - bool: True if the URL is valid; False otherwise.
    """
    try:
        response = requests.head(url)
        return response.status_code == 200
    except requests.RequestException:
        return False


def write_file(folder_path: str, file_name: str, file_data: str) -> None:
    """
    Write data to a file.

    Parameters:
    - folder_path (str): The path of the folder where the file will be written.
    - file_name (str): The name of the file.
    - file_data (str): The data to be written to the file.
    """
    with open(os.path.join(folder_path, file_name), "w", encoding="utf-8") as file:
        file.write(file_data)


def count_test_cases(md_file_path: str):
    """计算Markdown文件中图片链接的数量"""
    with open(md_file_path, "r") as f:
        content = f.read()
    return content.count("![")
