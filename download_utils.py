#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 4 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com

@sources:
         - https://codeburst.io/building-an-rss-feed-scraper-with-python-73715ca06e1f
         - https://stackoverflow.com/questions/7391945/how-do-i-read-image-data-from-a-url-in-python
         - https://stackoverflow.com/questions/27327513/create-pdf-from-a-list-of-images
"""
import requests
from bs4 import BeautifulSoup

import time
from selenium import webdriver
from selenium.webdriver.firefox.options import Options

import re
import os
from PIL import Image
from tqdm import tqdm
from retry import retry


def get_list_of_chapters(manga_rss_url):

    chapters_list = []

    r = requests.get(manga_rss_url)
    if r.status_code != 200:
        raise Exception(f"request error{r.status_code}")

    soup = BeautifulSoup(r.content, features="xml")

    chapters = soup.findAll("item")

    for a in chapters:
        title = a.find("title").text
        link = a.find("link").text
        published_date = a.find("pubDate").text
        chapter = {"title": title, "link": link, "published_date": published_date}
        chapters_list.append(chapter)
    return chapters_list


def get_url_of_images(chapter_url):
    options = Options()
    options.headless = True
    driver = webdriver.Firefox(options=options)

    driver.get(chapter_url)

    timeout = 60
    for i in range(timeout):
        if "{" in driver.title:
            time.sleep(1)
        else:
            break
    else:
        raise Exception("timeout")

    images_url = re.findall(
        r"(?:http\:|https\:)?\/\/.*?manga.*?\.(?:png|jpg)", driver.page_source
    )
    driver.quit()

    images_url = list(set(images_url))
    images_url.sort()

    return images_url


def download_images(images_url):
    images = []
    for url in tqdm(images_url):
        image = Image.open(requests.get(url, stream=True).raw)
        images.append([url, image])
    return images


def save_manga(save_path, url_and_images, save_png=True, save_pdf=True):
    if not os.path.exists(save_path):
        os.makedirs(save_path)

    if save_png:
        for url, image in url_and_images:
            image.save(os.path.join(save_path, os.path.basename(url)))
    if save_pdf:
        images = [image for _, image in url_and_images]
        images[0].save(
            os.path.join(save_path, f"{os.path.basename(save_path)}.pdf"),
            "PDF",
            resolution=100.0,
            save_all=True,
            append_images=images[1:],
        )
