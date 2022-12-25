# Markdown图片本地化
根据[Img_link_to_local_markdown](https://github.com/xZaR3y4p/Img_link_to_local_markdown)
修改🛠️

> 本代码将扫描给定文件夹下所有的markdown文件，对于每个markdown文件搜寻在线图片链接，下载对应的图片并替换文本中的链接为本地图片路径。

## 主要功能⭐
+ 支持`<img>`和`![]()`两种标签以及更多格式
+ 添加了选项功能，能够自由定制程序的操作（例如是否修改md源文件）
+ 以Python Async模式下载图片，可大大减少运行时间：

    |  普通模式   | 协程模式  |
    |  ----  | ----  |
    | 28.420s  | 5.236s |
+ 下载图片将根据不同markdown文件名创建新的文件夹储存
+ 支持markdown文件的递归遍历搜索


## 使用方法🚀
1. 安装Python
2. 在[Github](https://github.com/YellowAndGreen/Md-ImgLocalize)
直接下载或者克隆本项目 `git clone https://github.com/YellowAndGreen/Md-ImgLocalize.git`
3. 安装aiohttp `pip install aiohttp`
4. 切换到本项目路径并运行`python main.py --md_path=[markdown文件目录]`，其中的额外参数有：
    + 指定 `--md_path` 作为源markdown文件目录
    + 添加 `--log` 来保存运行日志
    + 添加 `--modify_source`来直接修改源文件

## 支持的图片格式
支持png, jpg, jpeg, gif, bmp, and svg，可修改正则表达式"png|jpg|jpeg|gif|bmp|svg"来增加新的图片格式。

## 如果有任何疑问或者对本项目的改进，欢迎提供Issue或者Pull Request😃！


