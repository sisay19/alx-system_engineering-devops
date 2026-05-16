#!/usr/bin/python3
"""
Module to query the Reddit API and return the number of subscribers
for a given subreddit.
"""

import requests


def number_of_subscribers(subreddit):
    """
    Queries the Reddit API and returns the total number of subscribers
    for a specified subreddit.

    Args:
        subreddit (str): The name of the subreddit to query.

    Returns:
        int: Number of subscribers, or 0 if the subreddit is invalid.
    """
    url = f"https://www.reddit.com/r/{subreddit}/about.json"
    headers = {"User-Agent": "ALX-API-Advanced-Task0/0.1"}
    try:
        # Disallow redirects to detect invalid subreddits (they return a 302 redirect)
        response = requests.get(url, headers=headers, allow_redirects=False)

        if response.status_code == 200:
            data = response.json()
            # Extract subscriber count from the JSON response
            return data.get("data", {}).get("subscribers", 0)
        else:
            return 0
    except requests.RequestException:
        # Any network/request error -> treat as invalid
        return 0
