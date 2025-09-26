import shutil
import os.path
import markdown
from ebooklib import epub
from pathlib import Path

# 每个章节单独保存为 HTML 文件
def md_to_html(md_content):
    # 转换为 HTML
    html_content = markdown.markdown(md_content,
                                      extensions=["mdx_math"],
                                      extension_configs={
                                          "mdx_math": {
                                              "enable_dollar_delimiter": True,
                                          }
                                      })
    # # 保存为 HTML 文件
    # html_file = md_file.replace('.md', '.html')
    return html_content

# html 转换为 epub 章节
def html_to_epub_chapter(title, html_content):
    # print(html_content)
    chapter = epub.EpubHtml(title=title, lang="cn", file_name=title+'.xhtml')
    chapter.content = html_content
    return chapter


def save_md_to_epub(md_file, epub_file, title):
    # 使用 # 分章节
    # 读取 Markdown 文件内容
    content = open(md_file, 'r', encoding='utf-8').readlines()
    all_chapters = []
    chapter_title = ""
    chapter =[]

    for i in range(len(content)):
        if content[i].startswith('#'):
            # 保存上一章节
            if chapter_title!="" or len(chapter)>0:  # 修复条件判断
                all_titles = [c[0] for c in all_chapters]
                if chapter_title in all_titles:
                    chapter_title = chapter_title + str(all_titles.count(chapter_title))
                all_chapters.append((chapter_title, chapter))
            chapter_title = content[i].strip('#').strip()
            # 创建章节对象
            chapter = [content[i]]
        else:
            chapter.append(content[i])

    # 保存最后一章节
    if chapter_title!="" or len(chapter)>0:  # 修复条件判断
        all_titles = [c[0] for c in all_chapters]
        if chapter_title in all_titles:
            chapter_title = chapter_title + str(all_titles.count(chapter_title))
        all_chapters.append((chapter_title, chapter))

    # 转换为 epub 章节
    book = epub.EpubBook()
    book.set_identifier('id123456789')
    book.set_title(title)
    book.set_language('zh')
    book.spine = ["nav"]

    # all_chapters = all_chapters[4:5]
    chapters = []


    for chapter_title, chapter in all_chapters:
        # 转换为 HTML
        html_content = md_to_html(''.join(chapter))
        # 保存为 HTML 文件
        html_file = md_file.replace('.md', '.html')
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        # 转换为 epub 章节
        epub_chapter = html_to_epub_chapter(chapter_title, html_content)
        # 添加到 epub 书籍中
        book.add_item(epub_chapter)
        # book.toc.append((epub.Section(chapter_title), epub_chapter))
        if chapter_title!="":
            # print(chapter_title, epub_chapter.file_name, chapter_title)
            book.toc.append(epub.Link(epub_chapter.file_name, chapter_title, chapter_title))
        chapters.append(epub_chapter)

    # 添加图片
    # 获取图片文件夹
    img_folder = os.path.dirname(md_file)
    # print("img_folder:", img_folder)
    img_folder = os.path.join(img_folder, 'images')
    # 遍历所有图片文件
    if os.path.exists(img_folder):  # 添加检查确保图片文件夹存在
        for img_file in os.listdir(img_folder):
            img_path = os.path.join(img_folder, img_file)
            # print("img_file:", img_file)
            # print("img_path:", img_path)
            # 读取图片内容
            with open(img_path, 'rb') as f:
                img_content = f.read()
            # 添加到 epub 书籍中
            img_file_path = os.path.join('images', img_file)

            book.add_item(epub.EpubItem(
                uid="img"+img_file,
                file_name=img_file_path, media_type='image/jpeg', content=img_content))

    # 保存为 epub 文件
    book.spine = ["nav"] + chapters
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # 保存为 epub 文件
    style = "BODY {color: black;}"  # 修改默认颜色为黑色
    nav_css = epub.EpubItem(
        uid="style_nav",
        file_name="style/nav.css",
        media_type="text/css",
        content=style,
    )

    # add CSS file
    book.add_item(nav_css)
    
    # 确保至少有一个章节被添加
    if len(chapters) > 0:
        epub.write_epub(epub_file, book, {})
    else:
        print("警告: 没有章节内容可以添加到EPUB文件中")
    
def sort_md_files(md_files):
    def key_func(x):
        name = x.stem
        num = name.split('-')[1]
        return int(num)
    md_files.sort(key=key_func)
    return md_files


def merge_md(md_files, output_dir, title):
    p = Path(md_files)
    md_files = list(p.glob("*/auto/*.md"))
    md_files = sort_md_files(md_files)
    md_images_dir = os.path.join(output_dir, 'images')
    # 确保md_images_dir存在, 如果存在 先删除目录内的文件
    if os.path.exists(md_images_dir):
        shutil.rmtree(md_images_dir)
    # 确保output_dir存在
    os.makedirs(output_dir, exist_ok=True)
    # 创建md_images_dir目录
    os.makedirs(md_images_dir, exist_ok=True)
    with open(os.path.join(output_dir, title + ".md"), 'w', encoding='utf-8') as f:
        for md_file in md_files:
            with open(md_file, 'r', encoding='utf-8') as f2:
                f.write(f2.read())
                f.write("\n")
            # 拷贝md文件夹内images文件夹 到output_dir
            img_folder = os.path.join(md_files[0].parent, 'images')
            if os.path.exists(img_folder):  # 添加检查确保图片文件夹存在，逐个拷贝文件到md_images_dir
                for img_file in os.listdir(img_folder):
                    img_path = os.path.join(img_folder, img_file)
                    shutil.copy(img_path, md_images_dir)


if __name__ == '__main__':
    input_dir = r"./md_output"
    epub_dir = r"./epubs"
    title = "demo"
    # 合并所有文件，保存到md_file/{title}.md
    merge_md(input_dir, "md_file", title)
    save_md_to_epub(os.path.join("md_file", title + ".md"), os.path.join(epub_dir, title + ".epub"), title)
