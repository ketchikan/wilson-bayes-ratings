# Wilson Score Interval

# The Wilson Score answers the question:
# "Given the reviews we've seen so far, what's the LOWEST the true
# approval rate could plausibly be?"
#
# This is more useful than a raw average because it penalizes small
# sample sizes. A product with 8/8 positive reviews sounds perfect,
# but we can't trust it yet. A product with 460/500 positive reviews
# has a much more reliable floor.
#
# Use this for BINARY ratings (thumbs up/down, helpful/not helpful).


# WILSON SCORE FUNCTION

wilson_score <- function(positive, total, confidence = 0.95) {
  #' Calculate the Wilson Score lower bound for a binary rating.
  #'
  #' @param positive   number of positive ratings (thumbs up, helpful, etc.)
  #' @param total      total number of ratings
  #' @param confidence how confident do you want to be? (default 0.95 = 95%)
  #'                   higher confidence = more conservative (lower) floor
  #'
  #' @return named list with raw_score, lower_bound, upper_bound, z

  if (total == 0) {
    return(list(raw_score = 0, lower_bound = 0, upper_bound = 0, z = 0))
  }

  # z is the number of standard deviations that captures our confidence level
  # qnorm gives us the z value for a given confidence level
  z <- qnorm(1 - (1 - confidence) / 2)

  # observed approval rate
  p_hat <- positive / total

  # the wilson formula — penalizes small samples and extreme scores
  center      <- p_hat + z^2 / (2 * total)
  margin      <- z * sqrt((p_hat * (1 - p_hat) / total) + (z^2 / (4 * total^2)))
  denominator <- 1 + z^2 / total

  lower_bound <- (center - margin) / denominator
  upper_bound <- (center + margin) / denominator

  list(
    raw_score   = round(p_hat, 4),
    lower_bound = round(lower_bound, 4),
    upper_bound = round(upper_bound, 4),
    z           = round(z, 4)
  )
}


# ---------------------------------------------------------------
# Compare multiple products
# ---------------------------------------------------------------

compare_products_wilson <- function(products, confidence = 0.95) {
  #' Compare a list of products by their Wilson Score lower bound.
  #'
  #' @param products   data.frame with columns: name, positive, total
  #' @param confidence confidence level (default 0.95)
  #'
  #' @return data.frame sorted by Wilson lower bound (best first)

  results <- do.call(rbind, lapply(seq_len(nrow(products)), function(i) {
    p     <- products[i, ]
    score <- wilson_score(p$positive, p$total, confidence)
    data.frame(
      name               = p$name,
      positive           = p$positive,
      total              = p$total,
      raw_score          = score$raw_score,
      wilson_lower_bound = score$lower_bound,
      stringsAsFactors   = FALSE
    )
  }))

  # rank by floor, not raw score — this is the whole point
  results[order(results$wilson_lower_bound, decreasing = TRUE), ]
}


# VISUALIZATION

plot_wilson_floor <- function(approval_rate = 0.92, confidence = 0.95) {
  #' Visualize how the Wilson Score floor rises as sample size increases.
  #'
  #' @param approval_rate fixed approval rate to visualize (default 0.92)
  #' @param confidence    confidence level (default 0.95)

  sample_sizes <- 1:500
  floors <- sapply(sample_sizes, function(n) {
    positive <- floor(n * approval_rate)
    wilson_score(positive, n, confidence)$lower_bound
  })

  plot(
    sample_sizes, floors,
    type  = "l",
    col   = "#2563eb",
    lwd   = 2,
    xlab  = "Number of Reviews",
    ylab  = "Wilson Score Lower Bound",
    main  = paste0(
      "Wilson Score Floor vs Sample Size\n",
      "(Approval Rate: ", scales::percent(approval_rate),
      ", Confidence: ", scales::percent(confidence), ")"
    ),
    ylim  = c(min(floors) - 0.05, 1.0)
  )

  # raw approval rate as a reference line
  abline(h = approval_rate, col = "#dc2626", lty = 2, lwd = 1.5)

  # annotate key sample sizes
  key_ns <- c(8, 50, 100, 250, 500)
  for (n in key_ns) {
    positive <- floor(n * approval_rate)
    floor_val <- wilson_score(positive, n, confidence)$lower_bound
    text(n, floor_val - 0.03, labels = paste0("n=", n, "\n", round(floor_val, 2)), cex = 0.7)
  }

  legend(
    "bottomright",
    legend = c("Wilson Floor", paste0("Raw Rate (", approval_rate, ")")),
    col    = c("#2563eb", "#dc2626"),
    lty    = c(1, 2),
    lwd    = 2
  )
}


# TRY IT YOURSELF

# Single product score
result <- wilson_score(positive = 460, total = 500, confidence = 0.95)
cat("460/500 positive reviews:\n")
cat(sprintf("  Raw score:      %.2f%%\n", result$raw_score * 100))
cat(sprintf("  Wilson floor:   %.2f%%\n", result$lower_bound * 100))
cat(sprintf("  Wilson ceiling: %.2f%%\n", result$upper_bound * 100))
cat("\n")

# Compare two products
products <- data.frame(
  name     = c("Product A", "Product B"),
  positive = c(8, 460),
  total    = c(8, 500),
  stringsAsFactors = FALSE
)

ranked <- compare_products_wilson(products)
cat("Ranking by Wilson Score (best first):\n")
for (i in seq_len(nrow(ranked))) {
  p <- ranked[i, ]
  cat(sprintf("  %d. %-15s raw: %.1f%%   floor: %.1f%%  (%d/%d reviews)\n",
    i, p$name, p$raw_score * 100, p$wilson_lower_bound * 100, p$positive, p$total))
}
cat("\n")

# Visualization
plot_wilson_floor(approval_rate = 0.92)