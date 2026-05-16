#!/usr/bin/python3
"""
Module to query the Reddit API and print the titles of the first 10 hot posts
for a given subreddit.
"""

import requests


def top_ten(subreddit):
    """
    Prints the titles of the first 10 hot posts for a subreddit.

    Args:
        subreddit (str): The name of the subreddit.
    """
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=10"
    headers = {"User-Agent": "ALX-API-Advanced-Task1/0.1"}

    try:
        # Do not follow redirects (invalid subreddits return 302)
        response = requests.get(
            url,
            headers=headers,
            allow_redirects=False
        )

        if response.status_code == 200:
            data = response.json()
            posts = data.get("data", {}).get("children", [])
            # Print each post title
            for post in posts:
                print(post.get("data", {}).get("title"))
        else:
            print(None)
    except requests.RequestException:
        print(None)
