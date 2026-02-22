# Page 38

38
IX. COMPUTATIONAL SYSTEMATICS
Given the very large number of observations for the
same spacecraft, the error contribution from observa-
tional noise is very small and not a meaningful measure of
uncertainty. It is therefore necessary to consider several
other eﬀects in order to assign realistic errors. Our ﬁrst
consideration is the statistical and numerical stability o f
of the calculations. We then go on to the cumulative
inﬂuence of all modeling errors and editing decisions. Fi-
nally we discuss the reasons for and signiﬁcance of the
annual term.
Besides the factors mentioned above, we will discuss in
this section errors that may be attributed to the speciﬁc
hardware used to run the orbit determination computer
codes, together with computational algorithms and sta-
tistical methods used to derive the solution.
A. Numerical stability of least-squares estimation
Having presented estimated solutions along with their
formal statistics, we should now attempt to characterize
the true accuracy of these results. Of course, the signiﬁ-
cance of the results must be assessed on the basis of the
expected measurement errors. These expected errors are
used to weight a least-squares adjustment to parameters
which describe the theoretical model. [Examination of
experimental systematics from sources both external to
and also internal to the spacecraft was covered in Sections
VII-VIII.]
First we look at the numerical stability of the least
squares estimation algorithm and the derived solution.
The leading computational error source turns out to be
subtraction of similar numbers. Due to the nature of
ﬂoating point arithmetic, two numbers with high order
digits the same are subtracted one from the other re-
sults in the low order digits being lost. This situation
occurs with time tags on the data. Time tags are refer-
enced to some epoch, such as say 1 January 1 1950 which
is used by CHASMP. As more than one billion seconds
have passed since 1950, time tags on the Doppler data
have a start and end time that have ﬁve or six common
leading digits. Doppler signal is computed by a diﬀer-
enced range formulation (see Section III B). This noise
in the time tags causes noise in the computed Doppler
at the 0.0006 Hz level for both Pioneers. This noise can
be reduced by shifting the reference epoch closer to the
data or increasing the word length of the computation,
however, it is not a signiﬁcant error source for this anal-
ysis.
In order to guard against possible computer com-
piler and/or hardware errors we ran orbit determina-
tion programs on diﬀerent computer platforms. JPL’s
ODP resides on an HP workstation. The Aerospace
Corporation ran the analysis on three diﬀerent com-
puter architectures: (i) Aerospace’s DEC 64-bit RISC
architecture workstation (Alphastation 500/266), (ii)
Aerospace’s DEC 32-bit CISC architecture workstation
(V AX 4000/60), and (iii) Pentium Pro PC. Comparisons
of computations performed for CHASMP in the three
machine show consistency to 15 digits which is just suﬃ-
cient to represent the data. While this comparison does
not eliminate the possibility of systematic errors that are
common to both systems, it does test the numerical sta-
bility of the analysis on three very diﬀerent computer
architectures.
The results of the individual programs were given
in Sections Vand VI. In a test we took the JPL re-
sults for a batch-sequential Sigma run with 50-day av-
erages of the anomalous acceleration of Pioneer 10, aP .
The data interval was from January 1987 to July 1998.
We compared this to an Aerospace determination using
CHASMP, where the was split into 200 day intervals,
over a shorter data interval ending in 1994. As seen in
Figure 14, the results basically agree.
Given the excellent agreement in these implementa-
tions of the modeling software, we conclude that diﬀer-
ences in analyst choices (parameterization of clocks, data
editing, modeling options, etc.) give rise to coordinate
discrepancies only at the level of 0 . 3 cm. This number
corresponds to an uncertainty in estimating the anoma-
lous acceleration on the order of 8 × 10− 12 cm/s2.
But there is a slightly larger error to contend with. In
principle the STRIPPER can give output to 16 signiﬁcant
ﬁgures. From the beginning the output was-rounded oﬀ
to 15 and later to 14 signiﬁcant ﬁgures. When Block
5 came on near the beginning of 1995, the output was
rounded oﬀ to 13 signiﬁcant ﬁgures. Since the Doppler
residuals are 1.12 mm/s this last truncation means an
error of order 0.01 mm/s. If we divide this number by 2
for an average round oﬀ, this translates to ±0. 04 × 10− 8
cm/s2. The roundoﬀ occurred in approximately all the
data we added for this paper. This is the cleanest 1/3
of the Pioneer 10 data. Considering this we take the
uncertainty to be
σ num ± 0. 02 × 10− 8 cm/ s2. (47)
It needs to be stressed that such tests examine only
the accuracy of implementing a given set of model codes,
without consideration of the inherent accuracy of the
models themselves. Numerous external tests, which we
have been discussing in the previous three sections, are
possible for assessing the accuracy of the solutions. Com-
parisons between the two software packages enabled us
to evaluate the implementations of the theoretical mod-
els within a particular software. Likewise, the results of
independent radio tracking observations obtained for the
diﬀerent spacecraft and analysis programs have enabled
us to compare our results to infer realistic error levels
from diﬀerences in data sets and analysis methods. Our
analysis of the Galileo and Ulysses missions (reported in
Sections V C and V D) was done partially for this pur-
pose.
