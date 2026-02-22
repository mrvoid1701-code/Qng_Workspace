# Page 39

39
B. Accuracy of consistency/model tests
a. Consistency of solutions: A code that models
the motion of solar system bodies and spacecraft in-
cludes numerous lengthy calculations. Therefore, the
software used to obtain solutions from the Doppler data
is, of necessity, very complex. To guard against poten-
tial errors in the implementation of these models, we
used two software packages; JPL’s ODP/ Sigma model-
ing software [41, 54] and The Aerospace Corporation’s
POEAS/CHASMP software package [77, 78]. The diﬀer-
ences between the JPL and Aerospace orbit determina-
tion program results are now examined.
As discussed in Section IV F, in estimating parame-
ters the CHASMP code uses a standard variation of pa-
rameters method whereas ODP uses the Cowell method
to integrate the equations of motion and the variational
equations. In other words, CHASMP integrates six ﬁrst-
order diﬀerential equation, using the Adams-Moulton
predictor-corrector method in the orbital elements. Con-
trariwise, ODP integrates three second-order diﬀerential
equations for the accelerations using the Gauss-Jackson
method. (For more details on these methods see Ref.
[121].)
As seen in our results of Sections Vand VI, agreement
was good; especially considering that each program uses
independent methods, models, and constants. Internal
consistency tests indicate that a solution is consistent at
the level of one part in 10 15. This implies an acceleration
error on the order of no more then one part in 10 4 in aP .
b. Earth orientation parameters: In order to check
for possible problems with Earth orientation, CHASMP
was modiﬁed to accept Earth orientation information
from three diﬀerent sources. (1) JPL’s STOIC pro-
gram that outputs UT1R-UTC, (2) JPL’s Earth Orienta-
tion Parameter ﬁles (UT1-UTC), and (3) The International
Earth Rotation Service’s Earth Orientation Parameter
ﬁle ( UT1-UTC). We found that all three sources gave vir-
tually identical results and changed the value of aP only
in the 4th digit [122].
c. Planetary ephemeris: Another possible source of
problems is the planetary ephemeris. To explore this a
ﬁt was ﬁrst done with CHASMP that used DE200. The
solution of that ﬁt was then used in a ﬁt where DE405
was substituted for DE200. The result produced a small
annual signature before the ﬁt. After the ﬁt, the maneu-
ver solutions changed a small amount (less then 10%)
but the value of the anomalous acceleration remained
the same to seven digits. The post-ﬁt residuals to DE405
were virtually unchanged from those using DE200. This
showed that the anomalous acceleration was unaﬀected
by changes in the planetary ephemeris.
This is pertinent to note for the following subsection.
To reemphasize the above, a small “annual term” can be
introduced by changing the planetary ephemerides. This
annual term can then be totally taken up by changing
the maneuver estimations. Therefore, in principle, any
possible mismodeling in the planetary ephemeris could be
at least partially masked by the maneuver estimations.
d. Diﬀerences in the codes’ model implementations:
The impact of an analyst’s choices is diﬃcult to address,
largely because of the time and expense required to pro-
cess a large data set using complex models. This is espe-
cially important when it comes to data editing. It should
be understood that small diﬀerences are to be expected
as models diﬀer in levels of detail and accuracy. The an-
alysts’ methods, experience, and judgment diﬀer. The
independence of the analysis of JPL and Aerospace has
been consistently and strictly maintained in order to pro-
vide conﬁdence on the validity of the analyses. Acknowl-
edging such diﬃculties, we still feel that using the very
limited tests given above is preferable to an implicit as-
sumption that all analysts’ choices were optimally made.
Another source for diﬀerences in the results presented
in Table I is the two codes’ modeling of spacecraft re-
orientation maneuvers. ODP uses a model that solves
for the resulted change in the Doppler observable ∆ v
(instantaneous burn model). This is a more convenient
model for Doppler velocity measurements. CHASMP
models the change in acceleration, solves for ∆ a (ﬁnite
burn model), and only then produces a solution for ∆ v.
Historically, this was done in order to incorporate range
observations (for Galileo and Ulysses) into the analysis.
Our best handle on this is the no-corona results, espe-
cially given that the two critical Pioneer 10 Interval III
results diﬀered by very little, 0 . 02 × 10− 8 cm/s2. This
data is least aﬀected by maneuver modeling, data edit-
ing, corona modeling, and spin calibration. Contrari-
wise, for the other data, the diﬀerences were larger. The
Pioneer Interval I and II results and the Pioneer 11 re-
sults diﬀered, respectively, by (0.21, 0.23, 0.25) in units
of 10 − 8 cm/s2. In these intervals models of maneuvers
and data editing were crucial. Assuming that these er-
rors are uncorrelated, we compute their combined eﬀect
on anomalous acceleration aP as
σ consist/model = ±0. 13 × 10− 8 cm/s2. (48)
e. Mismodeling of maneuvers: A small contribution
to the error comes from a possible mismodeling of the
propulsion maneuvers. In Section IV E we found that for
a typical maneuver the standard error in the residuals is
σ 0 ∼ 0. 095 mm/s.
Then we would expect that in the period between two
maneuvers, which on average is τ = 11.5/28 year, the ef-
fect of the mismodeling would produce a contribution to
the acceleration solution with a magnitude on the order
of δa man = σ 0/τ = 0. 07 × 10− 8 cm/s2. Now let us assume
that the errors in the Pioneer Doppler residuals are nor-
mally distributed around zero mean with the standard
deviation of δa man that constitute a single measurement
accuracy. Then, since there are N = 28 maneuvers in the
data set, the total error due to maneuver mismodeling is
σ man = δa man
√
N
= 0. 01 × 10− 8 cm/ s2. (49)
