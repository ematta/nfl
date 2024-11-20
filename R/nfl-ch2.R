library("tidyverse")
library("nflfastR")
library("ggthemes")

pbp_r <- load_pbp(2016:2022)

pbp_r_p <- pbp_r |>
  filter(play_type == "pass" & !is.na(air_yards))

pbp_r_p <-
  pbp_r_p |>
  mutate(
    pass_length_air_yards = ifelse(air_yards >= 20, "long", "short"),
    passing_yards = ifelse(is.na(passing_yards), 0, passing_yards)
  )

pbp_r_p |>
  pull(passing_yards) |>
  summary()

pbp_r_p |>
  filter(pass_length_air_yards == "short") |>
  pull(passing_yards) |>
  summary()

pbp_r_p |>
  filter(pass_length_air_yards == "long") |>
  pull(passing_yards) |>
  summary()

pbp_r_p |>
  filter(pass_length_air_yards == "long") |>
  pull(epa) |>
  summary()

pbp_r_p |>
  filter(pass_length_air_yards == "short") |>
  pull(epa) |>
  summary()

ggplot(pbp_r, aes(x = passing_yards)) + geom_histogram()

pbp_r_p |>
  filter(pass_length_air_yards == "long") |>
  ggplot(aes(passing_yards)) + 
  geom_histogram(binwidth = 1) +
  ylab("Count") +
  xlab("Yards gained or lost during passing plays on long passes") +
  theme_bw()

ggplot(pbp_r_p, aes(x = pass_length_air_yards, y = passing_yards)) + 
  geom_boxplot() +
  theme_bw() +
  ylab("Yards gained or lost during passing plays") +
  xlab("Pass length")

pbp_r_p_s <- pbp_r_p |>
  group_by(passer_player_name, passer_player_id, season) |>
  summarize(
    ypa = mean(passing_yards, na.rm = TRUE),
    n = n(),
    .groups = "drop"
  )
pbp_r_p_s |>
  arrange(-ypa) |>
  print()

pbp_r_p_100 <-
  pbp_r_p |>
  group_by(passer_id, passer, season) |>
  summarize(
    n=n(),
    ypa=mean(passing_yards),
    .groups = "drop"
  ) |>
  filter(n >= 100) |>
  arrange(-ypa)

pbp_r_p_100 |>
  print(n=20)

air_yards_r <- pbp_r_p |>
  select(passer_id, passer, season, pass_length_air_yards, passing_yards) |>
  arrange(passer_id, season, pass_length_air_yards) |>
  group_by(passer_id, passer, pass_length_air_yards, season) |>
  summarize(
    n=n(),
    ypa=mean(passing_yards),
    .groups = "drop"
  ) |>
  filter((n >= 100 & pass_length_air_yards == "short") | (n >= 30 & pass_length_air_yards == "long")) |>
  select(-n)

air_yards_lag <-
  air_yards_r |>
  mutate(season = season + 1) |>
  rename(ypa_last = ypa)

pbp_r_p_s_pl <-
  air_yards_r |>
  inner_join(air_yards_lag, by = c("passer_id", "pass_length_air_yards", "season", "passer"))

pbp_r_p_s_pl |>
  filter(passer %in% c("T.Brady", "A.Rodgers")) |>
  print(n = Inf)

pbp_r_p_s_pl |>
  glimpse()

pbp_r_p_s_pl |>
  distinct(passer_id) |>
  nrow()

scatter_ypa_r <-
  ggplot(pbp_r_p_s_pl, aes(x = ypa_last, y = ypa)) +
  geom_point() +
  facet_grid(cols = vars(pass_length_air_yards)) +
  labs(
    x = "Yards per attempt in previous season",
    y = "Yards per attempt in current season"
  ) +
  theme_bw() +
  theme(strip.background = element_blank())

print(scatter_ypa_r)

scatter_ypa_r +
  geom_smooth(method = "lm")

pbp_r_p_s_pl |>
  filter(!is.na(ypa) & !is.na(ypa_last)) |>
  group_by(pass_length_air_yards) |>
  summarize(correlation = cor(ypa, ypa_last))
