# Bayesian Average
# The Bayesian Average answers the question:
# "Given what we know about products in general, how good is THIS
# product once we account for how few reviews it has?"
#
# Every product starts at the global average — the assumption being
# that before you have real evidence, any product is probably about
# average. Reviews then pull the rating away from that starting point.
#
# The more reviews, the more the product's own signal takes over.
# The fewer reviews, the more it stays anchored to the global average.
#
# Use this for SCALED ratings (1-5 stars, 1-10 scores, etc.)


# BAYESIAN AVERAGE FUNCTION (from summary stats)

bayesian_average <- function(n, rating_sum, global_mean, confidence_weight) {
  #' Calculate the Bayesian Average from summary statistics.
  #'
  #' @param n                 number of reviews
  #' @param rating_sum        sum of all ratings (e.g. 5+4+5+3 = 17)
  #' @param global_mean       average rating across ALL products in your system
  #'                          this is your 'prior' — what you assume before seeing data
  #' @param confidence_weight how many reviews does it take before you trust this
  #'                          product's own signal over the global average?
  #'                          typically set to the average number of reviews per product
  #'
  #' @return named list with raw_average, bayesian_average, n

  if (n == 0) {
    return(list(raw_average = global_mean, bayesian_average = global_mean, n = 0))
  }

  raw_avg  <- rating_sum / n

  # the formula: pull toward the global mean, weighted by how few reviews we have
  # as n grows, the global_mean term shrinks and the product's own signal takes over
  bayes_avg <- (confidence_weight * global_mean + rating_sum) / (confidence_weight + n)

  list(
    raw_average      = round(raw_avg, 4),
    bayesian_average = round(bayes_avg, 4),
    n                = n
  )
}


# BAYESIAN AVERAGE FROM RAW RATINGS VECTOR

bayesian_average_from_ratings <- function(ratings, global_mean, confidence_weight) {
  #' Calculate Bayesian Average from a vector of individual ratings.
  #'
  #' @param ratings           numeric vector of ratings (e.g. c(5, 4, 5, 3, 5))
  #' @param global_mean       average rating across all products
  #' @param confidence_weight trust weight (see bayesian_average docstring)

  bayesian_average(
    n                = length(ratings),
    rating_sum       = sum(ratings),
    global_mean      = global_mean,
    confidence_weight = confidence_weight
  )
}


# COMPARE MULTIPLE PRODUCTS

compare_products_bayes <- function(products, global_mean, confidence_weight) {
  #' Compare a list of products by their Bayesian Average.
  #'
  #' @param products          data.frame with columns: name, n, rating_sum
  #' @param global_mean       average rating across all products
  #' @param confidence_weight trust weight
  #'
  #' @return data.frame sorted by Bayesian Average (best first)

  results <- do.call(rbind, lapply(seq_len(nrow(products)), function(i) {
    p     <- products[i, ]
    score <- bayesian_average(p$n, p$rating_sum, global_mean, confidence_weight)
    data.frame(
      name             = p$name,
      n                = p$n,
      raw_average      = score$raw_average,
      bayesian_average = score$bayesian_average,
      stringsAsFactors = FALSE
    )
  }))

  results[order(results$bayesian_average, decreasing = TRUE), ]
}


# VISUALIZATION

plot_convergence <- function(
  product_a_raw,
  product_b_raw,
  global_mean,
  confidence_weight,
  max_reviews = 500
) {
  #' Visualize how two products' Bayesian Averages converge as reviews accumulate.
  #'
  #' @param product_a_raw   the raw rating for product A (e.g. 5.0)
  #' @param product_b_raw   the raw rating for product B (e.g. 4.6)
  #' @param global_mean     prior (average across all products)
  #' @param confidence_weight trust weight
  #' @param max_reviews     how many reviews to simulate up to

  review_counts <- 1:max_reviews

  bayes_a <- sapply(review_counts, function(n) {
    bayesian_average(n, product_a_raw * n, global_mean, confidence_weight)$bayesian_average
  })

  bayes_b <- sapply(review_counts, function(n) {
    bayesian_average(n, product_b_raw * n, global_mean, confidence_weight)$bayesian_average
  })

  plot(
    review_counts, bayes_a,
    type = "l", col = "#2563eb", lwd = 2,
    xlab = "Number of Reviews",
    ylab = "Bayesian Average Score",
    main = "Bayesian Average Convergence\n(How ratings stabilize as reviews accumulate)",
    ylim = c(global_mean - 0.1, max(product_a_raw, product_b_raw) + 0.1)
  )

  lines(review_counts, bayes_b, col = "#16a34a", lwd = 2)

  # global mean as reference
  abline(h = global_mean, col = "#9ca3af", lty = 3, lwd = 1.5)

  # find and mark crossover point if it exists
  crossover <- which(bayes_a >= bayes_b & c(bayes_a[-1], NA) < c(bayes_b[-1], NA))
  if (length(crossover) > 0) {
    abline(v = crossover[1], col = "#f59e0b", lty = 2, lwd = 1.5)
  }

  legend(
    "right",
    legend = c(
      paste0("Product A (raw: ", product_a_raw, ")"),
      paste0("Product B (raw: ", product_b_raw, ")"),
      paste0("Global mean (", global_mean, ")")
    ),
    col  = c("#2563eb", "#16a34a", "#9ca3af"),
    lty  = c(1, 1, 3),
    lwd  = 2
  )
}


# TRY IT YOURSELF

GLOBAL_MEAN       <- 3.5   # average rating across all products in your system
CONFIDENCE_WEIGHT <- 25    # roughly: average number of reviews per product

# Single product scores
result_a <- bayesian_average(n = 8, rating_sum = 40, GLOBAL_MEAN, CONFIDENCE_WEIGHT)
cat("Product A — 8 reviews, all 5 stars:\n")
cat(sprintf("  Raw average:      %.2f\n", result_a$raw_average))
cat(sprintf("  Bayesian average: %.2f\n", result_a$bayesian_average))
cat("\n")

result_b <- bayesian_average(n = 500, rating_sum = 2300, GLOBAL_MEAN, CONFIDENCE_WEIGHT)
cat("Product B — 500 reviews, averaging 4.6 stars:\n")
cat(sprintf("  Raw average:      %.2f\n", result_b$raw_average))
cat(sprintf("  Bayesian average: %.2f\n", result_b$bayesian_average))
cat("\n")

# Compare two products
products <- data.frame(
  name       = c("Product A", "Product B"),
  n          = c(8, 500),
  rating_sum = c(40, 2300),
  stringsAsFactors = FALSE
)

ranked <- compare_products_bayes(products, GLOBAL_MEAN, CONFIDENCE_WEIGHT)
cat("Ranking by Bayesian Average (best first):\n")
for (i in seq_len(nrow(ranked))) {
  p <- ranked[i, ]
  cat(sprintf("  %d. %-15s raw: %.2f   bayesian: %.2f  (%d reviews)\n",
    i, p$name, p$raw_average, p$bayesian_average, p$n))
}
cat("\n")

# Visualization
plot_convergence(
  product_a_raw     = 5.0,
  product_b_raw     = 4.6,
  global_mean       = GLOBAL_MEAN,
  confidence_weight = CONFIDENCE_WEIGHT
)