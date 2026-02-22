# Page 40

40
f. Mismodeling of the solar corona: Finally, recall
that our number for mismodeling of the solar corona,
±0. 02 × 10− 8 cm/s2, was already explained in Section
VII C.
C. Apparent annual/diurnal periodicities in the
solution
In Ref. [13] we reported, in addition to the constant
anomalous acceleration term, a possible annual sinusoid.
If approximated by a simple sine wave, the amplitude
of this oscillatory term is about 1 . 6 × 10− 8 cm/s2. The
integral of a sine wave in the acceleration, aP , with an-
gular velocity ω and amplitude A0 yields the following
ﬁrst-order Doppler amplitude in two-way fractional fre-
quency:
∆ν
ν = 2A0
c ω . (50)
The resulting Doppler amplitude for the annual angular
velocity ∼ 2 × 10− 7 rad/s is ∆ ν/ν = 5.3 × 10− 12. At
the Pioneer downlink S-band carrier frequency of ∼ 2. 29
GHz, the corresponding Doppler amplitude is 0.012 Hz
(i.e. 0.795 mm/s).
This term was ﬁrst seen in ODP using the BSF method.
As we discussed in Section IV G, treating aP as a stochas-
tic parameter in JPL’s batch–sequential analysis allows
one to search for a possible temporal variation in this
parameter. Moreover, when many short interval times
were used with least-squares CHASMP, the eﬀect was
also observed. (See Figure 14 in Section VI.)
The residuals obtained from both programs are of the
same magnitude. In particular, the Doppler residuals
are distributed about zero Doppler velocity with a sys-
tematic variation ∼ 3.0 mm/s on a time scale of ∼ 3
months. More precisely, the least-squares estimation
residuals from both ODP/ Sigma and CHASMP are dis-
tributed well within a half-width taken to be 0.012 Hz.
(See, for example, Figure 9.) Even the general structures
of the two sets of residuals are similar. The fact that
both programs independently were able to produce simi-
lar post-ﬁt residuals gives us conﬁdence in the solutions.
With this conﬁdence, we next looked in greater de-
tail at the acceleration residuals from solutions for aP .
Consider Figure 17, which shows the aP residuals from
a value for aP of (7 . 77 ± 0. 16) × 10− 8 cm/s2. The data
was processed using ODP/ Sigma with a batch-sequential
ﬁlter and smoothing algorithm. The solution for aP
was obtained using 1-day batch sizes. Also shown are
the maneuver times. At early times the annual term is
largest. During Interval II, the interval of the large spin-
rate change anomaly, coherent oscillation is lost. During
Interval III the oscillation is smaller and begins to die
out.
In attempts to understand the nature of this annual
term, we ﬁrst examined a number of possible sources, in-
cluding eﬀects introduced by imprecise modeling of ma-
neuvers, the solar corona, and the Earth’s troposphere.
FIG. 17: ODP 1-day batch-sequential acceleration residual s
using the entire Pioneer 10 data set. Maneuver times are
indicated by the vertical dashed lines.
We also looked at the inﬂuence of the data editing strate-
gies that were used. We concluded that these eﬀects
could not account for the annual term.
Then, given that the eﬀect is particularly large in the
out-of-the-ecliptic voyage of Pioneer 11 [13], we focused
on the possibility that inaccuracies in solar system mod-
eling are the cause of the annual term in the Pioneer so-
lutions. In particular, we looked at the modeling of the
Earth orbital orientation and the accuracy of the plane-
tary ephemeris.
g. Earth’s orientation: We speciﬁcally modeled the
Earth orbital elements ∆ p and ∆ q as stochastic parame-
ters. (∆ p and ∆ q are two of the Set III elements deﬁned
by Brouwer and Clemence [123].) Sigma was applied to
the entire Pioneer 10 data set with aP , ∆p, and ∆ q deter-
mined as stochastic parameters sampled at an interval of
ﬁve days and exponentially correlated with a correlation
time of 200 days. Each interval was ﬁt independently,
but with information on the spacecraft state (position
and velocity) carried forward from one interval to the
next. Various correlation times, 0-day, 30-day, 200-day,
and 400-day, were investigated. The a priori error and
process noise on ∆ p and ∆ q were set equal to 0, 5, and
10 µ rad in separate runs, but only the 10 µ rad case re-
moved the annual term. This value is at least three orders
of magnitude too large a deviation when compared to
the present accuracy of the Earth orbital elements. It is
most unlikely that such a deviation is causing the annual
term. Furthermore, changing to the latest set of EOP
has very little eﬀect on the residuals. [We also looked
at variations of the other four Set III orbital elements,
essentially deﬁning the Earth’s orbital shape, size, and
longitudinal phase angle. They had little or no eﬀect on
the annual term.]
h. Solar system modeling: We concentrated on In-
terval III, where the spin anomaly is at a minimum and
where aP is presumably best determined. Further, this
data was partially taken after the DSN’s Block 5 hard-
