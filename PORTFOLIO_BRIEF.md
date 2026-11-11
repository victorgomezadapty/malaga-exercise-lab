Málaga Exercise Lab: locked facts for a later bilingual portfolio case.
Status: public on GitHub at https://github.com/victorgomezadapty/malaga-exercise-lab. Do not invent links or numbers.
Do not use double hyphens or long dashes in any copy, titles, commit messages or pull request titles. Write ranges as "18.0 to 63.0" and intervals as "95% CI 2.3 to 3.8" (in Spanish with decimal commas: "IC 95 %: 2,3 a 3,8"). A hyphen is fine only in names such as CC BY-NC-SA or 220-age.

Links:
- publicLink: null (no new Vercel project, no dedicated site)
- datasetLink: the PhysioNet page only, https://physionet.org/content/treadmill-exercise-cardioresp/1.0.1/ (no Kaggle dataset, no Kaggle notebook, never a copy of the CSV files)
- sourceLink: https://github.com/victorgomezadapty/malaga-exercise-lab (code, aggregate tables and figures only; both CSV files gitignored)
- No raw files on the portfolio page or in public/ assets

Official deposit title (use it, not only the short name): "Treadmill Maximal Exercise Tests from the Exercise Physiology and Human Performance Lab of the University of Malaga", PhysioNet version 1.0.1, DOI 10.13026/7ezk-j442, concept DOI 10.13026/94yv-6145, published 10 December 2021, open access.
Creators, in this order: Denis Mongin, Jeronimo García Romero, Jose Ramon Alvero Cruz.
"Málaga Exercise Lab" is only this project's short name.

License wording (must be stated, not simplified): the deposited LICENSE.txt is CC BY-NC-SA 4.0, but the PhysioNet project card lists the PhysioNet Contributor Review Health Data License 1.5.0 and a Data Use Agreement that forbids sharing the data. This project does not redistribute either CSV file. Figures are aggregate research results with attribution; do not label them CC BY 4.0.

Framing (title, summary, notice, evidence, limitations, role must stay honest):
- A transparent re-analysis of one open treadmill table, not a new study and not a replication of the companion papers (dynamical analysis of HR and VO2, Scientific Reports 2020 and Physiological Measurement 2020; heart rate recovery methods, Research in Sports Medicine). Cite only; never compare to or claim to beat them.
- The differential: how far three age-predicted HRmax formulas, and zones at 70% and 85% of HRmax, depart from the observed effort phase HRpeak.
- Not clinical advice, not a training prescription, not a new formula, not evidence of equivalence.
- Aggregates only. No IDs, no individual traces, minors only as a group.

Locked results (primary: adults 18 and over, first test per person, n = 735 tests and 735 people, 102 women, age 18.0 to 63.0; error = formula minus observed HRpeak, 95% CI):
- 220 minus age: bias 3.0 (2.3 to 3.8) bpm, MAE 8.2 (7.8 to 8.7), RMSE 10.5 (9.9 to 11.1), abs error > 10 bpm in 30.5% (27.3 to 33.9).
- Tanaka 2001 (208 - 0.7 x age): bias 0.4 (-0.3 to 1.1), MAE 7.1 (6.7 to 7.6), RMSE 9.2 (8.6 to 9.8), > 10 bpm in 26.3% (23.2 to 29.6).
- Gellish 2007 (206.9 - 0.67 x age): bias 0.2 (-0.4 to 0.9), MAE 7.1 (6.7 to 7.5), RMSE 9.2 (8.6 to 9.8), > 10 bpm in 26.7% (23.6 to 30.0).
- Zone discordance, mean share of effort phase time per test labelled in a different zone: 220 minus age 14.7% (13.7 to 15.7), Tanaka 12.4% (11.5 to 13.2), Gellish 12.3% (11.5 to 13.1).
- 85% boundary shift with 220 minus age: mean 2.6 bpm (2.0 to 3.2), 10th to 90th percentile -7.4 to 13.3.
- Descriptive: 220 minus age bias falls from 8.5 bpm (18 to 21 years) to -4.1 bpm (45 and over).
- Sensitivities move bias by less than 0.5 bpm and MAE by less than 0.2 bpm.
- Audit flags, none corrected: VO2 and VCO2 missing in 11 tests, not 30 as stated, VE never missing; GET index not a running count; 145 tests under 18; humidity and temperature missing in 30 rows; 53 HR values below 30 bpm set to missing in memory.

Suggested headline metric: MAE about 7 bpm and about 1 test in 4 off by more than 10 bpm even for the best formulas (Tanaka 26.3%), not the near zero average bias alone. Second metric: zone discordance 12.4% (Tanaka). Third: n = 735.

Figures (aggregate only, PNG and WebP in figures/; footer cites Mongin, García Romero and Alvero Cruz 2021, PhysioNet, doi 10.13026/7ezk-j442, "Aggregates only, no individual rows"):
- Cover: fig03_formula_error, four bar panels (bias, MAE, RMSE, % > 10 bpm) for three formulas with 95% CIs, n = 735.
- Pair: fig05_zone_discordance, time in zones by HRmax source and per test share with a different zone label.
- Also: fig01_deposit_audit, fig02_effort_phase_rule (schematic, not participant data), fig04_hrpeak_by_age_band, fig06_sensitivity.
- If the page footer says "Local draft", replace only that word when it becomes public, by regenerating, not by editing images.

Limitations to state: one lab, mostly athletes, mostly men (102 of 735 women in the primary sample); treadmill protocols vary and some are flagged as irregular; HRpeak depends on the effort phase rule; breath by breath HR may include artefacts; the license terms of the deposit are contradictory; results describe this table only.

Spanish copy reminder: decimal commas (3,0 lpm; 26,3 %), "IC 95 %", same honesty limits.


Discussion zone for the portfolio case (add this on the case page, not on a new Vercel site).
Literature search: November 2026. Cite only; do not reuse paper text, tables or figures.
Do not present this as a systematic review. Do not recommend a formula for training or clinical use.
The search does not change the locked primary numbers above.

Portfolio UI (required for this case): add optional fields so a "Discussion" / "Discusión" zone can
render on the project page when present, without changing other cases.
- discussion: { en, es } as several short paragraphs (preserve paragraph breaks).
- openQuestions: { en: string[], es: string[] }.
- Place the zone after "Data or evidence used" and before "Limitations". Title: "Discussion" /
  "Discusión". A one-line kicker is fine: "Literature search, November 2026" /
  "Búsqueda bibliográfica, noviembre de 2026".
- Then a short heading "What remains to investigate" / "Qué queda por investigar" and the
  numbered open questions.
- Existing limitations and nextStep fields stay. nextStep should point to the first open question
  (threshold concordance on this table), not repeat the whole list.
- Add the verified DOI references below to the case references list. Link DISCUSSION.md on the
  public GitHub repository once that URL exists. Still no publicLink and no Kaggle.

English discussion:

This re-analysis lines up with a result that recent papers keep finding: age-predicted maximal
heart rate formulas can look acceptable on average and still miss the person in front of you.
Martin, Lindsey, Gerrity and Ambegaonkar (2025), in 230 healthy adults (174 men and 56 women),
also reported small mean biases (about -3 to +6 bpm) with wide 95% limits of agreement (about
18 to 24 bpm either side of the mean). Arena, Tanaka and Gellish had the lowest absolute error;
none of the equations was accurate at the individual level, and cardiorespiratory fitness added
little. In this open table, Tanaka and Gellish sit near zero mean bias (0.4 and 0.2 bpm), but
the mean absolute error is 7.1 bpm, and more than one test in four is off by more than 10 bpm
(26.3% and 26.7%). For 220 minus age the mean bias is 3.0 bpm (2.3 to 3.8) and 30.5% (27.3 to
33.9) exceed 10 bpm. The practical message is the same, in a different sample, with an
effort-phase peak rule fixed before the results were computed.

Kasiak, Wiecha, Cieśliński, Takken, Lach, Lewandowski and colleagues (2023) validated models in
4043 runners and 1026 cyclists: RMSE was 9.1 to 10.5 bpm, close to the 9.2 to 10.5 bpm found
here, and women were only 15.01% of that sample. This primary sample has the same limit (102
women of 735), so sex-specific accuracy remains weakly estimated. Lach, Wiecha, Śliż, Price,
Zaborski, Cieśliński and colleagues (2021), in 3374 mostly athletic clinic clients, found that
adding body composition, VO2max, sex and ergometer improved prediction only slightly over age
alone (R-squared 0.22; mean absolute error 7.04 bpm), and that 220 minus age could reach mean
errors of up to 9 bpm. The 220 minus age pattern in this table (bias 8.5 bpm at 18 to 21 years,
falling to -4.1 bpm at 45 and over) matches Tanaka, Monahan and Seals (2001), Gellish and
colleagues (2007), and the review by Almaadawy, Uretsky, Krittanawong and Birnbaum (2024), who
also question a rigid 85% cutoff of age-predicted maximal heart rate and note that validation
in people aged 60 and over is still weak. The present 45-and-over band has only 63 people and
stops at age 63.0, so that gap is not closed here.

What this project adds, and what the companion papers on this deposit do not address, is zone
discordance at 70% and 85% of maximal heart rate: on average, 14.7% (13.7 to 15.7) of effort
time would change zone label with 220 minus age, 12.4% (11.5 to 13.2) with Tanaka and 12.3%
(11.5 to 13.1) with Gellish. That is not a ventilatory threshold analysis and not a training
prescription. Meixner, Filipas, Holmberg and Sperlich (2025) show that fixed percentages of
maximal heart rate also scatter against the first ventilatory threshold or maximal fat
oxidation. Whether formula-based zones also miss metabolic thresholds in this same Malaga table
remains open: thresholds were not computed here, by design. This deposit is mostly athletic
treadmill tests. Han, Choi, Kim and colleagues (2022) found that age-predicted maximal heart
rate differed from the measured peak in patients with heart or lung disease, especially among
those taking beta-blockers. This table does not answer that clinical question.

Spanish discussion (decimal commas, "IC 95 %", "lpm"):

Este reanálisis se alinea con un resultado que la literatura reciente sigue encontrando: las
fórmulas de frecuencia cardíaca máxima por edad pueden verse aceptables en media y, aun así,
fallar en la persona concreta. Martin, Lindsey, Gerrity y Ambegaonkar (2025), en 230 adultos
sanos (174 hombres y 56 mujeres), también hallaron sesgos medios pequeños (unos -3 a +6 lpm)
con límites de acuerdo del 95 % amplios (unos 18 a 24 lpm a cada lado de la media). Arena,
Tanaka y Gellish tuvieron el menor error absoluto; ninguna ecuación fue precisa a nivel
individual, y la aptitud cardiorrespiratoria aportó poco. En esta tabla abierta, Tanaka y
Gellish quedan cerca de sesgo cero (0,4 y 0,2 lpm), pero el error absoluto medio es de 7,1 lpm
y más de uno de cada cuatro tests se desvía más de 10 lpm (26,3 % y 26,7 %). Con 220 menos la
edad el sesgo medio es 3,0 lpm (2,3 a 3,8) y el 30,5 % (27,3 a 33,9) supera los 10 lpm. El
mensaje práctico es el mismo, en una muestra distinta y con una regla de pico de esfuerzo
fijada antes de calcular los resultados.

Kasiak, Wiecha, Cieśliński, Takken, Lach, Lewandowski y colegas (2023) validaron modelos en
4043 corredores y 1026 ciclistas: el RMSE fue de 9,1 a 10,5 lpm, cercano al de 9,2 a 10,5 lpm
de este caso, y las mujeres fueron solo el 15,01 % de esa muestra. Aquí hay 102 mujeres de 735,
así que la precisión por sexo sigue mal estimada. Lach, Wiecha, Śliż, Price, Zaborski,
Cieśliński y colegas (2021), en 3374 clientes de una clínica deportiva, vieron que añadir
composición corporal, VO2máx, sexo y ergómetro mejora solo un poco respecto a la edad sola
(R cuadrado 0,22; error absoluto medio 7,04 lpm) y que 220 menos la edad puede llegar a unos
9 lpm de error medio. El patrón de 220 menos la edad en esta tabla (sesgo 8,5 lpm entre 18 y
21 años, y -4,1 lpm a partir de 45) coincide con Tanaka, Monahan y Seals (2001), con Gellish y
colegas (2007) y con la revisión de Almaadawy, Uretsky, Krittanawong y Birnbaum (2024), que
además cuestionan el corte rígido al 85 % de la máxima predicha y señalan que la validación en
personas de 60 años o más sigue siendo débil. En este análisis el grupo de 45 años o más tiene
solo 63 personas y llega hasta 63,0 años, así que ese hueco no se cierra aquí.

Lo que este proyecto aporta, y lo que los artículos compañeros del depósito no abordan, es la
discordancia de zonas al 70 % y al 85 % de la frecuencia cardíaca máxima: de media, el 14,7 %
(13,7 a 15,7) del tiempo de esfuerzo cambiaría de etiqueta con 220 menos la edad, el 12,4 %
(11,5 a 13,2) con Tanaka y el 12,3 % (11,5 a 13,1) con Gellish. Eso no es un análisis de umbral
ventilatorio ni una pauta de entrenamiento. Meixner, Filipas, Holmberg y Sperlich (2025)
muestran que los porcentajes fijos de la máxima también se dispersan frente al primer umbral
ventilatorio o a la oxidación máxima de grasa. Si esas zonas basadas en fórmula también fallan
los umbrales metabólicos en esta misma tabla de Málaga sigue abierto: aquí no se calcularon
umbrales, a propósito. Este depósito es sobre todo de pruebas atléticas en tapiz. Han, Choi,
Kim y colegas (2022) hallaron que la máxima predicha por edad difiere de la medida en pacientes
con enfermedad cardíaca o pulmonar, sobre todo con betabloqueantes. Esta tabla no responde esa
pregunta clínica.

English open questions:
1. Threshold concordance on this same table: a pre-specified ventilatory or lactate threshold
   rule, or heart rate reserve, versus 70% and 85% of both the observed peak and each formula.
2. Sex-specific accuracy, with enough women (here 102 of 735; Kasiak et al., 2023, had 15.01%).
3. People under 18, in a clearly labelled analysis; the 122 first tests under 18 stayed
   descriptive and were not pooled into the primary family.
4. Older adults, especially 60 and over; the present 45-and-over band has only 63 people and
   stops at 63.0 years.
5. Whether fitness, body composition or modality improves prediction by a practically useful
   margin, with the 11 tests that lack VO2 and VCO2 handled as a pre-specified exclusion.
6. Repeat-test stability of the formula error in the 116 people with more than one test.
7. A clearer maximal-effort rule (respiratory exchange ratio or a heart-rate plateau) versus
   the effort-phase peak used here, because some apparent error may be a submaximal test.
8. Clinical and medicated populations, including beta-blockers; this athletic deposit does not
   substitute for that work.

Spanish open questions:
1. Concordancia de umbrales en esta misma tabla: una regla de umbral ventilatorio o de lactato
   fijada de antemano, o la reserva de frecuencia cardíaca, frente al 70 % y al 85 % del pico
   observado y de cada fórmula.
2. Precisión según el sexo, con suficientes mujeres (aquí 102 de 735; Kasiak et al., 2023,
   tenían el 15,01 %).
3. Menores de 18 años, en un análisis claramente etiquetado; los 122 primeros tests de menores
   se dejaron solo descriptivos y no se mezclaron con la familia primaria.
4. Adultos mayores, sobre todo de 60 años o más; el grupo de 45 años o más tiene solo 63
   personas y llega hasta 63,0 años.
5. Si la aptitud, la composición corporal o la modalidad mejoran la predicción de forma útil
   en la práctica, tratando los 11 tests sin VO2 y VCO2 como una exclusión fijada de antemano.
6. Estabilidad del error de la fórmula en las 116 personas con más de un test.
7. Un criterio más claro de esfuerzo máximo (cociente respiratorio o meseta de frecuencia
   cardíaca) frente al pico de la fase de esfuerzo usado aquí, porque parte del error aparente
   puede ser un test no maximal.
8. Poblaciones clínicas y con medicación, incluidos los betabloqueantes; este depósito atlético
   no sustituye ese trabajo.

Suggested nextStep (short):
en: Compare a pre-specified ventilatory or lactate threshold rule, or heart rate reserve, with
zones at 70% and 85% of both the observed peak and each formula, on this same table.
es: Comparar, en esta misma tabla, una regla de umbral ventilatorio o de lactato fijada de
antemano, o la reserva de frecuencia cardíaca, con las zonas al 70 % y al 85 % del pico
observado y de cada fórmula.

Verified discussion references (use DOI URLs; include formula and deposit cites already listed):
- Martin et al. (2025), PLOS One, https://doi.org/10.1371/journal.pone.0335842
- Lach et al. (2021), Frontiers in Physiology, https://doi.org/10.3389/fphys.2021.695950
- Kasiak et al. (2023), Journal of Clinical Medicine, https://doi.org/10.3390/jcm12082884
- Almaadawy et al. (2024), Journal of Clinical Medicine, https://doi.org/10.3390/jcm13185562
- Meixner et al. (2025), Translational Sports Medicine, https://doi.org/10.1155/tsm2/2008291
- Han et al. (2022), Annals of Rehabilitation Medicine, https://doi.org/10.5535/arm.21181
- Tanaka et al. (2001), https://doi.org/10.1016/S0735-1097(00)01054-8
- Gellish et al. (2007), https://doi.org/10.1097/mss.0b013e31803349c6
