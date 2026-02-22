# Page 14

14
provide transformations of ET – TAI to accuracies of 1 ns
[42].
For the purposes of our study the Station Time ( ST) is
especially signiﬁcant. This time is the atomic time TAI
at a DSN tracking station on Earth, ST=TAIstation. This
atomic time scale departs by a small amount from the
“reference time scale.” The reference time scale for a
DSN tracking station on Earth is the Coordinated Uni-
versal Time ( UTC). This last is standard time for 0 ◦ lon-
gitude. (For more details see [42, 55].)
All the vectors in Eq. (6) except the geocentric position
vector of the tracking station on Earth can be interpo-
lated from the planetary ephemeris or computed from
these quantities. Universal Time ( UT) is the measure of
time which is the basis for all civil time keeping. It is an
observed time scale. The speciﬁc version used in JPL’s
Orbit Determination Program (ODP) is UT1. This is used
to calculate mean sidereal time, which is the Greenwich
hour angle of the mean equinox of date measured in the
true equator of date. Observed UT1 contains 41 short-
term terms with periods between 5 and 35 days. They
are caused by long-period solid Earth tides. When the
sum of these terms, ∆ UT1, is subtracted from UT1 the
result is called UT1R, where R means regularized.
Time in any scale is represented as seconds past 1
January 2000, 12 h, in that time scale. This epoch is
J2000.0, which is the start of the Julian year 2000. The
Julian Date for this epoch is JD 245,1545.0. Our analyses
used the standard space-ﬁxed J2000 coordinate system,
which is provided by the International Celestial Reference
Frame (ICRF). This is a quasi-inertial reference frame de-
ﬁned from the radio positions of 212 extragalactic sources
distributed over the entire sky [56].
The variability of the earth-rotation vector relative to
the body of the planet or in inertial space is caused by
the gravitational torque exerted by the Moon, Sun and
planets, displacements of matter in diﬀerent parts of the
planet and other excitation mechanisms. The observed
oscillations can be interpreted in terms of mantle elas-
ticity, earth ﬂattening, structure and properties of the
core-mantle boundary, rheology of the core, underground
water, oceanic variability, and atmospheric variability o n
time scales of weather or climate.
Several space geodesy techniques contribute to the con-
tinuous monitoring of the Earth’s rotation by the Inter-
national Earth Rotation Service (IERS). Measurements
of the Earth’s rotation presented in the form of time de-
velopments of the so-called Earth Orientation Param-
eters ( EOP). Universal time ( UT1), polar motion, and
the celestial motion of the pole (precession/nutation)
are determined by Very Long-Baseline Interferometry
(VLBI). Satellite geodesy techniques, such as satellite
laser ranging (SLR) and using the Global Positioning
System (GPS), determine polar motion and rapid varia-
tions of universal time. The satellite geodesy programs
used in the IERS allow determination of the time varia-
tion of the Earth’s gravity ﬁeld. This variation reﬂects
the evolutions of the Earth’s shape and of the distribution
of mass in the planet. The programs have also detected
changes in the location of the center of mass of the Earth
relative to the crust. It is possible to investigate other
global phenomena such as the mass redistributions of the
atmosphere, oceans, and solid Earth.
Using the above experimental techniques, Universal
time and polar motion are available daily with an accu-
racy of about 50 picoseconds (ps). They are determined
from VLBI astrometric observations with an accuracy of
0.5 milliarcseconds (mas). Celestial pole motion is avail-
able every ﬁve to seven days at the same level of accuracy.
These estimations of accuracy include both short term
and long term noise. Sub-daily variations in Universal
time and polar motion are also measured on a campaign
basis.
In summary, this dynamical model accounts for a num-
ber of post-Newtonian perturbations in the motions of
the planets, the Moon, and spacecraft. Light propaga-
tion is correct to order c− 2. The equations of motion of
extended celestial bodies are valid to order c− 4. Indeed,
this dynamical model has been good enough to perform
tests of general relativity [28, 51, 52].
C. Standard modeling of small, non-gravitational
forces
In addition to the mutual gravitational interactions of
the various bodies in the solar system and the gravita-
tional forces acting on a spacecraft as a result of presence
of those bodies, it is also important to consider a num-
ber of non-gravitational forces which are important for
the motion of a spacecraft. (Books and lengthy reports
have been written about practically all of them. Consult
Ref. [57, 58] for a general introduction.)
The Jet Propulsion Laboratory’s ODP accounts for
many sources of non-gravitational accelerations. Among
them, the most relevant to this study, are: i) solar radia-
tion pressure, ii) solar wind pressure, iii) attitude-cont rol
maneuvers together with a model for unintentional space-
craft mass expulsion due to gas leakage of the propulsion
system. We can also account for possible inﬂuence of
the interplanetary media and DSN antennae contribu-
tions to the spacecraft radio tracking data and consider
the torques produced by above mentioned forces. The
Aerospace CHASMP code uses a model for gas leaks that
can be adjusted to include the eﬀects of the recoil force
due to emitted radio power and anisotropic thermal ra-
diation of the spacecraft.
In principle, one could set up complicated engineering
models to predict at least some of the eﬀects. However,
their residual uncertainties might be unacceptable for the
experiment, in spite of the signiﬁcant eﬀort required. In
fact, a constant acceleration produces a linear frequency
drift that can be accounted for in the data analysis by a
single unknown parameter.
The ﬁgure against which we compare the eﬀects of non-
gravitational accelerations on the Pioneers’ trajectorie s is
