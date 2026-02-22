# Page 42

42
Orbit determination programs are particularly sensi-
tive to an error in a poorly observed direction [124]. If
not corrected for, such an error could in principle signif-
icantly aﬀect the overall navigational accuracy. In the
case of the Pioneer spacecraft, navigation was performed
using only Doppler tracking, or line-of-sight observation s.
The other directions, perpendicular to the line-of-sight o r
in the plane of the sky, are poorly constrained by the data
available. At present, it is infeasible to precisely parame -
terize the systematic errors with a physical model. That
would have allowed one to reduce the errors to a level
below those from the best available ephemeris and Earth
orientation models. A local empirical parameterization is
possible, but not a parameterization over many months.
We conclude that for both Pioneer 10 and 11, there are
small periodic errors in solar system modeling that are
largely masked by maneuvers and by the overall plasma
noise. But because these sinusoids are essentially uncor-
related with the constant aP , they do not present im-
portant sources of systematic error. The characteristic
signature of aP is a linear drift in the Doppler, not an-
nual/diurnal signatures [125].
i. Annual/diurnal mismodeling uncertainty: We
now estimate the annual term contribution to the error
budget for aP . First observe that the standard errors for
radial velocity, vr, and acceleration, ar, are essentially
what one would expect for a linear regression. The
caveat is that they are scaled by the root sum of squares
(RSS) of the Doppler error and unmodeled sinusoidal
errors, rather than just the Doppler error. Further,
because the error is systematic, it is unrealistic to
assume that the errors for vr and ar can be reduced by
a factor 1/
√
N , where N is the number of data points.
Instead, averaging their correlation matrix over the data
interval, T , results in the estimated systematic error of
σ 2
ar = 12
T 2 σ 2
vr = 12
T 2
(
σ 2
T + σ 2
va.t. + σ 2
vd.t.
)
. (51)
σ T = 0. 1 mm/s is the Doppler error averaged over T (not
the standard error on a single Doppler measurement).
σ va.t. and σ vd.t. are equal to the amplitudes of correspond-
ing unmodeled annual and diurnal sine waves divided by
√
2. The resulting RSS error in radial velocity determi-
nation is about σ vr = (σ 2
T +σ 2
va.t. +σ 2
vd.t. )1/2 = 0. 15 mm/s
for both Pioneer 10 and 11. Our four interval values of
aP were determined over time intervals of longer than a
year. At the same time, to detect an annual signature in
the residuals, one needs at least half of the Earth’s orbit
complete. Therefore, with T = 1 / 2 yr, Eq. (51) results
in an acceleration error of
σ a/d = 0. 50 mm / s
T = 0. 32 × 10− 8 cm/ s2. (52)
We use this number for the systematic error from the
annual/diurnal term.
X. ERROR BUDGET AND FINAL RESUL T
It is important to realize that our experimental observ-
able is a Doppler frequency shift, i.e., ∆ ν (t). [See Figure
8 and Eq. (15).] In actual fact it is a cycle count. We
interpret this as an apparent acceleration experienced by
the spacecraft. However, it is possible that the Pioneer
eﬀect is not due to a real acceleration. (See Section XI.)
Therefore, the question arises “In what units should we
report our errors?” The best choice is not clear at this
point. For reasons of clarity we chose units of accelera-
tion.
The tests documented in the preceding sections have
considered various potential sources of systematic error.
The results of these tests are summarized in Table II,
which serves as a systematic “error budget.” This bud-
get is useful both for evaluating the accuracy of our so-
lution for aP and also for guiding possible future eﬀorts
with other spacecraft. In our case it actually is hard to
totally distinguish “experimental” error from “system-
atic error.” (What should a drift in the atomic clocks
be called?) Further, there is the intractable mathemati-
cal problem of how to handle combined experimental and
systematic errors. In the end we have decided to treat
them all in a least squares uncorrelated manner.
The results of our analyses are summarized in Table II.
There are two columns of results. The ﬁrst gives a bias,
bP , and the second gives an uncertainty, ±σ P . The con-
stituents of the error budget are listed separately in three
diﬀerent categories: 1) systematics generated external to
the spacecraft; 2) on-board generated systematics, and
3) computational systematics. Our ﬁnal result then will
become some average
aP = aP (exper) + bP ± σ P , (53)
where, from Eq. (23), aP (exper) = (7 . 84 ± 0. 01) × 10− 8
cm/s2.
The least signiﬁcant factors of our error budget are in
the ﬁrst group of eﬀects, those external to the spacecraft.
From the table one sees that some are near the limit of
contributing. But in totality, they are insigniﬁcant.
As was expected, the on-board generated systematics
are the largest contributors to our total error budget.
All the important constituents are listed in the second
group of eﬀects in Table II. Among these eﬀects, the ra-
dio beam reaction force produces the largest bias to our
result, 1 . 10 × 10− 8 cm/s2. It makes the Pioneer eﬀect
larger. The largest bias/uncertainty is from RTG heat
reﬂecting oﬀ the spacecraft. We argued for an eﬀect as
large as ( −0. 55 ± 0. 55) × 10− 8 cm/s2. Large uncertainties
also come from diﬀerential emissivity of the RTGs, ra-
diative cooling, and gas leaks, ±0. 85, ±0. 48, and ±0. 56,
respectively, ×10− 8 cm/s2. The computational system-
atics are listed in the third group of Table II.
Therefore, our ﬁnal value for aP is
aP = (8 . 74 ± 1. 33) × 10− 8 cm/ s2
∼ (8. 7 ± 1. 3) × 10− 8 cm/ s2. (54)
