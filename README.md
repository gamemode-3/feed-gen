# feed generator!

a simple rss feed generator made in python. supports uploading to neocities.

## requirements

[python](https://www.python.org/), obviously. packages:
- [markdown2](https://pypi.org/project/markdown2/)
- [bs4](https://pypi.org/project/beautifulsoup4/) (beautiful soup 4)

install all packages with `pip`:
```sh
pip install markdown2 bs4
```

OR install everything with `apt` (ubuntu / debian linux):
```
sudo apt install python3 python3-markdown2 python3-bs4
```

### optional


## how to use

you need to download the code which you can do from the green "`<> Code`" button, and then just "`Download ZIP`" at the bottom. if you're more techy you can just clone the repo of course.

### 1. change author info
open `gen_feed.py` in any text editor (e.g. notepad) and put your name, website, etc. in there. if you don't understand something, just leave it.

### 2. create a post
create a new markdown (`.md`) file in the `posts` folder. [here](https://www.tomarkdown.org/guides/markdown-tutorial-for-beginners)'s a quick intro to markdown if you're not familiar. [obsidian](https://obsidian.md/) is a great way to edit and organise markdown.

this version supports code blocks, metadata, strikethrough, tables and spoilers on top of the universal markdown functionality.

you can't put posts in subfolders (yet). only in the posts folder itself.

### 3. generate the feed!
alright, now just run `gen_feed.py` like this:

```
python3 gen_feed.py
python gen_feed.py
```

if that doesn't work replace `gen_feed.py` with the full path, e.g. `/home/me/Dowloads/gen_feed.py` or `C:\Downloads\gen_feed.py`. put that in `""` if there are spaces in the path.

it will prompt you for a neocities API key. if you don't want to upload to neocities, just press enter

you should get a `feed.xml` file. this is your rss feed.
