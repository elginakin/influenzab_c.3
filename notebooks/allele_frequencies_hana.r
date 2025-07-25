# --- Load Libraries ---
library(Biostrings)
library(tidyverse)
library(streamgraph)  # for geom_stream
library(ggstream)     # more flexible stream plots (preferred over streamgraph)

# --- Function 1: Parse FASTA into long residue-position table ---
parse_alignment <- function(fasta_file, positions = NULL, position_range = NULL) {
  aln <- readAAStringSet(fasta_file)
  seq_df <- tibble(sample_ID = names(aln), sequence = as.character(aln))

  wide_df <- seq_df %>%
    mutate(residues = strsplit(sequence, split = "")) %>%
    unnest_longer(residues, indices_to = "position") %>%
    mutate(position = position + 1)  # 1-based indexing

  if (!is.null(position_range)) {
    wide_df <- wide_df %>% filter(position >= position_range[1], position <= position_range[2])
  }
  if (!is.null(positions)) {
    wide_df <- wide_df %>% filter(position %in% positions)
  }

  return(wide_df)
}

# --- Function 2: Join metadata and summarize allele frequencies ---
summarize_alleles_over_time <- function(
  alignment_df,
  metadata_file,
  date_col = "date",
  date_range = NULL
) {
  metadata <- read_tsv(metadata_file, show_col_types = FALSE) %>%
    select(sample_ID, date = all_of(date_col)) %>%
    mutate(
      date = if_else(
        str_detect(date, "^2025-..-..$") & !str_detect(date, "^2025-\\d{2}-\\d{2}$"),
        "2025-01-01",
        date
      ),
      date = as.Date(date)
    )

  alignment_df <- alignment_df %>%
    left_join(metadata, by = "sample_ID") %>%
    drop_na(date)

  if (!is.null(date_range)) {
    alignment_df <- alignment_df %>%
      filter(date >= as.Date(date_range[1]) & date <= as.Date(date_range[2]))
  }

  allele_df <- alignment_df %>%
    group_by(sample_ID, date) %>%
    summarize(
      allele_combo = paste0(residues, collapse = ""),
      .groups = "drop"
    )

  allele_counts <- allele_df %>%
    group_by(date, allele_combo) %>%
    tally(name = "count") %>%
    ungroup()

  return(allele_counts)
}

# --- Function 3: Plot raw counts as streamgraph ---

plot_allele_counts <- function(count_df, color_map = NULL) {
  p <- ggplot(count_df, aes(x = date, y = count, fill = allele_combo)) +
    geom_stream(bw = 1.2, type = "proportional", sorting = "inside_out") +
    scale_y_continuous(expand = expansion(mult = c(0, 0.05))) +
    scale_x_date(date_labels = "%b\n%y", expand = expansion(mult = c(0.01, 0.05))) +
    labs(x = "Sequencing Date", y = "Allele Proportion", fill = "Allele") +
    theme_classic(base_size = 14) +
    theme(
      legend.position = "none",
        axis.title = element_text(size = 18, face = "bold"),
        axis.text = element_text(size = 16),
        legend.text = element_text(size = 15),
        legend.title = element_text(size = 15))
  
  if (!is.null(color_map)) {
    p <- p + scale_fill_manual(values = color_map)
  }

  return(p)
}

# --- Run ---
## Make HA Plots

# 1. Parse  FASTA
ha_aln_df <- parse_alignment(
  fasta_file = "results/ha_nextclade_complete/nextclade.cds_translation.HA1_jhhonly.fasta",
  position_range = c(198, 200)
)

# 2. Summarize alleles
ha_allele_counts <- summarize_alleles_over_time(
  alignment_df = ha_aln_df,
  metadata_file = "results/ha_nextclade_complete/filtered.tsv",
  date_range = c("2023-10-01", "2025-05-01")
)

# 3. Plot

## HA colors
ha_colors <- c(
  # glycan
  "NET" = "#FF746C",
  # no glycans
  "EET" = "#3a3a3a",
  "EEI" = "#838383",
  "DET" = "#aeaeae",
  ## minor alleles 
  "EEA" = "#c9c9c9",
  "EKT" = "#e5e5e5",
  "EGT" = "#cfd8dc"
)

# 1. Parse  FASTA
ha_aln_df <- parse_alignment(
  fasta_file = "results/ha_nextclade_complete/nextclade.cds_translation.HA1_jhhonly.fasta",
  position_range = c(198,200)
)

# 2. Summarize alleles
ha_allele_counts <- summarize_alleles_over_time(
  alignment_df = ha_aln_df,
  metadata_file = "results/ha_nextclade_complete/filtered.tsv",
  date_range = c("2023-10-01", "2025-05-01")
)

# 3. Plot
ha = plot_allele_counts(ha_allele_counts, color_map = ha_colors) # color_map = ha_colors

## NA Plots

# 1. Parse the FASTA 
na_aln_df <- parse_alignment(
  fasta_file = "results/na_nextclade_complete/nextclade.cds_translation.NA_jhhonly.fasta",
  positions = c(187,396)
)

# 2. Summarize alleles
na_allele_counts <- summarize_alleles_over_time(
  alignment_df = na_aln_df,
  metadata_file = "results/na_nextclade_complete/filtered.tsv",
  date_range = c("2023-10-01", "2025-07-01")
)

# 3. Plot

## NA colors
na_colors <- c(
  "SI" = "#DF8F5599",
  "KV" = "#7BB6AD",
  "KI" = "#FFDC91FF",
  "RI" = "#7876B1FF" # possible loss of NAI 
)

na = plot_allele_counts(na_allele_counts, color_map = na_colors)

ggsave("figures/ha_197-199_alleles.png", ha, width = 4, height = 4)
ggsave("figures/na_186-395_alleles.png", na, width = 4, height = 4)

ha
na

