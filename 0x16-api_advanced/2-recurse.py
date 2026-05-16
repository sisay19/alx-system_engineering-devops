#!/usr/bin/python3
"""
Module to recursively query the Reddit API and return a list of titles
of all hot articles for a given subreddit.
"""

import requests


def recurse(subreddit, hot_list=None, after=None):
    """
    Recursively retrieves titles of all hot posts for a subreddit.

    Args:
        subreddit (str): The name of the subreddit.
        hot_list (list): Accumulator for post titles (internal use).
        after (str): Pagination parameter (internal use).

    Returns:
        list or None: List of titles, or None if subreddit is invalid.
    """
    # Initialize hot_list on first call
    if hot_list is None:
        hot_list = []

    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    headers = {"User-Agent": "ALX-API-Advanced-Task2/0.1"}
    params = {"limit": 100}
    if after:
        params["after"] = after

    try:
        # Do not follow redirects (invalid subreddit returns 302)
        response = requests.get(
            url,
            headers=headers,
            params=params,
            allow_redirects=False
        )

        if response.status_code == 200:
            data = response.json()
            children = data.get("data", {}).get("children", [])
            # Append titles from current page
            for child in children:
                hot_list.append(child.get("data", {}).get("title"))

            # Get next page token
            after = data.get("data", {}).get("after")
            if after is not None:
                # Recursive call for next page
                return recurse(subreddit, hot_list, after)
            else:
                # No more pages - return full list
                return hot_list
        else:
            # Invalid subreddit (non-200 status)
            return None
    except requests.RequestException:
        return None
