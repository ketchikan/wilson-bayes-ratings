"""
Wilson Score Interval

The Wilson Score answers the question:
"Given the reviews we've seen so far, what's the LOWEST the true
approval rate could plausibly be?"

This is more useful than a raw average because it penalizes small
sample sizes. A product with 8/8 positive reviews sounds perfect,
but we can't trust it yet. A product with 460/500 positive reviews
has a much more reliable floor.

Use this for BINARY ratings (thumbs up/down, helpful/not helpful).
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import norm


def wilson_score(positive: int, total: int, confidence: float = 0.95) -> dict:
    """Calculate the Wilson Score lower bound for a binary rating.

    Args:
        positive (int)              : number of positive ratings (thumbs up, helpful, etc.)
        total (int)                 : total number of ratings
        confidence (float, optional): how confident do you want to be?
                                      higher confidence = more conservative (lower) floor
                                      common values: 0.90, 0.95, 0.99. Defaults to 0.95.

    Returns:
        dict:
            raw_score   : simple average (positive / total)
            lower_bound : wilson score floor — use this for ranking
            upper_bound : wilson score ceiling
            z           : z-value used (standard deviations for confidence level)
    """
    if total == 0:
        return {"raw_score": 0, "lower_bound": 0, "upper_bound": 0, "z": 0}

    # z is the number of standard deviations that captures our confidence level
    # example: z = 1.96 captures 95% of a normal distribution
    z = norm.ppf(1 - (1 - confidence) / 2)

    # observed approval rate
    p_hat = positive / total

    # the wilson formula, which penalizes small samples and extreme scores
    center = p_hat + z**2 / (2 * total)
    margin = z * np.sqrt((p_hat * (1 - p_hat) / total) + (z**2 / (4 * total**2)))
    denominator = 1 + z**2 / total

    lower_bound = (center - margin) / denominator
    upper_bound = (center + margin) / denominator

    return {
        "raw_score": round(p_hat, 4),
        "lower_bound": round(lower_bound, 4),
        "upper_bound": round(upper_bound, 4),
        "z": round(z, 4),
    }


def compare_products(products: list[dict], confidence: float = 0.95) -> list[dict]:
    """Compare multiple products by their Wilson Score lower bound.

    Args:
        products (list[dict])       : list of dicts, each with 'name', 'positive', 'total'
        confidence (float, optional): confidence level to use for all products. Defaults to 0.95.

    Returns:
        list[dict]: list of products sorted by Wilson lower bound (best first),
                    with scores attached
    """
    results = []
    for p in products:
        score = wilson_score(p["positive"], p["total"], confidence)
        results.append(
            {
                "name": p["name"],
                "positive": p["positive"],
                "total": p["total"],
                "raw_score": score["raw_score"],
                "wilson_lower_bound": score["lower_bound"],
            }
        )

    # rank by floor
    return sorted(results, key=lambda x: x["wilson_lower_bound"], reverse=True)


def plot_wilson_floor(approval_rate: float = 0.92, confidence: float = 0.95) -> None:
    """Visualize how the Wilson Score floor rises as sample size increases.

    Args:
        approval_rate (float, optional): fixed approval rate to visualize. Defaults to 0.92.
        confidence (float, optional): confidence level. Defaults to 0.95.
    """

    sample_sizes = np.arange(1, 501)
    floors = []

    for n in sample_sizes:
        positive = int(n * approval_rate)
        score = wilson_score(positive, n, confidence)
        floors.append(score["lower_bound"])

    plt.figure(figsize=(10, 5))
    plt.plot(sample_sizes, floors, color="#2563eb", linewidth=2, label="Wilson Score Floor")
    plt.axhline(
        y=approval_rate, color="#dc2626", linestyle="--", linewidth=1.5, label=f"Raw approval rate ({approval_rate:.0%})"
    )

    # annotate a few key sample sizes so the reader can see the convergence
    for n in [8, 50, 100, 250, 500]:
        positive = int(n * approval_rate)
        score = wilson_score(positive, n, confidence)
        plt.annotate(
            f"n={n}\nfloor={score['lower_bound']:.2f}",
            xy=(n, score["lower_bound"]),
            xytext=(n + 15, score["lower_bound"] - 0.04),
            fontsize=8,
            color="#374151",
        )

    plt.title(
        f"Wilson Score Floor vs Sample Size\n(Approval Rate: {approval_rate:.0%}, Confidence: {confidence:.0%})", fontsize=13
    )
    plt.xlabel("Number of Reviews")
    plt.ylabel("Wilson Score Lower Bound")
    plt.legend()
    plt.tight_layout()
    plt.savefig("wilson_floor.png", dpi=150)
    plt.show()
    print("Chart saved as wilson_floor.png")


# TRY IT YOURSELF!

if __name__ == "__main__":
    # --- Single product score ---
    result = wilson_score(positive=460, total=500, confidence=0.95)
    print("460/500 positive reviews:")
    print(f"  Raw score:     {result['raw_score']:.2%}")
    print(f"  Wilson floor:  {result['lower_bound']:.2%}")
    print(f"  Wilson ceiling:{result['upper_bound']:.2%}")
    print()

    # --- Compare two products ---
    products = [
        {"name": "Product A", "positive": 8, "total": 8},
        {"name": "Product B", "positive": 460, "total": 500},
    ]

    ranked = compare_products(products)
    print("Ranking by Wilson Score (best first):")
    for i, p in enumerate(ranked, 1):
        print(
            f"  {i}. {p['name']}: raw={p['raw_score']:.2%}, floor={p['wilson_lower_bound']:.2%} ({p['positive']}/{p['total']} reviews)"
        )
    print()

    # --- Visualization ---
    plot_wilson_floor(approval_rate=0.92)
