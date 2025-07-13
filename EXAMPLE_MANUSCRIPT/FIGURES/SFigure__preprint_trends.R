#!/usr/bin/env Rscript
# SFigure__preprint_trends: Preprint Submission Trends Across Multiple Servers
#
# Publication-ready plot showing the growth of arXiv submissions from 1991 to 2025.
# Optimized for single-column format in academic preprints.
# Runs in headless mode by default (no display window).
# Data source: https://arxiv.org/stats/monthly_submissions.
#
# Usage:
#   Rscript SFigure__preprint_trends.R           # Headless mode (save files only)
#   Rscript SFigure__preprint_trends.R --show    # Display plot and save files
#   Rscript SFigure__preprint_trends.R --help    # Show help message

# Function to check and install required packages
check_and_install_packages <- function(packages) {
  for (pkg in packages) {
    if (!require(pkg, character.only = TRUE)) {
      install.packages(pkg, repos = "https://cloud.r-project.org/")
      library(pkg, character.only = TRUE)
    }
  }
}

# List of required packages
required_packages <- c("ggplot2", "scales", "readr", "dplyr", "optparse", "svglite", "tidyr")
check_and_install_packages(required_packages)

# Ensure svglite is loaded
if (!requireNamespace("svglite", quietly = TRUE)) {
  stop("The 'svglite' package is required for SVG output but is not installed. Please install it with install.packages('svglite').")
} else {
  library(svglite)  # Explicitly load svglite to ensure it is recognized
}

library(ggplot2)
library(scales)
library(readr)
library(dplyr)
library(optparse)
library(tidyr)

# Parse command-line arguments
option_list <- list(
  make_option(c("--show"), action = "store_true", default = FALSE, help = "Display plot"),
  make_option(c("--help"), action = "store_true", default = FALSE, help = "Show help message")
)
opt <- parse_args(OptionParser(option_list = option_list))

if (opt$help) {
  cat("Usage: Rscript SFigure__preprint_trends.R [--show] [--help]\n")
  cat("  --show: Display plot (default is headless mode)\n")
  cat("  --help: Show this help message\n")
  quit(status = 0)
}

# Load and process data
load_and_process_data <- function() {
  # Get the directory of the current script
  script_args <- commandArgs(trailingOnly = FALSE)
  script_path <- normalizePath(sub("--file=", "", script_args[grep("--file=", script_args)]))
  script_dir <- dirname(script_path)

  # Define the path to the data file
  data_path <- file.path(script_dir, "DATA", "SFigure__preprint_trends", "pubmed_by_year.csv")

  # Check if the file exists
  if (!file.exists(data_path)) {
    stop(paste("Error: Data file not found at", data_path))
  }

  # Load and process the data
  df <- read_csv(data_path, show_col_types = FALSE)  # Suppress column type messages
  df <- df %>%
    pivot_longer(cols = c(preprint, medrxiv, biorxiv, arxiv), names_to = "source", values_to = "submissions") %>%
    mutate(date = as.Date(paste0(Year, "-01-01"), format = "%Y-%m-%d")) %>%  # Convert year to Date
    arrange(date, source)  # Ensure proper ordering
  return(df)
}

# Create the figure
create_figure <- function(df) {
  p <- ggplot(df, aes(x = date, y = submissions, color = source, fill = source)) +
    geom_line(size = 0.6, alpha = 0.8) +
    geom_area(alpha = 0.2, position = "identity") +  # Use "identity" to avoid stacking
    labs(
      title = "PubMed Preprints by Year and Source",
      x = "Year",
      y = "Submissions",
      color = "Source",
      fill = "Source"
    ) +
    scale_x_date(
      date_breaks = "1 year",
      date_labels = "%Y"
    ) +
    scale_y_continuous(
      labels = scales::comma,
      expand = expansion(mult = c(0, 0.05))
    ) +
    theme_minimal(base_size = 8) +
    theme(
      axis.title = element_text(face = "bold"),
      plot.title = element_text(face = "bold", size = 10, hjust = 0.5),
      panel.grid.minor = element_line(size = 0.3, linetype = "dotted"),
      panel.grid.major = element_line(size = 0.3),
      axis.text.x = element_text(angle = 45, hjust = 1)
    )
  return(p)
}

# Save the figure
save_figure <- function(p, output_path = NULL) {
  output_path <- ifelse(is.null(output_path), getwd(), output_path)

  # Ensure the output directory exists
  if (!dir.exists(output_path)) {
    dir.create(output_path, recursive = TRUE)
  }

  # Save the figure in multiple formats
  ggsave(file.path(output_path, "SFigure__preprint_trends.pdf"), plot = p, width = 3.5, height = 4, dpi = 300)
  ggsave(file.path(output_path, "SFigure__preprint_trends.png"), plot = p, width = 3.5, height = 4, dpi = 300)

  # Use svglite for SVG output
  ggsave(file.path(output_path, "SFigure__preprint_trends.svg"), plot = p, width = 3.5, height = 4, device = svglite::svglite)

  cat("Figure saved to:\n")
  cat(paste0("  - ", file.path(output_path, "SFigure__preprint_trends.pdf"), "\n"))
  cat(paste0("  - ", file.path(output_path, "SFigure__preprint_trends.png"), "\n"))
  cat(paste0("  - ", file.path(output_path, "SFigure__preprint_trends.svg"), "\n"))
}

# Main function
main <- function() {
  df <- load_and_process_data()
  p <- create_figure(df)
  save_figure(p)
  if (opt$show) {
    print(p)
  }
}

main()
