# Trustworthy Ratings: Wilson Score & Bayesian Average

A 5.0 rating from 8 reviews and a 4.6 rating from 500 reviews are not the same thing. This repo has clean implementations of two tools that formalize that intuition — in both Python and R.

---

## The Problem With Raw Averages

A straight average treats all sample sizes as equally trustworthy. It doesn't. A product with 8 perfect reviews could easily be a 3-star product that got lucky early. A product with 500 reviews averaging 4.6 is almost certainly close to its true quality.

These two tools fix that.

---

## Wilson Score

**Best for: binary ratings** (thumbs up/down, helpful/not helpful)

Instead of asking "what's the average so far," it asks "what's the lowest the true approval rate could plausibly be, given what we've seen?" It returns a lower confidence bound. Rank by the floor, not the ceiling.

- 8/8 positive → floor ~63%
- 460/500 positive → floor ~89%

Product B wins, even though its raw score is lower.

**Used by:** Reddit (comment sorting), Yelp, Amazon helpful votes

---

## Bayesian Average

**Best for: scaled ratings** (1-5 stars, 1-10 scores)

Every product starts at the global average — the assumption that before you have real evidence, any product is probably about average. Reviews pull the score away from that prior. The more reviews, the more the product's own signal takes over.

- 5.0 with 8 reviews → adjusts down to ~3.9
- 4.6 with 500 reviews → stays close to 4.6

**Used by:** IMDb (movie ratings), BoardGameGeek

---

## Repo Structure

```
wilson-bayes-ratings/
  python/
    wilson_score.py       # Wilson Score function + visualization
    bayesian_average.py   # Bayesian Average function + visualization
    demo.py               # Plug in your own products and compare
  r/
    wilson_score.R        # Wilson Score function + visualization
    bayesian_average.R    # Bayesian Average function + visualization
```

---

## Quick Start

**Python**

```bash
pip install numpy matplotlib scipy
python demo.py
```

**R**

```r
# No extra packages required beyond base R
source("wilson_score.R")
source("bayesian_average.R")
```

---

## Plug In Your Own Numbers

In `demo.py` (Python) or directly in either `.R` file, edit the products list:

```python
PRODUCTS = [
    {"name": "Your Product",    "positive": 45,  "total": 50,  "rating_sum": 225},
    {"name": "Their Product",   "positive": 180, "total": 200, "rating_sum": 880},
]
```

Set `GLOBAL_MEAN` to the average rating across your product catalog.
Set `CONFIDENCE_WEIGHT` to roughly the average number of reviews per product in your system.

---

## When to Use Which

| Situation                            | Use              |
| ------------------------------------ | ---------------- |
| Thumbs up / thumbs down              | Wilson Score     |
| Helpful / not helpful votes          | Wilson Score     |
| 1-5 star ratings                     | Bayesian Average |
| NPS scores                           | Bayesian Average |
| Ranking job candidates by references | Either           |

---

## Further Reading

- [Reddit's comment ranking](https://redditblog.com/2009/10/15/reddits-new-comment-sorting-system/) — the original Wilson Score post
- [IMDb's weighted average](https://www.imdb.com/chart/top/) — Bayesian Average in production
- Wilson, E.B. (1927). "Probable inference, the law of succession, and statistical inference." _JASA_.
