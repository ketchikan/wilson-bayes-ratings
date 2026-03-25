"""
Bayesian Average

The Bayesian Average answers the question:
"Given what we know about products in general, how good is THIS
product once we account for how few reviews it has?"

Every product starts at the global average — the assumption being
that before you have real evidence, any product is probably about
average. Reviews then pull the rating away from that starting point.

The more reviews, the more the product's own signal takes over.
The fewer reviews, the more it stays anchored to the global average.

Use this for SCALED ratings (1-5 stars, 1-10 scores, etc.)
"""

import numpy as np
import matplotlib.pyplot as plt


def bayesian_average(ratings: list[float], global_mean: float, confidence_weight: float) -> dict:
    """Calculate the Bayesian Average for a product's star ratings.

    Args:
        ratings (list[float])    : list of individual ratings (e.g. [5, 4, 5, 3, 5])
        global_mean (float)      : the average rating across ALL products in your system
                                   (for example, what the average rating of similar products or services is)
        confidence_weight (float): how many reviews does it take before you trust this
                                   product's own signal over the global average?
                                   typically set to the average number of reviews per product

    Returns:
        dict:
            raw_average      : simple mean of ratings
            bayesian_average : adjusted score (anchored toward global mean for small samples)
            n                : number of reviews
            global_mean      : the prior you provided
    """

    n = len(ratings)

    if n == 0:
        return {
            "raw_average": global_mean,
            "bayesian_average": global_mean,
            "n": 0,
            "global_mean": global_mean,
        }

    raw_avg = sum(ratings) / n

    # the formula: pull toward the global mean, weighted by how few reviews we have
    # as n grows, the global_mean term shrinks and the product's own signal takes over
    bayes_avg = (confidence_weight * global_mean + sum(ratings)) / (confidence_weight + n)

    return {
        "raw_average": round(raw_avg, 4),
        "bayesian_average": round(bayes_avg, 4),
        "n": n,
        "global_mean": global_mean,
    }


def bayesian_average_from_summary(n: int, rating_sum: float, global_mean: float, confidence_weight: float) -> dict:
    """Same as bayesian_average() but takes a summary instead of raw ratings.
       Useful when you only have aggregate data (e.g. from a database).

    Args:
        n (int)                  : number of reviews
        rating_sum (float)       : sum of all ratings
        global_mean (float)      : average rating across all products (see bayesian_average docstring)
        confidence_weight (float): trust weight (see bayesian_average docstring)

    Returns:
        dict:
            raw_average      : simple mean of ratings
            bayesian_average : adjusted score (anchored toward global mean for small samples)
            n                : number of reviews
            global_mean      : the prior you provided
    """

    if n == 0:
        return {"raw_average": global_mean, "bayesian_average": global_mean, "n": 0}

    raw_avg = rating_sum / n
    bayes_avg = (confidence_weight * global_mean + rating_sum) / (confidence_weight + n)

    return {
        "raw_average": round(raw_avg, 4),
        "bayesian_average": round(bayes_avg, 4),
        "n": n,
        "global_mean": global_mean,
    }


def compare_products(products: list[dict], global_mean: float, confidence_weight: float) -> list[dict]:
    """Compare multiple products by their Bayesian Average.

    Args:
        products (list[dict])    : list of dicts, each with 'name', 'n', 'rating_sum'
        global_mean (float)      : average rating across all products
        confidence_weight (float): trust weight

    Returns:
        list[dict]: list of products sorted by Bayesian Average (best first)
    """

    results = []
    for p in products:
        score = bayesian_average_from_summary(p["n"], p["rating_sum"], global_mean, confidence_weight)
        results.append(
            {
                "name": p["name"],
                "n": p["n"],
                "raw_average": score["raw_average"],
                "bayesian_average": score["bayesian_average"],
            }
        )

    return sorted(results, key=lambda x: x["bayesian_average"], reverse=True)


def plot_convergence(
    product_a_raw: float,
    product_b_raw: float,
    global_mean: float,
    confidence_weight: float,
    max_reviews: int = 500,
):
    """Visualize how two products' Bayesian Averages converge toward their
        true ratings as reviews accumulate.

        This shows why a 5.0 with 8 reviews is less trustworthy than a
        4.6 with 500 — the 5.0 is still mostly the global average talking.

    Args:
        product_a_raw (float)      : the 'true' raw rating for product A (e.g. 5.0)
        product_b_raw (float)      : the 'true' raw rating for product B (e.g. 4.6)
        global_mean (float)        : prior (average across all products)
        confidence_weight (float)  : trust weight
        max_reviews (int, optional): how many reviews to simulate up to. Defaults to 500.
    """

    review_counts = np.arange(1, max_reviews + 1)

    bayes_a = []
    bayes_b = []

    for n in review_counts:
        # simulate ratings as if each product is consistently rated at its raw score
        score_a = bayesian_average_from_summary(n, product_a_raw * n, global_mean, confidence_weight)
        score_b = bayesian_average_from_summary(n, product_b_raw * n, global_mean, confidence_weight)
        bayes_a.append(score_a["bayesian_average"])
        bayes_b.append(score_b["bayesian_average"])

    plt.figure(figsize=(10, 5))
    plt.plot(review_counts, bayes_a, color="#2563eb", linewidth=2, label=f"Product A (raw: {product_a_raw})")
    plt.plot(review_counts, bayes_b, color="#16a34a", linewidth=2, label=f"Product B (raw: {product_b_raw})")
    plt.axhline(y=global_mean, color="#9ca3af", linestyle=":", linewidth=1.5, label=f"Global mean ({global_mean})")

    # mark the crossover point if it exists
    for i in range(len(bayes_a) - 1):
        if bayes_a[i] >= bayes_b[i] and bayes_a[i + 1] < bayes_b[i + 1]:
            plt.axvline(
                x=review_counts[i],
                color="#f59e0b",
                linestyle="--",
                linewidth=1.5,
                label=f"Product B takes lead (~{review_counts[i]} reviews)",
            )
            break

    plt.title("Bayesian Average Convergence\n(How ratings stabilize as reviews accumulate)", fontsize=13)
    plt.xlabel("Number of Reviews")
    plt.ylabel("Bayesian Average Score")
    plt.legend()
    plt.tight_layout()
    plt.savefig("bayesian_convergence.png", dpi=150)
    plt.show()
    print("Chart saved as bayesian_convergence.png")


# TRY IT YOURSELF
if __name__ == "__main__":
    # global average rating across all products in your system
    GLOBAL_MEAN = 3.5

    # how many reviews does it take before you trust a product's own signal?
    # set this to roughly the average number of reviews per product in your system
    CONFIDENCE_WEIGHT = 25

    # --- Single product score ---
    result = bayesian_average_from_summary(
        n=8,
        rating_sum=40,  # 8 reviews all rated 5 stars
        global_mean=GLOBAL_MEAN,
        confidence_weight=CONFIDENCE_WEIGHT,
    )
    print("Product A — 8 reviews, all 5 stars:")
    print(f"  Raw average:      {result['raw_average']:.2f}")
    print(f"  Bayesian average: {result['bayesian_average']:.2f}")
    print()

    result = bayesian_average_from_summary(
        n=500,
        rating_sum=2300,  # 500 reviews averaging 4.6 stars
        global_mean=GLOBAL_MEAN,
        confidence_weight=CONFIDENCE_WEIGHT,
    )
    print("Product B — 500 reviews, averaging 4.6 stars:")
    print(f"  Raw average:      {result['raw_average']:.2f}")
    print(f"  Bayesian average: {result['bayesian_average']:.2f}")
    print()

    # --- Compare two products ---
    products = [
        {"name": "Product A", "n": 8, "rating_sum": 40},
        {"name": "Product B", "n": 500, "rating_sum": 2300},
    ]

    ranked = compare_products(products, GLOBAL_MEAN, CONFIDENCE_WEIGHT)
    print("Ranking by Bayesian Average (best first):")
    for i, p in enumerate(ranked, 1):
        print(f"  {i}. {p['name']}: raw={p['raw_average']:.2f}, bayesian={p['bayesian_average']:.2f} ({p['n']} reviews)")
    print()

    # --- Visualization ---
    plot_convergence(
        product_a_raw=5.0,
        product_b_raw=4.6,
        global_mean=GLOBAL_MEAN,
        confidence_weight=CONFIDENCE_WEIGHT,
    )
