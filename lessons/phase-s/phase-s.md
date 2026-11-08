# Phase S · Statistics and probability

Almost every claim you will meet about AI is a statistical claim: a benchmark score, a scaling law, an error rate, a comparison between two models, the probability a language model gives to a sentence. Phase S teaches the statistics and probability needed to make and judge such claims, starting from zero and using the data of the journal *Bibliothecae\.it* throughout.

Every concept follows the same steps: the idea in plain words; a picture or a slider to play with; the formula, read symbol by symbol; a tiny example worked by hand; and the same in code, on real data. The phase has 42 lessons in six parts, about 110 hours in all. There are no deadlines: the hours are only there to help you plan.

The lessons are being written in order. Those not yet written are listed so that you can see where each idea leads.

## Part 0 · The maths toolkit

| Lesson | What you learn | Status |
| --- | --- | --- |
| [S0.1 · Reading formulas](s0-1-reading-formulas.ipynb) | Subscripts, the Σ and Π signs, long formulas read from the inside out, indicators, proportions, percentages and percentage points | ready (1.5 h) |
| [S0.2 · Powers, exponentials and logarithms](s0-2-powers-and-logarithms.ipynb) | Powers and roots, exponential growth and decay, logarithms and their rules, orders of magnitude, log axes | ready (2.5 h) |
| [S0.3 · Functions and graphs](s0-3-functions-and-graphs.ipynb) | Functions and their graphs, slope and intercept, power and exponential functions, straight lines on log axes, Zipf's law | ready (2 h) |

## Part 1 · Describing data

| Lesson | What you learn | Status |
| --- | --- | --- |
| [S1.1 · Data, variables and measurement](s1-1-data-variables-measurement.ipynb) | Units, observations and variables; variable types; tidy tables; population and sample; validity, reliability and missing values | ready (2.5 h) |
| [S1.2 · Counting and tables](s1-2-counting-and-tables.ipynb) | Frequency tables, the mode, bar charts, two-way tables, row and column percentages | ready (2 h) |
| S1.3 · Distributions and their shape | Histograms, density, skew, outliers, box plots, the ECDF | planned (2.5 h) |
| S1.4 · The centre: mean, median and mode | Weighted and trimmed means; robustness and the breakdown point | planned (2.5 h) |
| S1.5 · Spread and position | Variance and standard deviation, IQR, MAD, percentiles, z-scores | planned (2.5 h) |
| S1.6 · Skew, heavy tails and log scales | Log transforms, log-spaced histograms, the CCDF on log–log axes | planned (2.5 h) |
| S1.7 · Concentration and inequality | Top shares, the Lorenz curve, the Gini coefficient | planned (2 h) |
| S1.8 · Two variables together | Scatter plots, covariance, Pearson and rank correlations, association in tables | planned (3 h) |
| S1.9 · Comparing groups and Simpson's paradox | Confounding, Simpson's paradox, field-normalised scores | planned (2.5 h) |
| S1.10 · Project 1: a portrait of Bibliothecae\.it | Part 1 applied to the journal, with Lotka's, Bradford's and Zipf's laws described | planned (3 h) |

## Part 2 · Probability

| Lesson | What you learn | Status |
| --- | --- | --- |
| S2.1 · Chance and simulation | Experiments, events, probability, random numbers and seeds, Monte Carlo | planned (2 h) |
| S2.2 · Rules of probability | Complements, unions and intersections, counting | planned (2 h) |
| S2.3 · Conditional probability and independence | Two-way tables, trees, the law of total probability | planned (2.5 h) |
| S2.4 · Bayes' theorem and base rates | Sensitivity, specificity, precision, the base-rate fallacy | planned (2.5 h) |
| S2.5 · Random variables and expected value | Probability mass functions, expected value, variance | planned (2.5 h) |
| S2.6 · Distributions for counts and choices | Binomial, categorical, Poisson, negative binomial | planned (3 h) |
| S2.7 · Continuous distributions | Normal, exponential, lognormal, power law; inverse-transform sampling | planned (3 h) |
| S2.8 · Where heavy tails come from | Multiplicative growth, cumulative advantage, the Matthew effect | planned (2.5 h) |
| S2.9 · Joint distributions and the chain rule: language models | The chain rule, a bigram model, softmax and temperature | planned (3 h) |
| S2.10 · Many draws | The law of large numbers, the central limit theorem, standard errors | planned (2.5 h) |
| S2.11 · Surprise and information | Entropy, cross-entropy, KL divergence, perplexity | planned (2.5 h) |

## Part 3 · Estimation

| Lesson | What you learn | Status |
| --- | --- | --- |
| S3.1 · Populations, samples and bias | Sampling frames and designs; selection, survivorship and coverage bias | planned (2.5 h) |
| S3.2 · Estimators and their errors | Bias, variance, mean squared error, standard error | planned (2.5 h) |
| S3.3 · Confidence intervals | Coverage, intervals for means and proportions, sample size | planned (3 h) |
| S3.4 · The bootstrap | Resampling intervals for medians, Gini coefficients, correlations | planned (2 h) |
| S3.5 · Likelihood and maximum likelihood | Log-likelihood, numerical fitting, cross-entropy | planned (3 h) |
| S3.6 · Fitting and comparing distributions | Poisson to power law; QQ plots, likelihood ratios, AIC | planned (2.5 h) |
| S3.7 · Accuracy and agreement | Confusion matrix, precision, recall, F1, Cohen's kappa, calibration | planned (3 h) |

## Part 4 · Testing and comparing

| Lesson | What you learn | Status |
| --- | --- | --- |
| S4.1 · The logic of a test | Hypotheses, permutation tests, p-values, errors of type I and II | planned (3 h) |
| S4.2 · Common tests | t-tests, Mann–Whitney, chi-squared, Fisher, McNemar | planned (2.5 h) |
| S4.3 · Effect sizes and power | Cohen's d, risk and odds ratios, power by simulation | planned (2.5 h) |
| S4.4 · Many tests and the replication crisis | Multiple comparisons, false discovery rate, p-hacking, preregistration | planned (2.5 h) |
| S4.5 · Comparing AI systems fairly | Paired comparisons, variation across runs, benchmarks, contamination | planned (2.5 h) |

## Part 5 · Modelling

| Lesson | What you learn | Status |
| --- | --- | --- |
| S5.1 · Fitting a line | Least squares, residuals, R², regression to the mean | planned (3 h) |
| S5.2 · Several predictors | Multiple regression, interactions, overfitting, training and test sets | planned (3 h) |
| S5.3 · Counts and yes-or-no outcomes | Logistic, Poisson and negative binomial regression | planned (3 h) |
| S5.4 · Bayesian inference | Priors and posteriors, credible intervals, PyMC | planned (3 h) |
| S5.5 · Causal thinking | Experiments, causal diagrams, confounders and colliders | planned (3 h) |
| S5.6 · Project 2: a question of your own | An end-to-end study of the journal's data | planned (4 h or more) |
