#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Apr 4 2021
@author: MohammadHossein Salari
@email: mohammad.hossein.salari@gmail.com
"""

import os
import shutil
from telethon import TelegramClient
from config import *
from download_utils import *

base_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "data")
chapters_path = os.path.join(base_path, "chapters_url")
session_path = os.path.join(base_path, "manga.session")

client = TelegramClient(session_path, api_id, api_hash)


@retry(delay=15, backoff=2, tries=5)
def download_mangas(manga_rss_url):
    manga_name = os.path.basename(manga_rss_url)[:-4]
    manga_chapters_path = os.path.join(base_path, "chapters_url", f"{manga_name}.txt")
    chapters_url_on_disk = []
    if os.path.exists(manga_chapters_path):
        print(f'Loadding list of "{manga_name}" chapters from disk')
        with open(manga_chapters_path, "r") as f:
            chapters_url_on_disk = [line.rstrip("\n") for line in f]

    print(f'Getting list of "{manga_name}" chapters from mangasee123.com')
    chapters_url = [chapter["link"] for chapter in get_list_of_chapters(manga_rss_url)]

    if chapters_url_on_disk == []:
        new_chapters = [chapters_url[0]]
    else:
        new_chapters = set(chapters_url) - set(chapters_url_on_disk)
    if new_chapters:
        for chapter_url in new_chapters:
            chapter_url = chapter_url.replace("-page-1.html", "")

            print(f"Gettin list of {os.path.basename(chapter_url)} images")
            images_url = get_url_of_images(chapter_url)

            print(f"Downloading {os.path.basename(chapter_url)} images")
            url_and_images = download_images(images_url)

            save_path = os.path.join(base_path, "temp", os.path.basename(chapter_url))
            print(f"Saveing chapter to {save_path}")
            save_manga(save_path, url_and_images, save_png=False, save_pdf=True)

            print(f"Download {os.path.basename(chapter_url)} Finished!")
    else:
        print("Notting new to download!")

    with open(manga_chapters_path, "w") as f:
        [f.write(chapter + "\n") for chapter in chapters_url]
    print("-" * 50)


async def main():

    mangas_rss_url_path = os.path.join(
        os.path.dirname(os.path.realpath(__file__)), "mangas_rss_url.txt"
    )
    if not os.path.exists(mangas_rss_url_path):
        raise Exception(f"{mangas_rss_url_path} doesn't exist!")

    with open(mangas_rss_url_path, "r") as f:
        mangas_rss_url = [line.rstrip("\n") for line in f]

    print("Check mangas for new chapter")
    print("#" * 50)
    for manga_rss_url in mangas_rss_url:
        download_mangas(manga_rss_url)
    print("#" * 50)
    print("Downloading finished!")

    mangas_pdf = []
    for dirpath, dirnames, filenames in os.walk(temp_path):
        for filename in [f for f in filenames if f.endswith(".pdf")]:
            mangas_pdf.append(os.path.join(dirpath, filename))

    if mangas_pdf:
        print("Sending PDF to my telegram account")
    for pdf in tqdm(mangas_pdf):

        await client.send_message(
            "mh_salari", f"{os.path.basename(pdf)[:-4].replace('-',' ')}"
        )

        await client.send_file("mh_salari", pdf)


if __name__ == "__main__":

    temp_path = os.path.join(base_path, "temp")

    if not os.path.exists(temp_path):
        os.makedirs(temp_path)

    with client:
        client.loop.run_until_complete(main())

    shutil.rmtree(temp_path, ignore_errors=True)

