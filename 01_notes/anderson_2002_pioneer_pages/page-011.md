# Page 11

11
s, 600 s and 1980 s. This input Orbit Determination File
(ODFILE) obtained from the RMDC group is the initial
data set with which both the JPL and The Aerospace
Corporation groups started their analyses. Therefore,
the initial data ﬁle already contained some common data
editing that the RMDC group had implemented through
program ﬂags, etc. The data set we started with had
already been compressed to 60 s. So, perhaps there were
some blunders that had already been removed using the
initial STRIPPER program.
The orbit analyst manually edits the remaining cor-
rupted data points. Editing is done either by plotting
the data residuals and deleting them from the ﬁt or plot-
ting weighted data residuals. That is, the residuals are
divided by the standard deviation assigned to each data
point and plotted. This gives the analyst a realistic view
of the data noise during those times when the data was
obtained while looking through the solar plasma. Apply-
ing an “ N -σ ” ( σ is the standard deviation) test, where
N is the choice of the analyst (usually 4-10) the analyst
can delete those points that lie outside the N -σ rejec-
tion criterion without being biased in his selection. The
N -σ test, implemented in CHASMP, is very useful for
data taken near solar conjunction since the solar plasma
adds considerable noise to the data. This criterion later
was changed to a similar criteria that rejects all data
with residuals in the ﬁt extending for more than ±0. 025
Hz from the mean. Contrariwise, the JPL analysis edits
only very corrupted data; e.g., a blunder due to a phase
lock loss, data with bad spin calibration, etc. Essentially
the Aerospace procedure eliminates data in the tails of
the Gaussian probability frequency distribution whereas
the JPL procedure accepts this data.
If needed or desired, the orbit analyst can choose to
perform an additional data compression of the origi-
nal navigation data. The JPL analysis does not apply
any additional data compression and uses all the orig-
inal data from the ODFILE as opposed to Aerospace’s
approach. Aerospace makes an additional compression
of data within CHASMP. It uses the longest available
data integration times which can be composed from ei-
ther summing up adjacent data intervals or by using data
spans with duration ≥ 600 s. (Eﬀectively Aerospace
prefers 600 and 1980 second data intervals and applies
a low-pass ﬁlter.)
The total count of corrupted data points is about 10%
of the total raw data points. The analysts’ judgments
play an important role here and is one of the main rea-
sons that JPL and Aerospace have slightly diﬀerent re-
sults. (See Sections Vand VI.) In Section Vwe will show
a typical plot (Figure 8 below) with outliers present in
the data. Many more outliers are oﬀ the plot. One would
expect that the two diﬀerent strategies of data compres-
sion used by the two teams would result in signiﬁcantly
diﬀerent numbers of total data points used in the two
independent analyses. The inﬂuence of this fact on the
solution estimation accuracy will be addressed in Section
VI below.
D. Data weighting
Considerable eﬀort has gone into accurately estimat-
ing measurement errors in the observations. These errors
provide the data weights necessary to accurately estimate
the parameter adjustments and their associated uncer-
tainties. To the extent that measurement errors are accu-
rately modeled, the parameters extracted from the data
will be unbiased and will have accurate sigmas assigned
to them. Both JPL and Aerospace assign a standard un-
certainty of 1 mm/s over a 60 second count time for the
S–band Pioneer Doppler data. (Originally the JPL team
was weighting the data by 2 mm/s uncertainty.)
A change in the DSN antenna elevation angle also di-
rectly aﬀects the Doppler observables due to tropospheric
refraction. Therefore, to correct for the inﬂuence of the
Earth’s troposphere the data can also be deweighted for
low elevation angles. The phenomenological range cor-
rection is given as
σ = σ nominal
(
1 + 18
(1 + θ E)2
)
, (2)
where σ nominal is the basic standard deviation (in Hz)
and θ E is the elevation angle in degrees [40]. Each leg
is computed separately and summed. For Doppler the
same procedure is used. First, Eq. (2) is multiplied by
√
60 s/T c, where Tc is the count time. Then a numerical
time diﬀerentiation of Eq. (2) is performed. That is,
Eq. (2) is diﬀerenced and divided by the count time, Tc.
(For more details on this standard technique see Refs.
[41]-[44].)
There is also the problem of data weighting for data
inﬂuenced by the solar corona. This will be discussed in
Section IV D.
E. Spin calibration of the data
The radio signals used by DSN to communicate with
spacecraft are circularly polarized. When these signals
are reﬂected from spinning spacecraft antennae a Doppler
bias is introduced that is a function of the spacecraft spin
rate. Each revolution of the spacecraft adds one cycle
of phase to the up-link and the down-link. The up-link
cycle is multiplied by the turn around ratio 240/221 so
that the bias equals (1+240/221) cycles per revolution of
the spacecraft.
High-rate spin data is available for Pioneer 10 only
up to July 17, 1990, when the DSN ceased doing spin
calibrations. (See Section II B.) After this date, in or-
der to reconstruct the spin behavior for the entire data
span and thereby account for the spin bias in the Doppler
signal, both analyses modeled the spin by performing in-
terpolations between the data points. The JPL interpo-
lation was non-linear with a high-order polynomial ﬁt of
the data. (The polynomial was from second up to sixth
order, depending on the data quality.) The CHASMP
interpolation was linear between the spin data points.
