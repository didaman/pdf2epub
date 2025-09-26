# 介绍
将pdf转换成epub格式。

基于MinerU 工具，[MinerU](https://github.com/opendatalab/MinerU)。

# 准备环境
clone当前项目到本地。
```
git clone https://github.com/didaman/pdf2epub.git
```

安装MinerU 工具。具体参考官方说明。


# 使用方法

将待转换的pdf文件放入pdfs目录下。先执行mineru转换脚本
```
python3 pdf2md.py
```
解析结果会保存到md_output目录下的各个子目录下。


之后用md2epub.py 脚本首先将markdown合并，保存到md_file目录下，再转换为epub格式。
```
python3 md2epub.py
```
转换后的epub文件会保存到epubs目录下。