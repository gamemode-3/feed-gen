import html
import os
from pathlib import Path
import time


FEED_NAME = "mai.loeckchen"
FEED_DESC = "what i'm up to"
FEED_IMAGE = "image.png"
FEED_URL = "https://mailoeckchen.neocities.org/up-to/feed.xml"
AUTHOR_NAME = "mai.loeckchen"
AUTHOR_EMAIL = "mailoeckchen@proton.me"
POST_URL_PATTERN = "https://mailoeckchen.neocities.org/up-to/view?post={slug}"


COPYRIGHT = AUTHOR_NAME
LANGUAGE = "en"


POST_DIR = Path("./posts")
OUTPUT_FILE = Path("./feed.xml")


def gen_post_url(index: int, slug: str):
    return POST_URL_PATTERN.replace("{id}", str(index)).replace("{slug}", slug)


from datetime import datetime, timezone
import markdown2
from bs4 import BeautifulSoup, PageElement


def format_time(t: datetime):
    return t.strftime("%a, %d %b %Y %H:%M:%S GMT")


def gen_post(text: str, index: int, modified: datetime):

    md_html = markdown2.markdown(text, extras=["fenced-code-blocks", "header-ids", "latex", "metadata", "strike", "tables", "tg-spoiler"])

    metadata = md_html.metadata
    print(metadata)

    soup = BeautifulSoup(md_html, "html.parser")

    title_o: None | PageElement = soup.find("h1")
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

    return f'''
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


def get_all_posts() -> list[str]:
    files = []

    for file in os.scandir(POST_DIR):
        if file.is_file() and file.name.endswith(".md"):
            mtime = os.path.getmtime(file)
            files.append((file, mtime))

    posts = []

    
    files.sort(key=lambda x: x[1])

    for i, (file, mtime) in enumerate(files):
        with open(file) as f:
            posts.append(gen_post(f.read(), i, datetime.fromtimestamp(mtime)))
    

    return posts



if __name__ == "__main__":

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


    feed = f'{head}{"".join(get_all_posts())}{tail}'

    with open(OUTPUT_FILE, "w") as f:
        f.write(feed)