"""
Demo — Compare Your Own Products

Plug in your own products and see how Wilson Score and Bayesian Average
rank them against each other.

Run this file directly:
    python demo.py
"""

from wilson_score import compare_products as wilson_compare
from bayesian_average import compare_products as bayes_compare


# ---------------------------------------------------------
# Configuration — edit these values
# ---------------------------------------------------------

# Your products: name, positive reviews (or sum of stars), total reviews
# For Wilson Score:  positive = number of thumbs up / helpful votes
# For Bayesian Avg:  rating_sum = sum of all star ratings (e.g. 5+4+5+3 = 17)

PRODUCTS = [
    {"name": "Product A", "positive": 8, "total": 8, "rating_sum": 40},
    {"name": "Product B", "positive": 460, "total": 500, "rating_sum": 2300},
    # Add more products here:
    # {"name": "Product C", "positive": 25, "total": 30, "rating_sum": 120},
]

# Bayesian Average settings
GLOBAL_MEAN = 3.5  # average rating across ALL products in your system
CONFIDENCE_WEIGHT = 25  # roughly: average number of reviews per product

# Wilson Score confidence level
CONFIDENCE_LEVEL = 0.95  # 95% — change to 0.90 or 0.99 if you want


# ---------------------------------------------------------
# Run the comparison
# ---------------------------------------------------------


def main():
    print("=" * 55)
    print("WILSON SCORE RANKING (binary ratings)")
    print("Best for: thumbs up/down, helpful/not helpful")
    print("=" * 55)

    wilson_products = [{"name": p["name"], "positive": p["positive"], "total": p["total"]} for p in PRODUCTS]
    wilson_ranked = wilson_compare(wilson_products, confidence=CONFIDENCE_LEVEL)

    for i, p in enumerate(wilson_ranked, 1):
        raw_pct = f"{p['raw_score']:.1%}"
        floor_pct = f"{p['wilson_lower_bound']:.1%}"
        print(f"  {i}. {p['name']:<15} raw: {raw_pct:<8} floor: {floor_pct}  ({p['positive']}/{p['total']} reviews)")

    print()
    print("=" * 55)
    print("BAYESIAN AVERAGE RANKING (star ratings)")
    print("Best for: 1-5 stars, 1-10 scores")
    print("=" * 55)

    bayes_products = [{"name": p["name"], "n": p["total"], "rating_sum": p["rating_sum"]} for p in PRODUCTS]
    bayes_ranked = bayes_compare(bayes_products, GLOBAL_MEAN, CONFIDENCE_WEIGHT)

    for i, p in enumerate(bayes_ranked, 1):
        print(
            f"  {i}. {p['name']:<15} raw: {p['raw_average']:.2f}    bayesian: {p['bayesian_average']:.2f}  ({p['n']} reviews)"
        )

    print()
    print(f"Settings: confidence={CONFIDENCE_LEVEL:.0%}, global_mean={GLOBAL_MEAN}, confidence_weight={CONFIDENCE_WEIGHT}")
    print()
    print("Tip: change GLOBAL_MEAN to the average rating in your own dataset.")
    print("     change CONFIDENCE_WEIGHT to the average number of reviews per product.")


if __name__ == "__main__":
    main()
