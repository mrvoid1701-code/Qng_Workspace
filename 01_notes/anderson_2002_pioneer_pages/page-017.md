# Page 17

17
direction. However the gas leak rapidly decays and be-
comes negligible after 20 days or so.
F. Orbit determination procedure
Our orbit determination procedure ﬁrst determines the
spacecraft’s initial position and velocity in a data inter-
val. For each data interval, we then estimate the mag-
nitudes of the orientation maneuvers, if any. The anal-
yses are modeled to include the eﬀects of planetary per-
turbations, radiation pressure, the interplanetary media ,
general relativity, and bias and drift in the Doppler and
range (if available). Planetary coordinates and solar sys-
tem masses are obtained using JPL’s Export Planetary
Ephemeris DE405, where DE stands for the Development
Ephemeris. [Earlier in the study, DE200 was used. See
Section V A.]
We include models of precession, nutation, sidereal ro-
tation, polar motion, tidal eﬀects, and tectonic plates
drift. Model values of the tidal deceleration, nonunifor-
mity of rotation, polar motion, Love numbers, and Chan-
dler wobble are obtained observationally, by means of
Lunar and Satellite Laser Ranging (LLR and SLR) tech-
niques and VLBI. Previously they were combined into
a common publication by either the International Earth
Rotation Service (IERS) or by the United States Naval
Observatory (USNO). Currently this information is pro-
vided by the ICRF. JPL’s Earth Orientation Parameters
(EOP) is a major source contributor to the ICRF.
The implementation of the J2000.0 reference coordi-
nate system in CHASMP involves only rotation from the
Earth-ﬁxed to the J2000.0 reference frame and the use
of JPL’s DE200 planetary ephemeris [68]. The rota-
tion from J2000.0 to Earth-ﬁxed is computed from
a series of rotations which include precession, nutation,
the Greenwich hour angle, and pole wander. Each of
these general categories is also a multiple rotation and
is treated separately by most software. Each separate
rotation matrix is chain multiplied to produce the ﬁnal
rotation matrix.
CHASMP, however, does not separate precession and
nutation. Rather, it combines them into a single matrix
operation. This is achieved by using a diﬀerent set of an-
gles to describe precession than is used in the ODP. (See
a description of the standard set of angles in [69].) These
angles separate luni-solar precession from planetary pre-
cession. Luni-solar precession, being the linear term of
the nutation series for the nutation in longitude, is com-
bined with the nutation in longitude from the DE200
ephemeris tape [70].
Both JPL’s ODP and The Aerospace Corporation’s
CHASMP use the JPL/Earth Orientation Parameters
(EOP) values. This could be a source of common er-
ror. However the comparisons between EOP and IERS
show an insigniﬁcant diﬀerence. Also, only secular terms,
such as precession, can contribute errors to the anoma-
lous acceleration. Errors in short period terms are not
correlated with the anomalous acceleration.
G. Parameter estimation strategies
During the last few decades, the algorithms of orbital
analysis have been extended to incorporate Kalman-ﬁlter
estimation procedure that is based on the concept of
“process noise” (i.e., random, non-systematic forces, or
random-walk eﬀects). This was motivated by the need to
respond to the signiﬁcant improvement in observational
accuracy and, therefore, to the increasing sensitivity to
numerous small perturbing factors of a stochastic nature
that are responsible for observational noise. This ap-
proach is well justiﬁed when one needs to make accurate
predictions of the spacecraft’s future behavior using only
the spacecraft’s past hardware and electronics state his-
tory as well as the dynamic environment conditions in
the distant craft’s vicinity. Modern navigational softwar e
often uses Kalman ﬁlter estimation since it more easily
allows determination of the temporal noise history than
does the weighted least-squares estimation.
To take advantage of this while obtaining JPL’s orig-
inal results [12, 13] discussed in Section V, JPL used
batch-sequential methods with variable batch sizes and
process noise characteristics. That is, a batch-sequentia l
ﬁltering and smoothing algorithm with process noise was
used with ODP. In this approach any small anomalous
forces may be treated as stochastic parameters aﬀecting
the spacecraft trajectory. As such, these parameters are
also responsible for the stochastic noise in the observa-
tional data. To better characterize these noise sources,
one splits the data interval into a number of constant or
variable size batches and makes assumptions on possible
statistical properties of these noise factors. One then est i-
mates the mean values of the unknown parameters within
the batch and also their second statistical moments.
Using batches has the advantage of dealing with a
smaller number of experimental data segments. We ex-
perimented with a number of diﬀerent constant batch
sizes; namely, 0, 5, 30, and 200 day batch sizes. (Later
we also used 1 and 10 day batch sizes.) In each batch
one estimates the same number of desired parameters.
So, one expects that the smaller the batch size the larger
the resulting statistical errors. This is because a smaller
number of data points is used to estimate the same num-
ber of parameters. Using the entire data interval as a
single batch while changing the process noise a priori val-
ues is expected in principle (see below) to yield a result
identical to the least-squares estimation. In the single
batch case, it would produce only one solution for the
anomalous acceleration.
There is another important parameter that was taken
into account in the statistical data analysis reported here .
This is the expected correlation time for the underly-
ing stochastic processes (as well as the process noise)
that may be responsible for the anomalous acceleration.
For example, using a zero correlation time is useful in
