# Page 15

15
the expected error in the acceleration error estimations.
This is on the order of
σ 0 ∼ 2 × 10− 8 cm/ s2, (7)
where σ 0 is a single determination accuracy related to ac-
celeration measurements averaged over number of days.
This would contribute to our result as σ N ∼ σ 0/
√
N .
Thus, if no systematics are involved then σ N will just
tend to zero as time progresses.
Therefore, the important thing is to know that these ef-
fects (systematics) are not too large, thereby overwhelm-
ing any possibly important signal (such as our anomalous
acceleration). This will be demonstrated in Sections VII
and VIII.
D. Solar corona model and weighting
The electron density and density gradient in the so-
lar atmosphere inﬂuence the propagation of radio waves
through the medium. So, both range and Doppler obser-
vations at S-band are aﬀected by the electron density in
the interplanetary medium and outer solar corona. Since,
throughout the experiment, the closest approach to the
center of the Sun of a radio ray path was greater than 3.5
R⊙ , the medium may be regarded as collisionless. The
one way time delay associated with a plane wave passing
through the solar corona is obtained [44, 46, 59] by inte-
grating the group velocity of propagation along the ray’s
path, ℓ:
∆t = ± 1
2c ncrit(ν )
∫ SC
⊕
dℓ n e(t, r),
ncrit(ν ) = 1 . 240 × 104
( ν
1 MHz
)2
cm− 3, (8)
where ne(t, r) is the free electron density in the solar
plasma, c is the speed of light, and ncrit(ν ) is the critical
plasma density for the radio carrier frequency ν . The
plus sign is applied for ranging data and the minus sign
for Doppler data [60].
Therefore, in order to calibrate the plasma contribu-
tion, one should know the electron density along the
path. One usually decomposes the electron density, ne,
into a static, steady-state part,
ne(r), plus a ﬂuctuation
δn e(t, r), i.e., ne(t, r) = ne(r) + δn e(t, r). The physical
properties of the second term are hard to quantify. But
luckily, its eﬀect on Doppler observables and, therefore,
on our results is small. (We will address this issue in Sec.
VII B.) On the contrary, the steady-state corona behav-
ior is reasonably well known and several plasma models
can be found in the literature [59]-[62].
Consequently, while studying the eﬀect of a system-
atic error from propagation of the S-band carrier wave
through the solar plasma, both analyses adopted the fol-
lowing model for the electron density proﬁle [44]:
ne(t, r) = A
(R⊙
r
)2
+ B
(R⊙
r
)2.7
e−
[
φ
φ0
] 2
+ C
(R⊙
r
)6
. (9)
r is the heliocentric distance to the immediate ray tra-
jectory and φ is the helio-latitude normalized by the ref-
erence latitude of φ 0 = 10 ◦. The parameters r and φ
are determined from the trajectory coordinates on the
tracking link being modeled. The parameters A, B, C
are parameters chosen to describe the solar electron den-
sity. (They are commonly given in two sets of units,
meters or cm − 3 [63].) They can be treated as stochas-
tic parameters, to be determined from the ﬁt. But in
both analyses we ultimately chose to use the values de-
termined from the recent solar corona studies done for
the Cassini mission. These newly obtained values are:
A = 6. 0 × 103, B = 2. 0 × 104, C = 0. 6 × 106, all in meters
[64]. [This is what we will refer to as the “Cassini corona
model.”]
Substitution of Eq. (9) into Eq. (8) results in the
following steady-state solar corona contribution to the
range model that we used in our analysis:
∆SCrange = ±
(ν 0
ν
)2[
A
(R⊙
ρ
)
F +
+ B
(R⊙
ρ
)1.7
e
−
[
φ
φ0
] 2
+ C
(R⊙
ρ
)5]
. (10)
ν 0 and ν are a reference frequency and the actual fre-
quency of radio-wave [for Pioneer 10 analysis ν 0 = 2295
MHz], ρ is the impact parameter with respect to the Sun
and F is a light-time correction factor. For distant space-
craft this function is given as follows:
F = F (ρ, r T , r E) = (11)
= 1
π
{
ArcTan
[ √
r2
T − ρ 2
ρ
]
+ ArcTan
[ √
r2
E − ρ 2
ρ
]}
,
where rT and rE are the heliocentric radial distances to
the target and to the Earth, respectively. Note that the
sign of the solar corona range correction is negative for
Doppler and positive for range. The Doppler correction
is obtained from Eq. (10) by simple time diﬀerentiation.
Both analyses use the same physical model, Eq. (10),
for the steady-state solar corona eﬀect on the radio-wave
propagation through the solar plasma. Although the ac-
tual implementation of the model in the two codes is dif-
ferent, this turns out not to be signiﬁcant. (See Section
IX B.)
CHASMP can also consider the eﬀect of temporal vari-
ation in the solar corona by using the recorded history
of solar activity. The change in solar activity is linked to
the variation of the total number of sun spots per year
as observed at a particular wavelength of the solar radia-
tion, λ =10.7 cm. The actual data corresponding to this
variation is given in Ref. [65]. CHASMP averages this
data over 81 days and normalizes the value of the ﬂux by
150. Then it is used as a time-varying scaling factor in
Eq. (10). The result is referred to as the “F10.7 model.”
Next we come to corona data weighting. JPL’s ODP
does not apply corona weighting. On the other hand,
Aerospace’s CHASMP can apply corona weighting if de-
sired. Aerospace uses a standard weight augmented by
