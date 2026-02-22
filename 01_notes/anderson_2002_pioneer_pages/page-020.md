# Page 20

20
data was performed using an independent program, The
Aerospace Corporation’s Compact High Accuracy Satel-
lite Motion Program (CHASMP) [77] – one of the stan-
dard Aerospace orbit analysis programs. CHASMP’s or-
bit determination module is a development of a program
called POEAS (Planetary Orbiter Error Analysis Study
program) that was developed at JPL in the early 1970’s
independently of JPL’s ODP. As far as we know, not a
single line of code is common to the two programs [78].
Although, by necessity, both ODP and CHASMP use
the same physical principles, planetary ephemeris, and
timing and polar motion inputs, the algorithms are oth-
erwise quite diﬀerent. If there were an error in either
program, they would not agree.
Aerospace analyzed a Pioneer 10 data arc that was
initialized on 1 January 1987 at 16 hr (the data itself
started on 3 January) and ended at 14 December 1994, 0
hr. The raw data set was averaged to 7560 data points of
which 6534 points were used. This CHASMP analysis of
Pioneer 10 data also showed an unmodeled acceleration
in a direction along the radial toward the Sun [79]. The
value is (8 . 65 ± 0. 03) × 10− 8 cm/s2, agreeing with JPL’s
result. The smaller error here is because the CHASMP
analysis used a batch least-squares ﬁt over the whole orbit
[76, 77], not looking for a variation of the magnitude of
aP with distance.
Without using the apparent acceleration, CHASMP
shows a steady frequency drift [38] of about −6 × 10− 9
Hz/s, or 1.5 Hz over 8 years (one-way only). (See Fig-
ure 8.) This equates to a clock acceleration, −at, of
−2. 8 × 10− 18 s/s2. The identity with the apparent Pio-
neer acceleration is
at ≡ aP /c. (16)
The drift in the Doppler residuals (observed minus com-
puted data) is seen in Figure 9.
The drift is clear, deﬁnite, and cannot be removed
without either the added acceleration, aP , or the inclu-
sion in the data itself of a frequency drift, i.e., a “clock
acceleration” at. If there were a systematic drift in the
atomic clocks of the DSN or in the time-reference stan-
dard signals, this would appear like a non-uniformity of
time; i.e., all clocks would be changing with a constant
acceleration. We now have been able to rule out this
possibility. (See Section XI D.)
Continuing our search for an explanation, we consid-
ered the possibilities: i) that the Pioneer 10/11 spacecraf t
had internal systematic properties, undiscovered because
they are of identical design, and ii) that the accelera-
tion was due to some not-understood viscous drag force
(proportional to the approximately constant velocity of
the Pioneers). Both these possibilities could be investi-
gated by studying spin-stabilized spacecraft whose spin
axes are not directed towards the Sun, and whose orbital
velocity vectors are far from being radially directed.
Two candidates were Galileo in its Earth-Jupiter mis-
sion phase and Ulysses in Jupiter-perihelion cruise out
of the plane of the ecliptic. As well as Doppler, these
FIG. 8: CHASMP two-way Doppler residuals (observed
Doppler velocity minus model Doppler velocity) for Pioneer
10 vs. time. 1 Hz is equal to 65 mm/s range change per
second. The model is fully-relativistic. The solar system’ s
gravitational ﬁeld is represented by the Sun and its planeta ry
systems [49].
FIG. 9: CHASMP best ﬁt for the Pioneer 10 Doppler residuals
with the anomalous acceleration taken out. After adding one
more parameter to the model (a constant radial acceleration )
the residuals are distributed about zero Doppler velocity w ith
a systematic variation ∼ 3.0 mm/s on a time scale of ∼ 3
months. The outliers on the plot were rejected from the ﬁt.
[The quality of the ﬁt may be determined by the ratio of
residuals to the downlink carrier frequency, ν 0 ≈ 2.29 GHz.]
spacecraft also yielded a considerable quantity of range
data. By having range data one can tell if a spacecraft
is accumulating a range eﬀect due to a spacecraft accel-
eration or if the orbit determination process is fooled by
a Doppler frequency rate bias.
