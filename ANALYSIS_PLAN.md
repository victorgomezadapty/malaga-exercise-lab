# Pre-specified analysis plan

Written and saved on 11 Nov 2026 (UTC+3), after the file integrity and structure
checks (row counts, column names, speed profiles of a few tests, missingness) and before any
formula error, zone or peak heart rate result was computed. Any later change is listed at the end
of this file with its reason.

## Question

How far do three common age-predicted maximal heart rate formulas, and training zone boundaries
taken as percentages of those formulas, depart from the peak heart rate observed in the open
University of Malaga treadmill table?

## 1. Codebook and missingness audit

Compare both deposited files with the deposit page: test and person counts, units, Sex coding,
repeated tests, GET index in ID_test, gas missingness (VO2, VCO2, VE), humidity and temperature
missingness, age range and tests under 18, heart rate values that cannot be physiological.
Mismatches are flagged in `tables/` and RESULTS.md. Values are never silently corrected.

## 2. Effort phase rule (fixed before results)

For each test, using treadmill Speed only:

* Peak speed Vmax is the highest speed in the test; t_vmax is the first time it is reached.
* Effort end: the last sample before the first sample after t_vmax whose speed is below
  Vmax minus 1.0 km/h (the drop into recovery). If speed never drops, effort ends at the last sample.
* Warmup speed S0 is the first speed above 0 km/h in the file.
* Effort start: the first sample after the last sample before t_vmax whose speed is at or below
  S0 plus 0.05 km/h. If no such sample exists, the effort starts at the first sample.
* Effort phase: effort start to effort end, inclusive.
* Irregular protocol flags (kept in the primary sample, removed in a sensitivity): warmup speed
  not within 4.5 to 5.5 km/h; effort phase shorter than 180 s; a speed drop of 1.0 km/h or more
  inside the effort phase; no recovery samples after effort end; recovery median speed not within
  3.5 to 5.5 km/h.
* Heart rate below 30 bpm is treated as a recording artefact and set to missing before any peak.
  Counts are reported.

Observed HRpeak (primary): the highest single heart rate value during the effort phase.
Sensitivities: highest heart rate at any time in the file; highest value of a centred rolling
median over 5 consecutive samples during the effort phase (spike robust).

VO2peak (descriptor only, tests with gas data): the highest 30 s time window mean of VO2 during
the effort phase, in mL/min and mL/kg/min.

## 3. Samples

* Primary: for each person, the first test (lowest GET index in ID_test). Kept if age at that
  test is 18 or over.
* Sensitivity A: all adult tests (age 18 or over), with person clustered uncertainty.
* Sensitivity B: first adult test per person (people whose first test was under 18 contribute
  their first adult test).
* Sensitivity C: primary sample without irregular protocol flags.
* Descriptive only: tests under 18 (first test per person). Never pooled into the primary family.

## 4. Formulas (age at the test)

* 220 minus age (Fox, Naughton and Haskell 1971 form)
* Tanaka 2001: 208 minus 0.7 times age
* Gellish 2007: 206.9 minus 0.67 times age

## 5. Primary endpoints, error = formula minus observed HRpeak (bpm)

Signed bias, MAE, RMSE, and the share of tests with absolute error above 10 bpm. 95% CIs:
bias and MAE from an intercept only OLS with HC3 standard errors (cluster robust by person in
Sensitivity A); the proportion by the Wilson interval (person cluster bootstrap in Sensitivity A);
RMSE by a percentile bootstrap, 2000 resamples, seed 20261111 (resampling persons in Sensitivity A).
Descriptive add ons: errors by age band (18 to 29, 30 to 39, 40 and over) and by sex; an OLS
(HC3) line of observed HRpeak on age, described only, never offered as a new formula.

## 6. Zone shift and zone discordance

Zone boundaries at 70% and 85% of HRmax. Boundary shift = boundary from formula HRmax minus
boundary from observed HRpeak, in bpm. Zone discordance: share of effort phase time whose zone
(below 70%, 70 to 85%, above 85%) differs between the formula and the observed HRpeak. Each
sample is weighted by the time to the next sample, capped at 10 s (the last sample takes the
test's median interval). The per test share is averaged across tests (each person equal weight)
with an HC3 95% CI; the direction (formula labels the sample lower or higher) is also reported.
This is a description of discordance, not training advice and not evidence of equivalence.

## 7. Not done

No ventilatory threshold algorithm. No replication of the companion papers.

## Changes after this plan was saved

* No change to the rule, samples, formulas, endpoints or CI methods.
* Added, descriptive only: observed HRpeak by seven narrower age bands for a figure and a table
  (bands with fewer than 10 tests would be suppressed). This is presentation, not a new endpoint.
