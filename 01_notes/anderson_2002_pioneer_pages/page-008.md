# Page 8

8
A. Data acquisition
The Deep Space Network (DSN) is the network of
ground stations that are employed to track interplanetary
spacecraft [31, 32]. There are three ground DSN com-
plexes, at Goldstone, California, at Robledo de Chavela,
outside Madrid, Spain, and at Tidbinbilla, outside Can-
berra, Australia.
There are many antennae, both existing and decom-
missioned, that have been used by the DSN for space-
craft navigation. For our four spacecraft (Pioneer 10,
11, Galileo, and Ulysses), depending on the time period
involved, the following Deep Space Station (DSS) anten-
nae were among those used: (DSS 12, 14, 24) at the
California antenna complex; (DSS 42, 43, 45, 46) at the
Australia complex; and (DSS 54, 61, 62, 63) at the Spain
complex. Speciﬁcally, the Pioneers used (DSS 12, 14, 42,
43, 62, 63), Galileo used (DSS 12, 14, 42, 43, 63), and
Ulysses used (DSS 12, 14, 24, 42, 43, 46, 54, 61, 63).
The DSN tracking system is a phase coherent system.
By this we mean that an “exact” ratio exists between the
transmission and reception frequencies; i.e., 240/221 for
S-band or 880/221 for X-band [24]. (This is in distinction
to the usual concept of coherent radiation used in atomic
and astrophysics.)
Frequency is an average frequency, deﬁned as the num-
ber of cycles per unit time. Thus, accumulated phase is
the integral of frequency. High measurement precision
is attained by maintaining the frequency accuracy to 1
part per 10 12 or better (This is in agreement with the
expected Allan deviation for the S-band signals.)
The DSN F requency and Timing System (FTS):
The DSN’s FTS is the source for the high accuracy just
mentioned (see Figure 4). At its center is an hydrogen
maser that produces a precise and stable reference fre-
quency [33, 34]. These devices have Allan deviations [35]
of approximately 3 × 10− 15 to 1 × 10− 15 for integration
times of 10 2 to 10 3 seconds, respectively.
FIG. 4: Block-diagram of the DSN complex as used for radio
Doppler tracking of an interplanetary spacecraft. For more
detailed drawings and technical speciﬁcations see Ref. [31 ].
These masers are good enough so that the quality
of Doppler-measurement data is limited by thermal or
plasma noise, and not by the inherent instability of the
frequency references. Due to the extreme accuracy of
the hydrogen masers, one can very precisely characterize
the spacecraft’s dynamical variables using Doppler and
range techniques. The FTS generates a 5 MHz and 10
MHz reference frequency which is sent through the lo-
cal area network to the Digitally Controlled Oscillator
(DCO).
The Digitally Controlled Oscillator (DCO) and
Exciter: Using the highly stable output from the FTS,
the DCO, through digitally controlled frequency multi-
pliers, generates the Track Synthesizer Frequency (TSF)
of ∼ 22 MHz. This is then sent to the Exciter Assembly.
The Exciter Assembly multiplies the TSF by 96 to pro-
duce the S-band carrier signal at ∼ 2. 2 GHz. The signal
power is ampliﬁed by Traveling Wave Tubes (TWT) for
transmission. If ranging data are required, the Exciter
Assembly adds the ranging modulation to the carrier.
[The DSN tracking system has undergone many upgrades
during the 29 years of tracking Pioneer 10. During this
period internal frequencies have changed.]
This S-band frequency is sent to the antenna where
it is ampliﬁed and transmitted to the spacecraft. The
onboard receiver tracks the up-link carrier using a phase
lock loop. To ensure that the reception signal does not
interfere with the transmission, the spacecraft (e.g., Pi-
oneer) has a turnaround transponder with a ratio of
240/221. The spacecraft transmitter’s local oscillator is
phase locked to the up-link carrier. It multiplies the re-
ceived frequency by the above ratio and then re-transmits
the signal to Earth.
Receiver and Doppler Extractor: When the two-
way [36] signal reaches the ground, the receiver locks on
to the signal and tunes the Voltage Control Oscillator
(VCO) to null out the phase error. The signal is sent
to the Doppler Extractor. At the Doppler Extractor the
current transmitter signal from the Exciter is multiplied
by 240/221 (or 880/241 for X-band)) and a bias, of 1
MHz for S-band or 5 MHz for X-band [24], is added to
the Doppler. The Doppler data is no longer modulated
at S-band but has been reduced as a consequence of the
bias to an intermediate frequency of 1 or 5 MHz
Since the light travel time to and from Pioneer 10 is
long (more than 20 hours), the transmitted frequency
and the current transmitted frequency can be diﬀerent.
The diﬀerence in frequencies are recorded separately and
are accounted for in the orbit determination programs we
discuss in Section V.
Metric Data Assembly (MDA): The MDA con-
sists of computers and Doppler counters where continu-
ous count Doppler data are generated. The intermediate
frequency (IF) of 1 or 5 MHz with a Doppler modulation
is sent to the Metric Data Assembly (MDA). From the
FTS a 10 pulse per second signal is also sent to the MDA
for timing. At the MDA, the IF and the resulting Doppler
pulses are counted at a rate of 10 pulses per second. At
