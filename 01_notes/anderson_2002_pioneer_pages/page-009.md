# Page 9

9
each tenth of a second, the number of Doppler pulses
are counted. A second counter begins at the instant the
ﬁrst counter stops. The result is continuously-counted
Doppler data. (The Doppler data is a biased Doppler
of 1 MHz, the bias later being removed by the analyst
to obtain the true Doppler counts.) The Range data (if
present) together with the Doppler data is sent separately
to the Ranging Demodulation Assembly. The accompa-
nying Doppler data is used to rate aid (i.e., to “freeze”
the range signal) for demodulation and cross correlation.
Data Communication: The total set of tracking
data is sent by local area network to the communica-
tion center. From there it is transmitted to the Goddard
Communication Facility via commercial phone lines or by
government leased lines. It then goes to JPL’s Ground
Communication Facility where it is received and recorded
by the Data Records Subsystem.
B. Radio Doppler and range techniques
Various radio tracking strategies are available for de-
termining the trajectory parameters of interplanetary
spacecraft. However, radio tracking Doppler and range
techniques are the most commonly used methods for nav-
igational purposes. The position and velocities of the
DSN tracking stations must be known to high accuracy.
The transformation from a Earth ﬁxed coordinate sys-
tem to the International Earth Rotation Service (IERS)
Celestial System is a complex series of rotations that in-
cludes precession, nutation, variations in the Earth’s ro-
tation ( UT1-UTC) and polar motion.
Calculations of the motion of a spacecraft are made
on the basis of the range time-delay and/or the Doppler
shift in the signals. This type of data was used to deter-
mine the positions, the velocities, and the magnitudes of
the orientation maneuvers for the Pioneer, Galileo, and
Ulysses spacecraft considered in this study.
Theoretical modeling of the group delays and phase de-
lay rates are done with the orbit determination software
we describe in the next section.
Data types: Our data describes the observations that
are the basis of the results of this paper. We receive
our data from DSN in closed-loop mode, i.e., data that
has been tracked with phase lock loop hardware. (Open
loop data is tape recorded but not tracked by phase lock
loop hardware.) The closed-loop data constitutes our
Archival Tracking Data File (ATDF), which we copy [37]
to the National Space Science Data Center (NSSDC) on
magnetic tape. The ATDF ﬁles are stored on hard disk
in the RMDC (Radio Metric Data Conditioning group)
of JPL’s Navigation and Mission Design Section. We
access these ﬁles and run standard software to produce
an Orbit Data File for input into the orbit determination
programs which we use. (See Section V.)
The data types are two-way and three-way [36] Doppler
and two-way range. (Doppler and range are deﬁned in
the following two subsections.) Due to unknown clock
oﬀsets between the stations, three-way range is generally
not taken or used.
The Pioneer spacecraft only have two- and three-way
S-band [24] Doppler. Galileo also has S-band range data
near the Earth. Ulysses has two- and three-way S-band
up-link and X-band [24] down-link Doppler and range as
well as S-band up-link and S-band down-link, although
we have only processed the Ulysses S-band up-link and
X-band down-link Doppler and range.
1. Doppler experimental techniques and strategy
In Doppler experiments a radio signal transmit-
ted from the Earth to the spacecraft is coherently
transponded and sent back to the Earth. Its frequency
change is measured with great precision, using the hy-
drogen masers at the DSN stations. The observable is
the DSN frequency shift [38]
∆ν (t) = ν 0
1
c
dℓ
dt , (1)
where ℓ is the overall optical distance (including diﬀrac-
tion eﬀects) traversed by a photon in both directions.
[In the Pioneer Doppler experiments, the stability of
the fractional drift at the S-band is on the order of
∆ν/ν 0 ≃ 10− 12, for integration times on the order of
103 s.] Doppler measurements provide the “range rate”
of the spacecraft and therefore are aﬀected by all the
dynamical phenomena in the volume between the Earth
and the spacecraft.
Expanding upon what was discussed in Section III A,
the received signal and the transmitter frequency (both
are at S-band) as well as a 10 pulse per second timing
reference from the FTS are fed to the Metric Data Assem-
bly (MDA). There the Doppler phase (diﬀerence between
transmitted and received phases plus an added bias) is
counted. That is, digital counters at the MDA record
the zero crossings of the diﬀerence (i.e., Doppler, or al-
ternatively the beat frequency of the received frequency
and the exciter frequency). After counting, the bias is
removed so that the true phase is produced.
The system produces “continuous count Doppler” and
it uses two counters. Every tenth of a second, a Doppler
phase count is recorded from one of the counters. The
other counter continues the counts. The recording alter-
nates between the two counters to maintain a continuous
unbroken count. The Doppler counts are at 1 MHz for
S-band or 5 MHz for X-band. The wavelength of each S-
band cycle is about 13 cm. Dividers or “time resolvers”
further subdivide the cycle into 256 parts, so that frac-
tional cycles are measured with a resolution of 0.5 mm.
This accuracy can only be maintained if the Doppler is
continuously counted (no breaks in the count) and coher-
ent frequency standards are kept throughout the pass. It
should be noted that no error is accumulated in the phase
count as long as lock is not lost. The only errors are the
