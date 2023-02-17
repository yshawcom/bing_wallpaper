# -*- coding: utf-8 -*-

import datetime
import os
import urllib.request

import requests
from bs4 import BeautifulSoup

DATE = datetime.date.today().strftime('%Y%m%d')
WALLPAPER_PATH = 'C:/Users/yshaw/Desktop/wallpaper/'
HEXO_CWD = 'D:/ProgramData/hexo'
BING_URL = 'https://cn.bing.com/'


def get_image_url(bs):
    """
    获取图片URL
    """
    # url_str = soup.find('div', class_='hp_top_cover')['style']
    url_str = bs.find('link', id='preloadBg')['href']

    begin = url_str.index('https://')
    end = url_str.index('.jpg', begin) + 4

    return url_str[begin: end].replace('1920x1080', 'UHD')


def get_image_name(bs):
    """
    获取图片名称
    """
    return bs.find('a', class_='title').string


def download_file(url, name):
    """
    下载文件
    """
    filename = '%s%s_%s.jpg' % (WALLPAPER_PATH, DATE, name)
    urllib.request.urlretrieve(url, filename=filename)


def handle_hexo(image_url, image_name):
    """
    hexo博客
    """
    cwd_cmd = ' --cwd ' + HEXO_CWD
    title = 'bing每日一图-' + DATE
    md_file_path = '%s/source/_posts/%s.md' % (HEXO_CWD, title)

    # 新建博文
    cmd_new = 'hexo new "%s" --replace' % title
    os.system(cmd_new + cwd_cmd)

    # 读取md现有内容
    md_file = open(md_file_path, mode='r', encoding='UTF-8')
    front_matter = md_file.readlines()
    # 添加标签
    front_matter[4] = front_matter[4].replace('tags:', 'tags: bing每日一图')

    md_file = open(md_file_path, mode='w+', encoding='UTF-8')
    # 写入现有内容
    for line in front_matter:
        if line.startswith('tags:'):
            # 添加标签和封面图
            md_file.writelines('tags: \n')
            md_file.writelines('index_img: ' + image_url + '\n')
            md_file.writelines('banner_img: ' + image_url + '\n')
        elif line.startswith('category:'):
            # 分类
            md_file.writelines('category:\n')
            md_file.writelines('    - 爬虫\n')
            md_file.writelines('    - 每日一图\n')
        else:
            md_file.writelines(line)
    # 写入文章
    md_file.writelines('\n')
    md_file.writelines(image_name + '\n')
    md_file.writelines('\n')
    md_file.writelines('<!-- more -->\n')
    md_file.writelines('\n')
    md_file.writelines('![' + image_name + '](' + image_url + ')\n')
    md_file.close()

    # 生成html，部署到git
    cmd_generate = 'hexo generate --deploy'
    os.system(cmd_generate + cwd_cmd)


if __name__ == '__main__':
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/93.0.4577.63 Safari/537.36 '
    }

    resp = requests.get(BING_URL, headers=headers)
    soup = BeautifulSoup(resp.text, 'lxml')

    # 获取图片URL
    imageUrl = get_image_url(soup)
    print(imageUrl)

    # 获取图片名称
    imageName = get_image_name(soup)
    print(imageName)

    # 下载图片
    download_file(imageUrl, imageName)

    # hexo博客
    handle_hexo(imageUrl, imageName)
