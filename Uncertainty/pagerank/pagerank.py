import os
import random
import re
import sys
import copy

DAMPING = 0.85
SAMPLES = 10000


def main():
    if len(sys.argv) != 2:
        sys.exit("Usage: python pagerank.py corpus")
    corpus = crawl(sys.argv[1])
    ranks = sample_pagerank(corpus, DAMPING, SAMPLES)
    print(f"PageRank Results from Sampling (n = {SAMPLES})")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")
    ranks = iterate_pagerank(corpus, DAMPING)
    print(f"PageRank Results from Iteration")
    for page in sorted(ranks):
        print(f"  {page}: {ranks[page]:.4f}")


def crawl(directory):
    """
    Parse a directory of HTML pages and check for links to other pages.
    Return a dictionary where each key is a page, and values are
    a list of all other pages in the corpus that are linked to by the page.
    """
    pages = dict()

    # Extract all links from HTML files
    for filename in os.listdir(directory):
        if not filename.endswith(".html"):
            continue
        with open(os.path.join(directory, filename)) as f:
            contents = f.read()
            links = re.findall(r"<a\s+(?:[^>]*?)href=\"([^\"]*)\"", contents)
            pages[filename] = set(links) - {filename}

    # Only include links to other pages in the corpus
    for filename in pages:
        pages[filename] = set(
            link for link in pages[filename]
            if link in pages
        )

    return pages


def transition_model(corpus, page, damping_factor):
    """
    Returns a probability distribution over which page to visit next,
    given the current page.

    With probability `damping_factor`, the next page is chosen randomly
    from the links available on the current page.
    With probability `1 - damping_factor`, the next page is chosen randomly
    from all pages in the corpus.
    """
    d = {}  # Dictionary to store the probability distribution
    links = corpus[page]  # Get all links from the current page
    num_pages = len(corpus)  # Total number of pages in the corpus
    num_links = len(links)  # Number of links available on the current page

    if links:
        # Assign base probability of (1 - damping_factor) / num_pages to all pages
        for key in corpus:
            d[key] = (1 - damping_factor) / num_pages

        # Distribute damping_factor probability among linked pages
        for key in links:
            d[key] += damping_factor / num_links
    else:
        # If no links are available, distribute probability equally to all pages
        for key in corpus:
            d[key] = 1.0 / num_pages

    return d


def sample_pagerank(corpus, damping_factor, n):
    """
    Returns the estimated PageRank values for each page by sampling `n` pages
    based on the transition model.

    - Starts with a random page.
    - Uses the transition model to determine the next page based on probabilities.
    - Updates the estimated PageRank values iteratively.
    - Ensures that the sum of PageRank values is approximately 1.
    """
    d = {}.fromkeys(corpus.keys(), 0)  # Initialize PageRank dictionary with zeros
    page = random.choices(list(corpus.keys()))[0]  # Choose a random starting page

    for i in range(1, n):
        current_dist = transition_model(corpus, page, damping_factor)  # Get transition probabilities
        for _page in d:
            # Update PageRank estimate using weighted average formula
            d[_page] = (((i - 1) * d[_page]) + current_dist[_page]) / i

        # Choose the next page based on the current probability distribution
        page = random.choices(list(d.keys()), weights=list(d.values()), k=1)[0]

    return d


def iterate_pagerank(corpus, damping_factor):
    """
    Returns the PageRank values for each page by iteratively updating
    the values until convergence.

    - Starts with equal probability for all pages.
    - Updates the PageRank values based on incoming links and their PageRanks.
    - Stops when the difference in PageRank values is below a threshold (0.001).
    - Ensures that the sum of PageRank values is approximately 1.
    """
    total_pages = len(corpus)
    distribution = {}.fromkeys(corpus.keys(), 1.0 / total_pages)  # Initialize equal probability
    change = True  # Flag to check for convergence

    while change:
        change = False
        old_distribution = copy.deepcopy(distribution)  # Store previous PageRank values

        for page in corpus:
            # Compute new PageRank using the damping formula
            distribution[page] = ((1 - damping_factor) / total_pages) + \
                (damping_factor * get_sum(corpus, distribution, page))

            # Check if the change in PageRank is significant (greater than 0.001)
            change = change or abs(old_distribution[page] - distribution[page]) > 0.001

    return distribution


def get_sum(corpus, distribution, page):
    result = 0
    for p in corpus:
        if page in corpus[p]:
            result += distribution[p] / len(corpus[p])
    return result


if __name__ == "__main__":
    main()