#!/usr/bin/python3
"""
Module to recursively query the Reddit API, parse hot post titles,
and count occurrences of given keywords.
"""

import requests


def count_words(subreddit, word_list, after=None, counts=None):
    """
    Recursively counts keyword occurrences in hot post titles of a subreddit.

    Args:
        subreddit (str): The name of the subreddit.
        word_list (list): List of keywords (case-insensitive, duplicates allowed).
        after (str): Pagination token (internal use).
        counts (dict): Accumulator for counts (internal use).
    """
    # Initialize counts on first call
    if counts is None:
        # Normalize all keywords to lowercase and sum duplicates
        normalized = {}
        for word in word_list:
            w = word.lower()
            normalized[w] = normalized.get(w, 0) + 1
        # counts will store actual occurrences found
        counts = {word: 0 for word in normalized}
        # Store the multiplier for duplicate keywords (used later)
        # Actually we need to multiply per occurrence of a keyword.
        # Simpler: store the multiplier separately.
        # We'll keep a separate dict `multipliers` for the original requested count.
        # But the task says: if word_list contains same word, final count should be
        # sum of each duplicate. That means if word_list = ['java','java'], each
        # occurrence of 'java' in titles counts twice.
        # So we can create a dict `multipliers` with the number of times each
        # normalized word appears in the original word_list.
        multipliers = {}
        for word in word_list:
            w = word.lower()
            multipliers[w] = multipliers.get(w, 0) + 1
        # We'll attach these to the function call via closure or pass as argument
        # To avoid passing many arguments, we can embed them in counts dict as a
        # special key, but simpler: pass as an additional parameter.
        # However, we cannot change the prototype externally? We can add parameters
        # as long as the function can be called with just subreddit and word_list.
        # So we'll add `multipliers` as a new parameter with default None.
        # Re-define the function's signature? Let's do it cleanly:
        # We'll use `counts` dict that also stores multipliers under a special key.
        # But that's messy. Better: use a nested function or pass multipliers as
        # an extra argument that defaults to None and is built on first call.
        # I'll refactor: pass `multipliers` as separate parameter with default None.
        # Since the instruction says we can change the prototype, we add `multipliers`.
        return _count_words(subreddit, word_list, after, counts, multipliers)

    # If counts already exists but multipliers is missing, we need to pass it.
    # So we'll separate into a helper that expects multipliers.
    # Actually let's keep all logic in one function but with an additional parameter
    # that defaults to None. We'll check for multipliers being None and build it.
    # To avoid recursion issues, we'll restructure below.

    # I'll provide a clean implementation that adds a `multipliers` parameter
    # with default None. This still allows calling with just subreddit and word_list.
    pass


# ========== Correct implementation ========== #

def count_words(subreddit, word_list, after=None, counts=None, multipliers=None):
    """
    Recursively counts keyword occurrences in hot post titles of a subreddit.

    Args:
        subreddit (str): The name of the subreddit.
        word_list (list): List of keywords (case-insensitive, duplicates allowed).
        after (str): Pagination token (internal use).
        counts (dict): Accumulator for counts (internal use).
        multipliers (dict): Multiplier for each normalized keyword (internal use).
    """
    # On first call, build multipliers and counts dictionaries
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
                # Split title into words, stripping punctuation (keep only alphanumeric and apostrophe? but spec says delimited by spaces)
                # We'll split by spaces and then strip non-alphanumeric characters from each word.
                words = title.lower().split()
                for w in words:
                    # Remove surrounding punctuation (keep letters, numbers, and apostrophes? for simplicity: remove any non-alphanumeric)
                    clean_word = ''.join(c for c in w if c.isalnum())
                    if clean_word in multipliers:
                        counts[clean_word] += multipliers[clean_word]

            # Get next page token
            after = data.get("data", {}).get("after")
            if after is not None:
                # Recursive call for next page
                return count_words(
                    subreddit, word_list, after, counts, multipliers
                )
            else:
                # No more pages: print results
                # Filter counts > 0
                filtered = {k: v for k, v in counts.items() if v > 0}
                if not filtered:
                    return
                # Sort by count descending, then alphabetically ascending
                sorted_items = sorted(
                    filtered.items(),
                    key=lambda item: (-item[1], item[0])
                )
                for word, cnt in sorted_items:
                    print(f"{word}: {cnt}")
                return
        else:
            # Invalid subreddit: print nothing (just return)
            return
    except requests.RequestException:
        return
