from flask import Flask, render_template, send_file
from htmlmin.main import minify
import os


PREFIX_MANGA = "/m/"
PREFIX_CHAPTER = "/c/"
PREFIX_IMAGE = "/i/"


def beautify_manga_title(title):
    title = title.replace("-", " ")
    title = title.title()
    return title


def check_param(manga, chapter="*", img="*"):
    path = os.path.join(os.getcwd(), "manga")
    chapters = dict()

    # Check if manga exist
    path = os.path.join(path, manga)
    if not os.path.exists(path):
        return "", "Manga Not Found :(", chapters

    if chapter == "*" or img == "*":
        chapters_tmp = os.listdir(path)
        if chapter != "*":
            chapters_tmp.sort()
        else:
            chapters_tmp.sort(reverse=True)

        for chapter_tmp in chapters_tmp:
            key = PREFIX_CHAPTER + manga + "/" + chapter_tmp
            text = beautify_manga_title(manga) + " " + str(int(chapter_tmp))

            chapter_data = dict()
            chapter_data["text"] = text

            if chapter != "*":
                chapter_data["selected"] = ""
                if chapter_tmp == chapter:
                    chapter_data["selected"] = "selected"

            chapters[key] = chapter_data

    if chapter == "*":
        return path, "", chapters

    # Check if chapter exist
    path = os.path.join(path, chapter)
    if not os.path.exists(path):
        return "", "Chapter Not Found :(", chapters

    if img == "*":
        return path, "", chapters

    path = os.path.join(path, img)
    if not os.path.exists(path):
        return "", "Image Not Found :("

    return path, "", chapters


app = Flask(__name__)


@app.after_request
def response_minify(response):
    if response.content_type == u'text/html; charset=utf-8':
        response.set_data(
            minify(response.get_data(as_text=True))
        )

        return response
    return response


@app.route("/")
def home_page():
    path = os.path.join(os.getcwd(), "manga")
    manga_list_tmp = os.listdir(path)
    manga_list_tmp.sort()

    manga_list = dict()
    for m in manga_list_tmp:
        if m[0] == ".":
            continue
        manga_list[m] = beautify_manga_title(m)

    return render_template("manga_list.html", manga=manga_list)


@app.route(PREFIX_MANGA + "<manga>")
def manga_page(manga):
    _, error, chapters = check_param(manga)

    if error != "":
        return error

    return render_template("manga_chapter_list.html", manga=beautify_manga_title(manga), chapters=chapters)


@app.route(PREFIX_CHAPTER + "<manga>/<chapter>")
def chapter_page(manga, chapter):
    path, error, chapters = check_param(manga, chapter)
    if error != "":
        return error

    images = os.listdir(path)
    images.sort()

    list_images = list()
    for i in images:
        url_image = PREFIX_IMAGE + manga + "/" + chapter + "/"
        tmp_path = url_image + i
        list_images.append(tmp_path)

    chapter_int = int(chapter)
    next_chapter = chapter_int + 1
    prev_chapter = chapter_int - 1
    if prev_chapter < 1:
        prev_chapter = 1

    nav = dict()
    nav["next"] = PREFIX_CHAPTER + manga + "/" + f"{next_chapter:04}"
    nav["prev"] = PREFIX_CHAPTER + manga + "/" + f"{prev_chapter:04}"
    nav["chapters"] = chapters

    manga_d = dict()
    manga_d["raw"] = manga
    manga_d["readable"] = beautify_manga_title(manga)

    chapter_d = dict()
    chapter_d["raw"] = chapter
    chapter_d["readable"] = str(int(chapter))

    return render_template("manga_read.html", manga=manga_d, chapter=chapter_d, data=list_images, navigation=nav)


@app.route(PREFIX_IMAGE + "<manga>/<chapter>/<img>")
def get_image(manga, chapter, img):
    path, error, _ = check_param(manga, chapter, img)
    if error != "":
        return error

    mime_type = "image/" + str(path.split(".")[-1])
    return send_file(path, mimetype=mime_type)


if __name__ == '__main__':
    app.run()
