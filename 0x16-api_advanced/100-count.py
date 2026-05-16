#!/usr/bin/python3
"""
Module to recursively query the Reddit API, parse hot post titles,
and count occurrences of given keywords.
"""

import requests


def count_words(
        subreddit,
        word_list,
        after=None,
        counts=None,
        multipliers=None):
    """
    Recursively counts keyword occurrences in hot post titles of a subreddit.

    Args:
        subreddit (str): The name of the subreddit.
        word_list (list): List of keywords (case-insensitive,
                          duplicates allowed).
        after (str): Pagination token (internal use).
        counts (dict): Accumulator for counts (internal use).
        multipliers (dict): Multiplier for each normalized keyword
                            (internal use).
    """
    # Initialize on first call
    if multipliers is None:
        multipliers = {}
        for word in word_list:
            w = word.lower()
            multipliers[w] = multipliers.get(w, 0) + 1
        counts = {word: 0 for word in multipliers}

    url = f"https://www.reddit.com/r/{subreddit}/hot.json"
    headers = {"User-Agent": "ALX-API-Advanced-Task3/0.1"}
    params = {"limit": 100}
    if after:
        params["after"] = after

    try:
        response = requests.get(
            url,
            headers=headers,
            params=params,
            allow_redirects=False
        )

        if response.status_code == 200:
            data = response.json()
            children = data.get("data", {}).get("children", [])

            # Process each post title
            for child in children:
                title = child.get("data", {}).get("title", "")
                # Split into words and clean punctuation
                words = title.lower().split()
                for w in words:
                    # Keep only alphanumeric characters
                    clean_word = ''.join(c for c in w if c.isalnum())
                    if clean_word in multipliers:
                        counts[clean_word] += multipliers[clean_word]

            # Recursive call for next page
            after = data.get("data", {}).get("after")
            if after is not None:
                return count_words(
                    subreddit, word_list, after, counts, multipliers
                )
            else:
                # No more pages – print results
                filtered = {k: v for k, v in counts.items() if v > 0}
                if not filtered:
                    return
                sorted_items = sorted(
                    filtered.items(),
                    key=lambda item: (-item[1], item[0])
                )
                for word, cnt in sorted_items:
                    print(f"{word}: {cnt}")
                return
        else:
            # Invalid subreddit: print nothing
            return
    except requests.RequestException:
        return
