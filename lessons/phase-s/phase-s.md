# Phase S · Statistics and probability

Almost every claim you will meet about AI is a statistical claim: a benchmark score, a scaling law, an error rate, a comparison between two models, the probability that a language model assigns to a sentence. Phase S builds the statistical reasoning needed to make and judge such claims, on the kind of data you work with: skewed, messy, bibliographic.

The phase follows one rule: **simulate first, formula second.** You generate data whose truth you know, see what a method recovers, and only then apply it to real data.

| Module | Topic | Status |
| --- | --- | --- |
| **S1** | Describing data and the bibliometric laws | ready |
| S2 | Probability and language models | planned |
| S3 | Estimation, sampling, the bootstrap and maximum likelihood | planned |
| S4 | Testing, power, multiple comparisons and preregistration | planned |
| S5 | Regression, GLMs, Bayesian inference and causal inference, with an open access citation advantage project | planned |

## S1 · Describing data and the bibliometric laws

About one week of work (8–10 hours), in four parts:

| Part | What you do | Time |
| --- | --- | --- |
| [S1.1 · Centre, spread and shape](s1-1-centre-spread-shape.ipynb) | Medians and percentiles instead of means; histograms, ECDFs and CCDFs | 2 h |
| [S1.2 · Concentration and association](s1-2-concentration-association.ipynb) | Lorenz curves and the Gini coefficient; Pearson and Spearman; Simpson's paradox and field normalisation | 2 h |
| [S1.3 · Heavy tails and the laws of bibliometrics](s1-3-heavy-tails-laws.ipynb) | Cumulative advantage; fitting and testing power laws; Lotka, Bradford and Zipf (on Dante) | 3 h |
| [S1.4 · Project: the shape of Bibliothecae\.it](s1-4-project-bibliothecae.ipynb) | The whole toolkit on your own data, and a write-up | 3 h |

**You need:** Python and a little pandas. No statistics beyond school.

**You will be able to:** describe skewed bibliographic data honestly, measure concentration, avoid the classic traps of correlation and aggregation, fit and test heavy-tailed distributions, and explain why each of these matters when AI systems are built and evaluated.
