library(tidyverse)

set.seed(42)

npart <- 100
steps <- seq(4000, 6000, by = 50)
rounds <- 10

pool <- c(
  rep(steps, each = 24), seq(4150, 4850, by = 100), seq(5150, 5850, by = 100)
)
length(pool)
mean(pool)
table(pool)

deduct_draw <- function(d, p) {
  tab <- c(
    table(p[p %in% intersect(p,d)]) - table(d), table(p[!p %in% intersect(p,d)])
  )
  rep(as.integer(names(tab)), tab)
}

is_unif <- function(x) {
  x <- factor(x, levels = steps)
  suppressWarnings(chisq.test(table(x))$p.value > 0.1)
}

draw_part <- function(pool) {
  while (TRUE) {
    draw <- sample(pool, rounds - 1)
    npool <- deduct_draw(draw, pool) 
    if (sum(draw) <= 5000*rounds - 4000 & 
        sum(draw) >= 5000*rounds - 6000 & (5000*rounds - sum(draw)) %in% npool) {
      draw <- c(draw, 5000*rounds - sum(draw))
      if (is_unif(draw)) break      
    }
  }
  draw
}

dta <- matrix(NA_integer_, npart, rounds)

cpool <- pool
for (i in 1:npart) {
  dta[i,] <- draw_part(cpool)
  cpool <- deduct_draw(dta[i,], cpool)
}

while(TRUE) {
  cs <- 1:rounds
  cm = colMeans(dta)
  if (any(cm == 5000)) {
    message(sprintf("Found %d valid rounds.", length(which(cm == 5000))))
    cs <- setdiff(cs, which(cm == 5000))
    if (length(cs) == 0) break
  }
  for (i in 1:npart) dta[i, cs] <- sample(dta[i, cs])
}


stopifnot(all(apply(dta, 1, is_unif)))
stopifnot(all(apply(dta, 2, is_unif)))
stopifnot(all(rowMeans(dta) == mean(steps)))
stopifnot(all(colMeans(dta) == mean(steps)))
stopifnot(all(table(dta) == table(pool)))

colnames(dta) <- paste0("V", 1:rounds)
rownames(dta) <- paste0("P", 1:npart)
df <- as_tibble(dta, rownames = "part") %>% 
  pivot_longer(
    starts_with("V"), values_to = "true_amount", names_to = "round", 
    names_prefix = "V", names_transform = as.integer
  ) 

write_csv(df, "data/generated/honesty_true_amounts.csv")
