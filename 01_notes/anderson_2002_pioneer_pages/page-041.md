# Page 41

41
ware implementation from September 1994 to August
1995. As a result of this implementation the data is less
noisy than before. Over Interval III the annual term is
roughly in the form of a sine wave. (In fact, the mod-
eling error is not strictly a sine wave. But it is close
enough to a sine wave for purposes of our error analy-
sis.) The peaks of the sinusoid are centered on conjunc-
tion, where the Doppler noise is at a maximum. Look-
ing at a CHASMP set of residuals for Interval III, we
found a 4-parameter, nonlinear, weighted, least-squares
ﬁt to an annual sine wave with the parameters amplitude
va.t. = (0 . 1053 ± 0. 0107) mm/s, phase ( −5. 3◦ ± 7. 2◦),
angular velocity ω a.t = (0 . 0177 ± 0. 0001) rad/day, and
bias (0 . 0720 ± 0. 0082) mm/s. The weights eliminate
data taken inside of solar quadrature, and also account
for diﬀerent Doppler integration times Tc according to
σ = (0. 765 mm / s) [(60 s)/T c]1/2. This rule yields post-ﬁt
weighted RMS residuals of 0.1 mm/s.
The amplitude, va.t., and angular velocity, ω a.t., of the
annual term results in a small acceleration amplitude of
aa.t. = va.t.ω a.t. = (0. 215 ± 0. 022) × 10− 8 cm/s2. We will
argue below that the cause is most likely due to errors in
the navigation programs’ determinations of the direction
of the spacecraft’s orbital inclination to the ecliptic.
A similar troubling modeling error exists on a much
shorter time scale that is most likely an error in the space-
craft’s orbital inclination to the Earth’s equator. We
looked at CHASMP acceleration residuals over a limited
data interval, from 23 November 1996 to 23 December
1996, centered on opposition where the data is least af-
fected by solar plasma. As seen in Figure 18, there is a
signiﬁcant diurnal term in the Doppler residuals, with pe-
riod approximately equal to the Earth’s sidereal rotation
period (23 h56m04s.0989 mean solar time).
FIG. 18: CHASMP acceleration residuals from 23 November
1996 to 23 December 1996. A clear modeling error is repre-
sented by the solid diurnal curve. (An annual term maximum
is also seen as a background.)
After the removal of this diurnal term, the RMS
Doppler residuals are reduced to amplitude 0.054 mm/s
for Tc = 660 s ( σ ν /ν = 2. 9 × 10− 13 at Tc = 1000 s). The
amplitude of the diurnal oscillation in the fundamental
Doppler observable, vd.t., is comparable to that in the
annual oscillation, va.t., but the angular velocity, ω d.t.,
is much larger than ω a.t.. This means the magnitude
of the apparent angular acceleration, ad.t. = vd.t.ω d.t. =
(100. 1 ± 7. 9) × 10− 8 cm/s2, is large compared to aP . Be-
cause of the short integration times, Tc = 660 s, and long
observing intervals, T ∼ 1 yr, the high frequency, diur-
nal, oscillation signal averages out to less than 0 . 03×10− 8
cm/s2 over a year. This intuitively helps to explain why
the apparently noisy acceleration residuals still yield a
precise value of aP .
Further, all the residuals from CHASMP and
ODP/Sigma are essentially the same. Since ODP and
CHASMP both use the same Earth ephemeris and the
same Earth orientation models, this is not surprising.
This is another check that neither program introduces
serious modeling errors of its own making.
Due to the long distances from the Sun, the spin-
stabilized attitude control, the long continuous Doppler
data history, and the fact that the spacecraft communica-
tion systems utilize coherent radio-tracking, the Pioneer s
allow for a very sensitive and precise positioning on the
sky. For some cases, the Pioneer 10 coherent Doppler
data provides accuracy which is even better than that
achieved with VLBI observing natural sources. In sum-
mary, the Pioneers are simply much more sensitive de-
tectors of a number of solar system modeling errors than
other spacecraft.
The annual and diurnal terms are very likely diﬀerent
manifestations of the same modeling problem. The mag-
nitude of the Pioneer 10 post-ﬁt weighted RMS residuals
of ≈ 0. 1 mm/s, implies that the spacecraft angular posi-
tion on the sky is known to ≤ 1. 0 milliarcseconds (mas).
(Pioneer 11, with ≈ 0. 18 mm/s, yields the result ≈ 1. 75
mas.) At their great distances, the trajectories of the
Pioneers are not gravitationally aﬀected by the Earth.
(The round-trip light time is now ∼ 24 hours for Pioneer
10.) This suggests that the sources of the annual and
diurnal terms are both Earth related.
Such a modeling problem arises when there are er-
rors in any of the parameters of the spacecraft orien-
tation with respect to the chosen reference frame. Be-
cause of these errors, the system of equations that de-
scribes the spacecraft’s motion in this reference frame
is under-determined and its solution requires non-linear
estimation techniques. In addition, the whole estima-
tion process is subject to Kalman ﬁltering and smooth-
ing methods. Therefore, if there are modeling errors in
the Earth’s ephemeris, the orientation of the Earth’s spin
axis (precession and nutation), or in the station coordi-
nates (polar motion and length of day variations), the
least-squares process (which determines best-ﬁt values of
the three direction cosines) will leave small diurnal and
annual components in the Doppler residuals, like those
seen in Figures 17-18.
