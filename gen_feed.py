from pathlib import Path


#== main settings ==#

FEED_NAME = "mai.loeckchen"
FEED_DESC = "what i'm up to"
FEED_IMAGE = "https://mailoeckchen.neocities.org/favicon.ico"
FEED_URL = "https://mailoeckchen.neocities.org/up-to/feed.xml"
AUTHOR_NAME = "mai.loeckchen"
AUTHOR_EMAIL = "mailoeckchen@proton.me"
POST_URL_PATTERN = "https://mailoeckchen.neocities.org/up-to/view?post={slug}"

UPLOAD_TO_NEOCITIES = True
NEOCITIES_UPLOAD_PATH = "up-to/feed.xml"
NEOCITIES_IMAGE_UPLOAD_PATH = "up-to/feed-media/"


COPYRIGHT = AUTHOR_NAME
NEOCITIES_USERNAME = "mailoeckchen"
LANGUAGE = "en"


POST_DIR = Path("./posts")
OUTPUT_FILE = Path("./feed.xml")

#===================#

def gen_post_url(index: int, slug: str):
    return POST_URL_PATTERN.replace("{id}", str(index)).replace("{slug}", slug)


import os
from datetime import datetime, timezone
import markdown2
from bs4 import BeautifulSoup
import getpass

upload_to_neocities = UPLOAD_TO_NEOCITIES

def format_time(t: datetime):
    return t.strftime("%a, %d %b %Y %H:%M:%S GMT")


def gen_post(text: str, index: int, modified: datetime) -> tuple[str, list[tuple[str, str]]]:


    md_html = markdown2.markdown(text, extras=["fenced-code-blocks", "header-ids", "metadata", "strike", "tables", "tg-spoiler"])

    metadata = md_html.metadata

    soup = BeautifulSoup(md_html, "html.parser")

    images_to_upload = []
    all_img = soup.find_all("img")
    for img in all_img:
        src = img["src"]
        if src is None:
            continue
        src = str(src)
        if src.startswith("http"):
            continue
        local_path = Path(POST_DIR) / Path(src)
        if not local_path.exists() or not local_path.is_file():
            print(f"WARNING: '{local_path}' is not a file")
            continue
        
        rel_path = local_path.relative_to(Path(POST_DIR))
        neocities_path = Path(NEOCITIES_IMAGE_UPLOAD_PATH) / rel_path
        upload_pair = (str(local_path), str(neocities_path))
        images_to_upload.append(upload_pair)
        if upload_to_neocities:
            img["src"] = f"https://{NEOCITIES_USERNAME}.neocities.org/" + str(neocities_path)

    title_o = soup.find("h1")
    title = ""
    if title_o != None:
        title = title_o.text
        title_o.decompose()
    slug = title.lower().replace(" ", "-")
    
    for li in soup.find_all("li"):
        span = soup.new_tag("span")
        for child in li.contents:
            span.append(child)
        li.clear()
        li.append(span)

    desc_o = soup.find("p")
    desc = ""
    if desc_o != None:
        desc = desc_o.text

    img_o = soup.find("img")
    img = None
    if img_o != None:
        img = img_o["src"]

    img_html = ""
    if img != None:
        img_html = f'<enclosure url="{img}" length="0" type="image/jpeg"/>'

    body_html = str(soup)

    post_url = gen_post_url(index, slug)

    post = f'''
        <item slug="{slug}">
            <title><![CDATA[{title}]]></title>
            <description><![CDATA[{desc}]]></description>
            <link>
                {post_url}
            </link>
            <guid isPermaLink="false">
                {post_url}
            </guid>
            <dc:creator><![CDATA[{AUTHOR_NAME}]]></dc:creator>
            <pubDate>{format_time(modified)}</pubDate>
            {img_html}
            <content:encoded>
                <![CDATA[{body_html}]]>
            </content:encoded>
        </item>
    '''

    return (post, images_to_upload)


def get_all_posts() -> tuple[list[str], list[tuple[str, str]]]:
    files = []

    for file in os.scandir(POST_DIR):
        if file.is_file() and file.name.endswith(".md"):
            mtime = os.path.getmtime(file)
            files.append((file, mtime))

    posts = []
    images = []

    
    files.sort(key=lambda x: x[1])

    for i, (file, mtime) in enumerate(files):
        with open(file) as f:
            post, image_list = gen_post(f.read(), i, datetime.fromtimestamp(mtime))
            posts.append(post)
            for img in image_list:
                images.append(img) 
    

    return posts, images



if __name__ == "__main__":
    if upload_to_neocities:
        try:
            import neocities
            try:
                key = os.environ["NEOCITIES_API_KEY"]
            except:
                key=getpass.getpass("neocities API key: ")
                if key.strip() in ["no", "n", ""]:
                    upload_to_neocities = False
        except ImportError as e:
            if e.name == "neocities":
                print("python-neocities is not installed. not uploading to neocities. install from: https://github.com/neocities/python-neocities")
                upload_to_neocities = False
            else:
                raise e

    generation_time = format_time(datetime.now(timezone.utc))

    head = f'''<?xml version="1.0" encoding="UTF-8"?>
<rss xmlns:dc="http://purl.org/dc/elements/1.1/"
    xmlns:content="http://purl.org/rss/1.0/modules/content/"
    xmlns:atom="http://www.w3.org/2005/Atom" version="2.0"
    xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd"
    xmlns:googleplay="http://www.google.com/schemas/play-podcasts/1.0">
    <channel>
        <title><![CDATA[{FEED_NAME}]]></title>
        <description>
        <![CDATA[{FEED_DESC}]]>
        </description>
        <link>{FEED_URL}</link>
        <image>
        <url>
        {FEED_IMAGE}
        </url>
        <title>{FEED_NAME}</title>
        <link>{FEED_URL}</link>
        </image>
        
        <generator>gamemode-3-feed-gen</generator>
        <lastBuildDate>{generation_time}</lastBuildDate>
        
        <atom:link href="{FEED_URL}" 
                rel="self" 
                type="application/rss+xml"/>
        <copyright><![CDATA[{COPYRIGHT}]]></copyright>
        <language><![CDATA[{LANGUAGE}]]></language>
        <webMaster><![CDATA[{AUTHOR_EMAIL}]]></webMaster>
        
        <itunes:owner>
            <itunes:email><![CDATA[{AUTHOR_EMAIL}]]></itunes:email>
            <itunes:name><![CDATA[{AUTHOR_NAME}]]></itunes:name>
        </itunes:owner>
        <itunes:author><![CDATA[{AUTHOR_NAME}]]></itunes:author>
        <itunes:block>Yes</itunes:block>
        
        <googleplay:owner><![CDATA[{AUTHOR_EMAIL}]]></googleplay:owner>
        <googleplay:email><![CDATA[{AUTHOR_EMAIL}]]></googleplay:email>
        <googleplay:author><![CDATA[{AUTHOR_NAME}]]></googleplay:author>'''
    tail = '''
    </channel>
</rss>'''

    posts, images_to_upload = get_all_posts()

    feed = f'{head}{"".join(posts)}{tail}'

    with open(OUTPUT_FILE, "w") as f:
        f.write(feed)

    if upload_to_neocities:
        nc = neocities.NeoCities(api_key=key.strip())
        try:
            nc.upload((str(OUTPUT_FILE), NEOCITIES_UPLOAD_PATH), *images_to_upload)
        except neocities.neocities.NeoCities.InvalidRequestError as e:
            print(e)
            print()
            print("Your API key might be incorrect / broken")