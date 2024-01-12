# Markdown图片本地化
根据[Img_link_to_local_markdown](https://github.com/xZaR3y4p/Img_link_to_local_markdown)
修改🛠️

> 本代码将扫描给定文件夹下所有的markdown文件，对于每个markdown文件搜寻在线图片链接，下载对应的图片并替换文本中的链接为本地图片路径。

## 主要功能⭐
+ 支持`<img>`和`![]()`两种标签以及更多格式
+ 添加了选项功能，能够自由定制程序的操作（例如是否修改md源文件）
+ 以Python **Async**模式下载图片，可大大减少运行时间：

    |  普通模式   | 协程模式  |
    |  ----  | ----  |
    | 28.420s  | 5.236s |
+ 下载图片将根据不同markdown文件名创建新的文件夹储存
+ 支持markdown文件的**递归遍历**搜索
+ 保存图片和链接之间的字典关系，能够使该程序**自动检查并下载**未下载的图片，也可重新运行该程序以只检查并下载未下载的图片。
+ 转换所有的绝对路径文件到相对路径文件
+ 支持自定义添加测试样例以测试markdown文件是否能够正确转换


## 使用方法🚀
1. 安装Python
2. 在[Github](https://github.com/YellowAndGreen/Md-ImgLocalize)
直接下载或者克隆本项目 `git clone https://github.com/YellowAndGreen/Md-ImgLocalize.git`
3. 安装aiohttp： `pip install aiohttp`
4. 切换到本项目路径并运行`python main.py --md_path=[markdown文件目录]`，其中的额外参数有：
    + 指定 `--md_path` 作为源markdown文件目录
    + 添加 `--log` 来保存完整运行日志，如果使用此参数则屏幕上不会有输出
    + 添加 `--modify_source`来直接修改源文件
    + 使用`--coroutine_num`来指定协程数量，如果不需要使用协程，可设置为1
    + 使用`--del_dict`来删除`all_img_dict.json`
    + 使用`--relative`来转换所有的绝对路径到相对路径，使用此选项则不会进行图片下载
5. 使用测试功能则需要运行`python main.py --test`。所有的测试样例均保存在`test_case`文件夹中，添加单个图片样例请直接修改`test_single/test_single.md`文件，添加一整个测试文件夹请添加到`test_folder`下


## TODO📃

- [x] 协程功能
- [x] 循环遍历
- [x] 重新下载失败图片
- [x] 删除生成的dict
- [x] 绝对路径转换为相对路径
- [ ] 网页版功能
- [x] 添加测试样例

## 如果有任何疑问或者对本项目的改进，欢迎提供Issue或者Pull Request😃！

