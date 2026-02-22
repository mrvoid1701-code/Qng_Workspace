# Page 31

31
Long-term frequency stability tests are conducted with
the exciter/transmitter subsystems and the DSN’s radio-
science open-loop subsystem. An uplink signal gener-
ated by the exciter is translated at the antenna by a test
translator to a downlink frequency. (See Section III.)
The downlink signal is then passed through the RF-IF
downconverter present at the antenna and into the ra-
dio science receiver chain [31]. This technique allows the
processes to be synchronized in the DSN complex based
on the frequency standards whose Allan variances are of
the order of σ y ∼ 10− 14 − 10− 15 for integration time in
the range from 10 s to 10 3 s. For the S-band frequen-
cies of the Pioneers, the corresponding Allan variances
are 1.3 × 10− 12 and 1.0 × 10− 12, respectively, for a 10 3
s Doppler integration time.
Phase-stability testing characterizes stability over ver y
short integration times; that is, spurious signals whose
frequencies are very close to the carrier (frequency). The
phase noise region is deﬁned to be frequencies within 100
kHz of the carrier. Both amplitude and phase variations
appear as phase noise. Phase noise is quoted in dB rela-
tive to the carrier, in a 1 Hz band at a speciﬁed deviation
from the carrier; for example, dBc-Hz at 10 Hz. Thus,
for the frequency 1 Hz, the noise level is at −51 dBc and
10 Hz corresponds to −60 dBc. This was not signiﬁcant
for our study.
Finally, the inﬂuence of the clock stability on the de-
tected acceleration, aP , may be estimated based on the
reported Allan variances for the clocks, σ y. Thus, the
standard ‘single measurement’ error on acceleration as
derived by the time derivative of the Doppler frequency
data is ( cσ y)/τ , where the Allan variance, σ y, is calcu-
lated for 1000 s Doppler integration time, and τ is the
signal averaging time. This formula provides a good rule
of thumb when the Doppler power spectral density func-
tion obeys a 1 /f ﬂicker-noise law, which is approximately
the case when plasma noise dominates the Doppler error
budget. Assume a worst case scenario, where only one
clock was used for the whole 11 years study. (In reality
each DSN station has its own atomic clock.) To estimate
the inﬂuence of that one clock on the reported accuracy
of the detected anomaly aP , combine σ y = ∆ ν/ν 0, the
fractional Doppler frequency shift from the reference fre-
quency of ν 0 =∼ 2. 29 GHz, with the estimate for the Al-
lan variance, σ y = 1. 3× 10− 12. This yields a number that
characterizes the upper limit for a frequency uncertainty
introduced in a single measurement by the instabilities
in the atomic clock: σ ν = ν 0σ y = 2 . 98 × 10− 3 Hz for a
103 Doppler integration time.
In order to derive an estimate for the total eﬀect, re-
call that the Doppler observation technique is essentially
a continuous count of the total number of complete fre-
quency circles during observational time. Within a year
one can have as many as N ≈ 3. 156 × 103 indepen-
dent single measurements of the clock with duration 10 3
seconds. This yields an upper limit for the contribu-
tion of atomic clock instability on the frequency drift of
σ clock = σ ν/
√
N ≈ 5. 3 × 10− 5 Hz/year. But in Section
V B we noted that the observed aP corresponds to a fre-
quency drift of about 0.2 Hz/year, so the error in aP is
about 0 . 0003 × 10− 8 cm/s2. Since all data is not inte-
grated over 1,000 seconds and is data is not available for
all time, we increase the numerical factor to 0 . 001, which
is still negligible to us. [But further, this upper limit
for the error becomes even smaller if one accounts for
the number of DSN stations and corresponding atomic
clocks that were used for the study.]
Therefore, we conclude that the clocks are not a con-
tributing factor to the anomalous acceleration at a mean-
ingfully level. We will return to this issue in Section XI D
where we will discuss a number of phenomenological time
models that were used to ﬁt the data.
G. DSN antennae complex
The mechanical structures which support the reﬂecting
surfaces of the antenna are not perfectly stable. Among
the numerous eﬀects inﬂuencing the DSN antennae per-
formance, we are only interested in those whose behav-
ior might contribute to the estimated solutions for aP .
The largest systematic instability over a long period is
due to gravity loads and the aging of the structure. As
discussed in [102], antenna deformations due to gravity
loads should be absorbed almost entirely into biases of
the estimated station locations and clock oﬀsets. There-
fore, they will have little eﬀect on the derived solutions
for the purposes of spacecraft navigation.
One can also consider ocean loading, wind loading,
thermal expansion, and aging of the structure. We
found none of these can produce the constant drift in
the Doppler frequency on a time scale comparable to the
Pioneer data. Also, routine tests are performed by DSN
personnel on a regular basis to access all the eﬀects that
may contribute to the overall performance of the DSN
complex. The information is available and it shows all pa-
rameters are in the required ranges. Detailed assessments
of all these eﬀect on the astrometric VLBI solutions were
published in [35, 102]. The results for the astrometric
errors introduced by the above factors may be directly
translated to the error budget for the Pioneers, scaled by
the number of years. It yields a negligible contribution.
Our analyses also estimated errors introduced by a
number of station-speciﬁc parameters. These include the
error due to imperfect knowledge in a DSN station lo-
cation, errors due to troposphere and ionosphere models
for diﬀerent stations, and errors due to the Faraday rota-
tion eﬀects in the Earth’s atmosphere. Our analysis indi-
cates that at most these eﬀects would produce a distance-
and/or time-dependent drifts that would be easily notice-
able in the radio Doppler data. What is more important
is that none of the eﬀects would be able to produce a con-
stant drift in the Doppler residuals of Pioneers over such a
long time scale. The updated version of the ODP, Sigma,
routinely accounts for these error factors. Thus, we run
covariance analysis for the whole set of these parameters
