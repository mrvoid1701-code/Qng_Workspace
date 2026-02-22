# Page 29

29
we could determine the values of K implied, We found:
KODP
Pio− 10(I) ≈ 1. 72; KODP
Pio− 11 ≈ 1. 82; KCHASMP
Pio− 10(I) ≈ 1. 74;
and ˆKCHASMP
Pio− 11) ≈ 1. 84. [The hat over the last K indicates
it was multiplied by (237.73/251.883) because CHASMP
uses 259.883 kg instead of 239.73 kg for the input mass.]
All these values of K are in the region expected and are
clustered around the value K5.2 in Eq. (26).
Finally, if you take the average values of K for Pio-
neers 10 and 11 (1.73, 1.83), multiply these numbers by
the input masses (251.883, 239.73) kg, and divide them
by our nominal masses (241, 232) kg, you obtain (1.87,
1.89), indicating our choice of nominal masses was well
motivated.
B. The solar wind
The acceleration caused by the solar wind has the same
form as Eq. (25), with f⊙ replaced by mpv3n, where
n ≈ 5 cm − 3 is the proton density at 1 AU and v ≈ 400
km/s is the speed of the wind. Thus,
σ s.w.(r) = Ks.w.
mpv3 n A cos θ
cM r 2
≈ 1. 24 × 10− 13
(20 AU
r
)2
cm/ s2. (29)
Because the density can change by as much as 100%,
the exact acceleration is unpredictable. But there are
measurements [89] showing that it is about 10 − 5 times
smaller than the direct solar radiation pressure. Even if
we make the very conservative assumption that the solar
wind contributes only 100 times less force than the solar
radiation, its smaller contribution is completely negligi -
ble.
C. The eﬀects of the solar corona and models of it
As we saw in the previous Section VII B, the eﬀect of
the solar wind pressure is negligible for distant spacecraf t
motion in the solar system. However, the solar corona
eﬀect on propagation of radio waves between the Earth
and the spacecraft needs to be analyzed in more detail.
Initially, to study the sensitivity of aP to the solar
corona model, we were also solving for the solar corona
parameters A, B, and C of Eq. (9) in addition to aP .
However, we realized that the Pioneer Doppler data is
not precise enough to produce credible results for these
physical parameters. In particular, we found that solu-
tions could yield a value of aP which was changed by
of order 10 % even though it gave unphysical values of
the parameters (especially B, which previously had been
poorly deﬁned even by the Ulysses mission [62]). [By
“unphysical” we mean electron densities that were either
negative or positive with values that are vastly diﬀerent
from what would be expected.]
Therefore, as noted in Section IV D, we decided to use
the newly obtained values for A, B, and C from the
Cassini mission and use them as inputs for our analy-
ses: A = 6 . 0 × 103, B = 2 . 0 × 104, C = 0 . 6 × 106, all in
meters [64]. This is the “Cassini corona model.”
The eﬀect of the solar corona is expected to be small
for Doppler and large for range. Indeed it is small for
Sigma. For ODP/ Sigma, the time-averaged eﬀect of the
corona was small, of order
σ corona = ±0. 02 × 10− 8 cm/ s2, (30)
as might be expected. We take this number to be the
error due to the corona.
What about the results from CHASMP. Both analyses
use the same physical model for the eﬀect of the steady-
state solar corona on radio-wave propagation through the
solar plasma (that is given by Eq. (10)). However, there
is a slight diﬀerence in the actual implementation of the
model in the two codes.
ODP calculates the corona eﬀect only when the Sun-
spacecraft separation angle as seen from the Earth (or
Sun-Earth-spacecraft angle) is less then π/ 2. It sets the
corona contribution to zero in all other cases. Earlier
CHASMP used the same model and got a small corona
eﬀect. Presently CHASMP calculates an approximate
corona contribution for all the trajectory. Speciﬁc atten-
tion is given to the region when the spacecraft is at oppo-
sition from the Sun and the Sun-Earth-spacecraft angle
∼ π . There CHASMP’s implementation truncates the
code approximation to the scaling factor F in Eq. (10).
This is speciﬁcally done to remove the ﬁctitious diver-
gence in the region where “impact parameter” is small,
ρ → 0.
However, both this and also the more complicated
corona models (with data-weighting and/or “F10.7” time
variation) used by CHASMP produce small deviations
from the no-corona results. Our decision was to incorpo-
rate these small deviations between the two results due
to corona modeling into our overall error budget as a
separate item:
σ corona
model = ±0. 02 × 10− 8 cm/ s2. (31)
This number could be discussed in Section IX, on com-
putational systematics. Indeed, that is where it will be
listed in our error budget.
D. Electro-magnetic Lorentz forces
The possibility that the spacecraft could hold a charge,
and be deﬂected in its trajectory by Lorentz forces, was
a concern for the magnetic ﬁeld strengths at Jupiter and
Saturn. However, the magnetic ﬁeld strength in the outer
solar system is on the order of < 1 γ (γ = 10 − 5 Gauss).
This is about a factor of 10 5 times smaller than the mag-
netic ﬁeld strengths measured by the Pioneers at their
nearest approaches to Jupiter: 0.185 Gauss for Pioneer
10 and 1.135 Gauss for the closer in Pioneer 11 [93].
