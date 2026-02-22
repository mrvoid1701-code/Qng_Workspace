# Page 25

25
dependently and then subtracting these solutions (given
in Table I) from the ﬁts within the corresponding data
intervals.
FIG. 13: ODP Doppler residuals in Hz for the entire Pioneer
10 data span. The two solid vertical lines in the upper part of
the plot indicate the boundaries between data Intervals I/I I
and II/III, respectively. Maneuver times are indicated by t he
vertical dashed lines in the lower part of the plot.
One can easily see the very close agreement with the
CHASMP residuals of Figure 9, which go up to 14 De-
cember 1994.
The Pioneer 11 number is signiﬁcantly higher. A de-
viation is not totally unexpected since the data was rela-
tively noisy, was from much closer in to the Sun, and was
taken during a period of high solar activity. We also do
not have the same handle on spin-rate change eﬀects as
we did for Pioneer 10. We must simply take the number
for what it is, and give the basic JPL result for Pioneer
11 as aP = 8. 46 × 10− 8 cm/s2.
Now look at the batch-sequential results in row 3 of Ta-
ble I. First, note that the statistical errors are an order
of magnitude larger than for WLS. This is not surprising
since: i) the process noise signiﬁcantly aﬀects the preci-
sion, ii) BSF smoothes the data and the data from the
various intervals is more correlated than in WLS. The ef-
fects of all this are that all four numbers change so as to
make them all closer to each other, but yet all the num-
bers vary by less than 2 σ from their WLS counterparts.
Finally, there is the annual term. It remains in the data
(for both Pioneers 10 and 11). A representation of it can
be seen in a 1-day batch-sequential averaged over all 11.5
years. It yielded a result aP = (7. 77± 0. 16)× 10− 8 cm/s2,
consistent with the other numbers/errors, but with an
added annual oscillation. In the following subsection we
will compare JPL results showing the annual term with
the counterpart Aerospace results.
We will argue in Section IX C that this annual term
is due to the inability to model the angles of the Pio-
neers’ orbits accurately enough. [Note that this annual
term is not to be confused with a small oscillation seen
in Figure 8 that can be caused by mispointing towards
the spacecraft by the ﬁt programs.]
C. Recent results using The Aerospace
Corporation software
As part of an ongoing upgrade to CHASMP’s accuracy,
Aerospace has used Pioneer 10 and 11 as a test bed to
conﬁrm the revision’s improvement. In accordance with
the JPL results of Section VI B, we used the new version
of CHASMP to concentrate on the Pioneer 10 and 11
data. The physical models are basically the same ones
that JPL used, but the techniques and methods used are
largely diﬀerent. (See Section IX B.)
The new results from the Aerospace Corporation’s
software are based on ﬁrst improving the Planetary
Ephemeris and Earth orientation and spacecraft spin
models required by the program. That is: i) the spin
data ﬁle has been included with full detail; ii) a newer
JPL Earth Orientation Parameters ﬁle was used; iii) all
IERS tidal terms were included; iv) plate tectonics were
included; v) DE405 was used; vi) no a priori information
on the solved for parameters was included in the ﬁt; vii)
Pioneer 11 was considered, viii) the Pioneer 10 data set
used was extended to 14 Feb. 1998. Then the Doppler
data was reﬁtted.
Beginning with this last point: CHASMP uses the
same original data ﬁle, but it performs an additional data
compression. This compression combines the longest con-
tiguous data composed of adjacent data intervals or data
spans with duration ≥ 600 s (eﬀectively it prefers 600
and 1980 second data intervals). It ignores short-time
data points. Also, Aerospace uses an N- σ /ﬁxed bound-
ary rejection criteria that rejects all data in the ﬁt with a
residual greater than ±0. 025 Hz. These rejection criteria
resulted in the loss of about 10 % of the original data
for both Pioneers 10 and 11. In particular, the last ﬁve
months of Pioneer 10 data, which was all of data-lengths
less than 600 s, was ignored. Once these data compres-
sion/cuts were made, CHASMP used 10,499 of its 11,610
data points for Pioneer 10 and 4,380 of its 5,137 data
points for Pioneer 11.
Because of the spin-anomaly in the Pioneer 10 data,
the data arc was also divided into three time intervals
(although the I/II boundary was taken as 31 August
1990 [85]). In what was especially useful, the Aerospace
analysis uses direct propagation of the trajectory data
and solves for the parameter of interest only for the data
within a particular data interval. That means the three
interval results were truly independent. Pioneer 11 was
ﬁt as a single arc.
Three types of runs are listed, with: i) no corona; ii)
with Cassini corona model of Sections IV D and VII C;
and iii) with the Cassini corona model, but added are
corona data weighting (Section IV D) and the time-
variation called “F10.7” [65]. (The number 10.7 labels
the wavelength of solar radiation, λ =10.7 cm, that, in
our analysis, is averaged over 81 days.)
The results are given in rows 4-6 of Table I. The no
corona results (row 4) are in good agreement with the
Sigma results of the ﬁrst row. This is especially true
