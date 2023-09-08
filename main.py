"""This script parses the HTML of the Google Next website and saves the transcript of each
presentation to a JSON file.
"""

from bs4 import BeautifulSoup
from youtube_transcript_api import YouTubeTranscriptApi
import json


def parse_html(html):
    """
    Parse the HTML of the Google Next website and return a list of presentations.

    Each presentation is a dictionary with the following keys:
    - title: title of the presentation
    - presentation_type: type of presentation (e.g. "Keynote", "Breakout Session")
    - categories: list of categories (e.g. ["Data Analytics", "AI & ML"])
    - video_id: YouTube video ID
    - time: time of presentation (e.g. "9:00 AM - 9:30 AM")

    :param html: HTML of the Google Next website
    :return: list of presentations
    """
    soup = BeautifulSoup(html, "html.parser")
    presentations = soup.find_all("div", class_="resourceCard-content")

    for i in range(len(presentations)):
        card = presentations[i]
        time = (
            card.find("div", class_="resource-time-small")
            .text.replace("\n", "")
            .strip()
        )
        presentation_type = card.find("span", class_="label").text
        category_node = card.find("p", class_="glue-label")
        categories = [
            span.text
            for span in category_node.find_all("span")
            if "aria-hidden" not in span.attrs
        ]
        title = card.find("h5", class_="glue-headline").text
        link = card.find("img").attrs["srcset"]
        video_id = (
            link.split("/")[4] if link.startswith("https://i.ytimg.com/vi") else None
        )

        presentations[i] = {
            "title": title,
            "presentation_type": presentation_type,
            "categories": categories,
            "video_id": video_id,
            "time": time,
        }

    return presentations


def get_transcript(video_id):
    """Return the transcript of a YouTube video.

    :param video_id: YouTube video ID
    :return: transcript of the video
    """
    transcript = YouTubeTranscriptApi.get_transcript(video_id)
    combined_text = "".join([t["text"] for t in transcript])
    return " ".join(combined_text.split())


def run():
    """
    Parse the HTML of the Google Next website and save the transcript of each presentation
    to a JSON file.

    The JSON file is saved in the transcripts/ directory.
    """
    with open("google-next.html", "r") as f:
        presentations = parse_html(f.read())

    # keep only presentations with youtube video, ignore the rest
    presentation_with_youtubes = [p for p in presentations if p["video_id"] is not None]

    # add transcript to each presentation and save to JSON file
    for p in presentation_with_youtubes:
        print(p["title"])

        p["transcript"] = get_transcript(p["video_id"])

        # convert title to safe filename
        filename = p["title"].replace("/", "-")
        json.dump(
            p,
            open(f"transcripts/{filename}.json", "w"),
            indent=4,
        )


if __name__ == "__main__":
    run()
