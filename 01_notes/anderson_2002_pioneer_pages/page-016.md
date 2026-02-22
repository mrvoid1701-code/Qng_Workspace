# Page 16

16
a weight function that accounts for noise introduced by
solar plasma and low elevation. The weight values are ad-
justed so that i) the post-ﬁt weighted sum of the squares
is close to unity and ii) approximately uniform noise in
the residuals is observed throughout the ﬁt span.
Thus, the corresponding solar-corona weight function
is:
σ r = k
2
(ν 0
ν
)2(R⊙
ρ
)3
2
, (12)
where, for range data, k is an input constant nominally
equal to 0.005 light seconds, ν 0 and ν are a reference
frequency and the actual frequency, ρ is the trajectory’s
impact parameter with respect to the Sun in km, and R⊙
is the solar radius in km [66]. The solar-corona weight
function for Doppler is essentially the same, but obtained
by numerical time diﬀerentiation of Eq. (12).
E. Modeling of maneuvers
There were 28 Pioneer 10 maneuvers during our data
interval from 3 January 1987 to 22 July 1998. Imperfect
coupling of the hydrazine thrusters used for the spin ori-
entation maneuvers produced integrated velocity changes
of a few millimeters per second. The times and durations
of each maneuver were provided by NASA/Ames. JPL
used this data as input to ODP. The Aerospace team
used a slightly diﬀerent approach. In addition to the orig-
inal data, CHASMP used the spin-rate data ﬁle to help
determine the times and duration of maneuvers. The
CHASMP determination mainly agreed with the data
used by JPL. [There were minor variations in some of
the times, one maneuver was split in two, and one extra-
neous maneuver was added to Interval II to account for
data not analyzed (see below).]
Because the eﬀect on the spacecraft acceleration could
not be determined well enough from the engineering
telemetry, JPL included a single unknown parameter in
the ﬁtting model for each maneuver. In JPL’s ODP anal-
ysis, the maneuvers were modeled by instantaneous ve-
locity increments at the beginning time of each maneu-
ver (instantaneous burn model). [Analyses of individual
maneuver ﬁts show the residuals to be small.] In the
CHASMP analysis, a constant acceleration acting over
the duration of the maneuver was included as a param-
eter in the ﬁtting model (ﬁnite burn model). Analyses
of individual maneuver ﬁts show the residuals are small.
Because of the Pioneer spin, these accelerations are im-
portant only along the Earth-spacecraft line, with the
other two components averaging out over about 50 revo-
lutions of the spacecraft over a typical maneuver duration
of 10 minutes.
By the time Pioneer 11 reached Saturn, the pattern
of the thruster ﬁrings was understood. Each maneuver
caused a change in spacecraft spin and a velocity incre-
ment in the spacecraft trajectory, immediately followed
by two to three days of gas leakage, large enough to be
observable in the Doppler data [67].
Typically the Doppler data is time averaged over 10
to 33 minutes, which signiﬁcantly reduces the high-
frequency Doppler noise. The residuals represent our ﬁt.
They are converted from units of Hz to Doppler velocity
by the formula [38]
[∆v]DSN = c
2
[∆ν ]DSN
ν 0
, (13)
where ν 0 is the downlink carrier frequency, ∼ 2. 29 GHz,
∆ν is the Doppler residual in Hz from the ﬁt, and c is
the speed of light.
As an illustration, consider the ﬁt to one of the Pio-
neer 10 maneuvers, # 17, on 22 December 1993, given in
Figure 5. This was particularly well covered by low-noise
FIG. 5: The Doppler residuals after a ﬁt for maneuver # 17
on 23 December 1993.
Doppler data near solar opposition. Before the start of
the maneuver, there is a systematic trend in the residu-
als which is represented by a cubic polynomial in time.
The standard error in the residuals is 0.095 mm/s. After
the maneuver, there is a relatively small velocity discon-
tinuity of −0. 90 ± 0. 07 mm/s. The discontinuity arises
because the model ﬁts the entire data interval. In fact,
the residuals increase after the maneuver. By 11 January
1994, 19 days after the maneuver, the residuals are scat-
tered about their pre-maneuver mean of −0. 15 mm/s.
For purposes of characterizing the gas leak immedi-
ately after the maneuver, we ﬁt the post-maneuver resid-
uals by a two-parameter exponential curve,
∆v = −v0 exp
[
− t
τ
]
− 0. 15 mm / s. (14)
The best ﬁt yields v0 = 0 . 808 mm/s and the time con-
stant τ is 13.3 days, a reasonable result. The time deriva-
tive of the exponential curve yields a residual acceleratio n
immediately after the maneuver of 7.03 × 10− 8 cm/s2.
This is close to the magnitude of the anomalous acceler-
ation inferred from the Doppler data, but in the opposite
