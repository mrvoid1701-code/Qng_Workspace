# Page 28

28
and have been reﬁned since then. The models take into
account various parts of the spacecraft exposed to solar
radiation, primarily the high-gain antenna. It computes
an acceleration directed away from the Sun as a function
of spacecraft orientation and solar distance.
The models for the acceleration due to solar radiation
can be formulated as
as.p.(r) = Kf⊙ A
c M
cos θ (r)
r2 . (25)
f⊙ = 1367 W / m2(AU)2 is the (eﬀective-temperature
Stefan-Boltzmann) “solar radiation constant” at 1 AU
from the Sun and A is the eﬀective size of the craft as
seen by the Sun [89]. (For Pioneer the area was taken
to be the antenna dish of radius 1.73 m.) θ is the an-
gle between the axis of the antenna and the direction of
the Sun, c is the speed of light, M is the mass of the
spacecraft (taken to be 251.883 for Pioneer 10), and r
is the distance from the Sun to the spacecraft in AU. K
[90] is the eﬀective [91] absorption/reﬂection coeﬃcient.
For Pioneer 10 the simplest approximately correct model
yields K0 = 1 . 71 [91]. Eq. (25) provides a good model
for analysis of the eﬀect of solar radiation pressure on
the motion of distant spacecraft and is accounted for by
most of the programs used for orbit determination.
However, in reality the absorptivities, emissivities, and
eﬀective areas of spacecraft parts parameters which, al-
though modeled by design, are determined by calibration
early in the mission [92]. One determines the magnitude
of the solar-pressure acceleration at various orientation s
using Doppler data. (The solar pressure eﬀect can be
distinguished from gravity’s 1 /r 2 law because cos θ varies
[45].) The complicated set of program input parameters
that yield the parameters in Eq. (25) are then set for
later use [92]. Such a determination of the parameters
for Pioneer 10 was done, soon after launch and later.
When applied to the solar radiation acceleration in the
region of Jupiter, this yields (from a 5 % uncertainty in
as.p. [87])
as.p.(r = 5. 2AU) = (70 . 0 ± 3. 5) × 10− 8 cm/ s2,
K5.2 = 1 . 77. (26)
The second of Eqs. (26) comes from putting the ﬁrst into
Eq. (25). Note, speciﬁcally, that in a ﬁt a too high input
mass will be compensated for by a higher eﬀective K.
Because of the 1 /r 2 law, by the time the craft reached
10 AU the solar radiation acceleration was 18 . 9 × 10− 8
cm/s2 going down to 0.39 of those units by 70 AU. Since
this systematic falls oﬀ as r− 2, it can bias the Doppler de-
termination of a constant acceleration at some level, even
though most of the systematic is correctly modeled by
the program itself. By taking the average of the r− 2 ac-
celeration curves over the Pioneer distance intervals, we
estimate that the systematic error from solar-radiation
pressure in units of 10 − 8 cm/ s2 is 0.001 for Pioneer 10
over an interval from 40 to 70 AU, and 0.006 for Pioneer
11 over an interval from 22 to 32 AU.
However, this small uncertainty is not our main prob-
lem. In actuality, since the parameters were ﬁt the mass
has decreased with the consumption of propellant. Eﬀec-
tively, the 1/r 2 systematic has changed its normalization
with time. If not corrected for, the diﬀerence between
the original 1 /r 2 and the corrected 1 /r 2 will be inter-
preted as a bias in aP . Unfortunately, exact information
on gas usage is unavailable [16]. Therefore, in dealing
with the eﬀect of the temporal mass variation during the
entire data span (i.e. nominal input mass vs. actual mass
history [15, 16]) we have to address two eﬀects on the so-
lutions for the anomalous acceleration aP . They are i)
the eﬀect of mass variation from gas consumption and ii)
the eﬀect of an incorrect input mass [15, 16].
To resolve the issue of mass variation uncertainty we
performed a sensitivity analysis of our solutions to dif-
ferent spacecraft input masses. We simply re-did the no-
corona, WLS runs of Table I with a range of diﬀerent
masses. The initial wet weight of the package was 259 kg
with about 36 kg of consumable propellant. For Pioneer
10, the input mass in the program ﬁt was 251.883 kg,
roughly corresponding to the mass after spin-down. By
our data period, roughly half the fuel (18 kg) was gone
so we take 241 kg as our nominal Pioneer 10 mass. Thus,
the eﬀect of going from 251.883 kg to 241 kg we take to
be our bias correction for Pioneer 10. We take the un-
certainty to be given by one half the eﬀect of going from
plus to minus 9 kg (plus or minus a quarter tank) from
the nominal mass of 241 kg.
For the three intervals of Pioneer 10 data, using
ODP/Sigma yields the following changes in the accel-
erations:
δa mass
P = [(0 . 040 ± 0. 035), (0. 029 ± 0. 025),
(0. 020 ± 0. 017)] × 10− 8 cm/ s2.
As expected,these results make aP larger. For our sys-
tematic bias we take the weighted average of δa mass
P for
the three intervals of Pioneer 10. The end result is
as.p. = (0. 03 ± 0. 01) × 10− 8 cm/ s2. (27)
For Pioneer 11 we did the same except our bias point
was 3/4 of the fuel gone (232 kg). Therefore the bias
results by going from the input mass of 239.73 to 232 kg.
The uncertainty is again deﬁned by ± 9 kg. The result
for Pioneer 11 is more sensitive to mass changes, and we
ﬁnd using ODP/ Sigma
as.p. = (0. 09 ± 0. 21) × 10− 8 cm/ s2. (28)
The bias number is three times larger than the similar
number for Pioneer 10, and the uncertainty much larger.
We return to this diﬀerence in Section VIII G.
The previous analysis also allowed us to perform
consistency checks on the eﬀective values of K which
the programs were using. By taking [ rminrmax]− 1 =
[
∫
(dr/r 2)/
∫
dr] for the inverse distance squared of a data
set, varying the masses, and determining the shifts in aP
