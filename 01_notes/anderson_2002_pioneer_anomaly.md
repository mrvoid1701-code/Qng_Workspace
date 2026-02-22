# Source Text

- Source: `data\trajectory\sources\anderson_2002_pioneer_anomaly.pdf`
- Generated: `2026-02-17 18:22:15`

## Page 1

arXiv:gr-qc/0104064v5  10 Mar 2005
Study of the anomalous acceleration of Pioneer 10 and 11
John D. Anderson, ∗a Philip A. Laing, †b Eunice L. Lau, ‡a
Anthony S. Liu, §c Michael Martin Nieto, ¶d and Slava G. Turyshev ∗∗a
aJet Propulsion Laboratory, California Institute of Techno logy, Pasadena, CA 91109
bThe Aerospace Corporation, 2350 E. El Segundo Blvd., El Segu ndo, CA 90245-4691
cAstrodynamic Sciences, 2393 Silver Ridge Ave., Los Angeles , CA 90039
dTheoretical Division (MS-B285), Los Alamos National Labor atory,
University of California, Los Alamos, NM 87545
(Dated: 11 April 2002)
Our previous analyses of radio Doppler and ranging data from distant spacecraft in the solar
system indicated that an apparent anomalous acceleration i s acting on Pioneer 10 and 11, with a
magnitude aP ∼ 8 × 10− 8 cm/s2, directed towards the Sun. Much eﬀort has been expended look ing
for possible systematic origins of the residuals, but none h as been found. A detailed investigation of
eﬀects both external to and internal to the spacecraft, as we ll as those due to modeling and compu-
tational techniques, is provided. We also discuss the metho ds, theoretical models, and experimental
techniques used to detect and study small forces acting on in terplanetary spacecraft. These include
the methods of radio Doppler data collection, data editing, and data reduction.
There is now further data for the Pioneer 10 orbit determinat ion. The extended Pioneer 10 data
set spans 3 January 1987 to 22 July 1998. [For Pioneer 11 the sh orter span goes from 5 January
1987 to the time of loss of coherent data on 1 October 1990.] Wi th these data sets and more
detailed studies of all the systematics, we now give a result , of aP = (8 . 74 ± 1. 33) × 10− 8 cm/ s2.
(Annual/diurnal variations on top of aP , that leave aP unchanged, are also reported and discussed.)
PACS numbers: 04.80.-y, 95.10.Eg, 95.55.Pe
I. INTRODUCTION
Some thirty years ago, on 2 March 1972, Pioneer 10
was launched on an Atlas/Centaur rocket from Cape
Canaveral. Pioneer 10 was Earth’s ﬁrst space probe to
an outer planet. Surviving intense radiation, it success-
fully encountered Jupiter on 4 December 1973 [1]-[6]. In
trail-blazing the exploration of the outer solar system,
Pioneer 10 paved the way for, among others, Pioneer
11 (launched on 5 April 1973), the Voyagers, Galileo,
Ulysses, and the upcoming Cassini encounter with Sat-
urn. After Jupiter and (for Pioneer 11) Saturn encoun-
ters, the two spacecraft followed hyperbolic orbits near
the plane of the ecliptic to opposite sides of the solar sys-
tem. Pioneer 10 was also the ﬁrst mission to enter the
edge of interstellar space. That major event occurred in
June 1983, when Pioneer 10 became the ﬁrst spacecraft
to “leave the solar system” as it passed beyond the orbit
of the farthest known planet.
The scientiﬁc data collected by Pioneer 10/11 has
yielded unique information about the outer region of the
solar system. This is due in part to the spin-stabilization
of the Pioneer spacecraft. At launch they were spinning
∗Electronic address: john.d.anderson@jpl.nasa.gov
†Electronic address: Philip.A.Laing@aero.org
‡Electronic address: Eunice.L.Lau@jpl.nasa.gov
§Deceased (13 November 2000).
¶ Electronic address: mmn@lanl.gov
∗∗turyshev@jpl.nasa.gov
at approximately 4.28 and 7.8 revolutions per minute
(rpm), respectively, with the spin axes running through
the centers of the dish antennae. Their spin-stabilization s
and great distances from the Earth imply a minimum
number of Earth-attitude reorientation maneuvers are re-
quired. This permits precise acceleration estimations, to
the level of 10 − 8 cm/s2 (single measurement accuracy av-
eraged over 5 days). Contrariwise, a Voyager-type three-
axis stabilized spacecraft is not well suited for a precise
celestial mechanics experiment as its numerous attitude-
control maneuvers can overwhelm the signal of a small
external acceleration.
In summary, Pioneer spacecraft represent an ideal sys-
tem to perform precision celestial mechanics experiments.
It is relatively easy to model the spacecraft’s behavior
and, therefore, to study small forces aﬀecting its motion
in the dynamical environment of the solar system. In-
deed, one of the main objectives of the Pioneer extended
missions (post Jupiter/Saturn encounters) [5] was to per-
form accurate celestial mechanics experiments. For in-
stance, an attempt was made to detect the presence of
small bodies in the solar system, primarily in the Kuiper
belt. It was hoped that a small perturbation of the
spacecraft’s trajectory would reveal the presence of these
objects [7]-[9]. Furthermore, due to extremely precise
navigation and a high quality tracking data, the Pioneer
10 scientiﬁc program also included a search for low fre-
quency gravitational waves [10, 11].
Beginning in 1980, when at a distance of 20 astronom-
ical units (AU) from the Sun the solar-radiation-pressure
acceleration on Pioneer 10 away from the Sun had de-
creased to < 5 × 10− 8 cm/s2, we found that the largest

## Page 2

2
systematic error in the acceleration residuals was a con-
stant bias, aP , directed toward the Sun. Such anoma-
lous data have been continuously received ever since. Jet
Propulsion Laboratory (JPL) and The Aerospace Corpo-
ration produced independent orbit determination analy-
ses of the Pioneer data extending up to July 1998. We
ultimately concluded [12, 13], that there is an unmodeled
acceleration, aP , towards the Sun of ∼ 8 × 10− 8 cm/s2
for both Pioneer 10 and Pioneer 11.
The purpose of this paper is to present a detailed expla-
nation of the analysis of the apparent anomalous, weak,
long-range acceleration of the Pioneer spacecraft that we
detected in the outer regions of the solar system. We at-
tempt to survey all sensible forces and to estimate their
contributions to the anomalous acceleration. We will dis-
cuss the eﬀects of these small non-gravitational forces
(both generated on-board and external to the vehicle) on
the motion of the distant spacecraft together with the
methods used to collect and process the radio Doppler
navigational data.
We begin with descriptions of the spacecraft and other
systems and the strategies for obtaining and analyzing
information from them. In Section II we describe the
Pioneer (and other) spacecraft. We provide the reader
with important technical information on the spacecraft,
much of which is not easily accessible. In Section III we
describe how raw data is obtained and analyzed and in
Section IV we discuss the basic elements of a theoretical
foundation for spacecraft navigation in the solar system.
The next major part of this manuscript is a description
and analysis of the results of this investigation. We ﬁrst
describe how the anomalous acceleration was originally
identiﬁed from the data of all the spacecraft in Section
V [12, 13]. We then give our recent results in Section
VI. In the following three sections we discuss possible
experimental systematic origins for the signal. These in-
clude systematics generated by physical phenomena from
sources external to (Section VII) and internal to (Sec-
tion VIII) the spacecraft. This is followed by Section IX,
where the accuracy of the solution for aP is discussed. In
the process we go over possible numerical/calculational
errors/systematics. Sections VII-IX are then summarized
in the total error budget of Section X.
We end our presentation by ﬁrst considering possible
unexpected physical origins for the anomaly (Section XI).
In our conclusion, Section XII, we summarize our results
and suggest venues for further study of the discovered
anomaly.
II. THE PIONEER AND OTHER SP ACECRAFT
In this section we describe in some detail the Pioneer
10 and 11 spacecraft and their missions. We concentrate
on those spacecraft systems that play important roles in
maintaining the continued function of the vehicles and
in determining their dynamical behavior in the solar sys-
tem. Speciﬁcally we present an overview of propulsion
and attitude control systems, as well as thermal and com-
munication systems.
Since our analysis addresses certain results from the
Galileo and Ulysses missions, we also give short descrip-
tions of these missions in the ﬁnal subsection.
A. General description of the Pioneer spacecraft
Although some of the more precise details are often
diﬃcult to uncover, the general parameters of the Pi-
oneer spacecraft are known and well documented [1]-[6].
The two spacecraft are identical in design [14]. At launch
each had a “weight” (mass) of 259 kg. The “dry weight”
of the total module was 223 kg as there were 36 kg of
hydrazine propellant [15, 16]. The spacecraft were de-
signed to ﬁt within the three meter diameter shroud of
an added third stage to the Atlas/Centaur launch vehi-
cle. Each spacecraft is 2.9 m long from its base to its
cone-shaped medium-gain antenna. The high gain an-
tenna (HGA) is made of aluminum honeycomb sandwich
material. It is 2.74 m in diameter and 46 cm deep in the
shape of a parabolic dish. (See Figures 1 and 2.)
FIG. 1: NASA photo #72HC94, with caption “The Pioneer
F spacecraft during a checkout with the launch vehicle third
stage at Cape Kennedy.” Pioneer F became Pioneer 10.
The main equipment compartment is 36 cm deep.
The hexagonal ﬂat top and bottom have 71 cm long
sides. The equipment compartment provides a thermally
controlled environment for scientiﬁc instruments. Two
three-rod trusses, 120 degrees apart, project from two
sides of the equipment compartment. At their ends, each
holds two SNAP-19 (Space Nuclear Auxiliary Power,

## Page 3

3
FIG. 2: A drawing of the Pioneer spacecraft.
model 19) RTGs (Radioisotope Thermoelectric Gener-
ators) built by Teledyne Isotopes for the Atomic En-
ergy Commission. These RTGs are situated about 3 m
from the center of the spacecraft and generate its electric
power. [We will go into more detail on the RTGs in Sec-
tion VIII.] A third single-rod boom, 120 degrees from the
other two, positions a magnetometer about 6.6 m from
the spacecraft’s center. All three booms were extended
after launch. With the mass of the magnetometer being
5 kg and the mass of each of the four RTGs being 13.6
kg, this conﬁguration deﬁnes the main moment of inertia
along the z-spin-axis. It is about Iz ≈ 588. 3 kg m 2 [17].
[Observe that this all left only about 164 kg for the main
bus and superstructure, including the antenna.]
Figures 1 and 2 show the arrangement within the
spacecraft equipment compartment. The majority of the
spacecraft electrical assemblies are located in the cen-
tral hexagonal portion of the compartment, surrounding
a 16.5-inch-diameter spherical hydrazine tank. Most of
the scientiﬁc instruments’ electronic units and internall y-
mounted sensors are in an instrument bay (“squashed”
hexagon) mounted on one side of the central hexagon.
The equipment compartment is in an aluminum honey-
comb structure. This provides support and meteoroid
protection. It is covered with insulation which, together
with louvers under the platform, provides passive thermal
control. [An exception is from oﬀ-on control by thermal
power dissipation of some subsystems. (See Sec. VIII).]
B. Propulsion and attitude control systems
Three pairs of these rocket thrusters near the rim of the
HGA provide a threefold function of spin-axis precession,
mid-course trajectory correction, and spin control. Each
of the three thruster pairs develops its repulsive jet force
from a catalytic decomposition of liquid hydrazine in a
small rocket thrust chamber attached to the oppositely-
directed nozzle. The resulted hot gas is then expended
through six individually controlled thruster nozzles to ef -
fect spacecraft maneuvers.
The spacecraft is attitude-stabilized by spinning about
an axis which is parallel to the axis of the HGA. The
nominal spin rate for Pioneer 10 is 4.8 rpm. Pioneer 11
spins at approximately 7.8 rpm because a spin-controlling
thruster malfunctioned during the spin-down shortly af-
ter launch. [Because of the danger that the thruster’s
valve would not be able to close again, this particular
thruster has not been used since.] During the mission
an Earth-pointing attitude is required to illuminate the
Earth with the narrow-beam HGA. Periodic attitude ad-
justments are required throughout the mission to com-
pensate for the variation in the heliocentric longitude
of the Earth-spacecraft line. [In addition, correction of
launch vehicle injection errors were required to provide
the desired Jupiter encounter trajectory and Saturn (for
Pioneer 11) encounter trajectory.] These velocity vector
adjustments involved reorienting the spacecraft to direct

## Page 4

4
the thrust in the desired direction.
There were no anomalies in the engineering telemetry
from the propulsion system, for either spacecraft, dur-
ing any mission phase from launch to termination of the
Pioneer mission in March 1997. From the viewpoint of
mission operations at the NASA/Ames control center,
the propulsion system performed as expected, with no
catastrophic or long-term pressure drops in the propul-
sion tank. Except for the above-mentioned Pioneer 11
spin-thruster incident, there was no malfunction of the
propulsion nozzles, which were only opened every few
months by ground command. The fact that pressure was
maintained in the tank has been used to infer that no
impacts by Kuiper belt objects occurred, and a limit has
been placed on the size and density distribution of such
objects [7], another useful scientiﬁc result.
For attitude control, a star sensor (referenced to Cano-
pus) and two sunlight sensors provided reference for ori-
entation and roll maneuvers. The star sensor on Pioneer
10 became inoperative at Jupiter encounter, so the sun
sensors were used after that. For Pioneer 10, spin calibra-
tion was done by the DSN until 17 July 1990. From 1990
to 1993 determinations were made by analysts using data
from the Imaging Photo Polarimeter (IPP). After the 6
July 1993 maneuver, there was not enough power left to
support the IPP. But approximately every six months
analysts still could get a rough determination using in-
formation obtained from conscan maneuvers [18] on an
uplink signal. When using conscan, the high gain feed
is oﬀ-set. Thruster ﬁrings are used to spiral in to the
correct pointing of the spacecraft antenna to give the
maximum signal strength. To run this procedure (con-
scan and attitude) it is now necessary to turn oﬀ the
traveling-wave-tube (TWT) ampliﬁer. So far, the power
and tube life-cycle have worked and the Jet Propulsion
Laboratory’s (JPL) Deep Space Network (DSN) has been
able to reacquire the signal. It takes about 15 minutes
or so to do a maneuver. [The magnetometer boom in-
corporates a hinged, viscous, damping mechanism at its
attachment point, for passive nutation control.]
In the extended mission phase, after Jupiter and Sat-
urn encounters, the thrusters have been used for preces-
sion maneuvers only. Two pairs of thrusters at opposite
sides of the spacecraft have nozzles directed along the
spin axis, fore and aft (See Figure 2.) In precession mode,
the thrusters are ﬁred by opening one nozzle in each pair.
One ﬁres to the front and the other ﬁres to the rear of the
spacecraft [19], in brief thrust pulses. Each thrust pulse
precesses the spin axis a few tenths of a degree until the
desired attitude is reached.
The two nozzles of the third thruster pair, no longer
in use, are aligned tangentially to the antenna rim. One
points in the direction opposite to its (rotating) velocity
vector and the other with it. These were used for spin
control.
C. Thermal system and on-board power
Early on the spacecraft instrument compartment is
thermally controlled between ≈ 0 F and 90 F. This is
done with the aid of thermo-responsive louvers located at
the bottom of the equipment compartment. These lou-
vers are adjusted by bi-metallic springs. They are com-
pletely closed below ∼ 40 F and completely open above ∼
85 F. This allows controlled heat to escape in the equip-
ment compartment. Equipment is kept within an opera-
tional range of temperatures by multi-layered blankets of
insulating aluminum plastic. Heat is provided by electric
heaters, the heat from the instruments themselves, and
by twelve one-watt radioisotope heaters powered directly
by non-ﬁssionable plutonium ( 238
94 Pu→ 234
92 U+4
2He).
238Pu, with a half life time of 87.74 years, also provides
the thermal source for the thermoelectric devices in the
RTGs. Before launch, each spacecraft’s four RTGs deliv-
ered a total of approximately 160 W of electrical power
[20, 21]. Each of the four space-proven SNAP-19 RTGs
converts 5 to 6 percent of the heat released from pluto-
nium dioxide fuel to electric power. RTG power is great-
est at 4.2 Volts; an inverter boosts this to 28 Volts for
distribution. RTG life is degraded at low currents; there-
fore, voltage is regulated by shunt dissipation of excess
power.
The power subsystem controls and regulates the RTG
power output with shunts, supports the spacecraft load,
and performs battery load-sharing. The silver cadmium
battery consists of eight cells of 5 ampere-hours capacity
each. It supplies pulse loads in excess of RTG capability
and may be used for sharing peak loads. The battery
voltage is often discharged and charged. This can be
seen by telemetry of the battery discharge current and
charge current
At launch each RTG supplied about 40 W to the input
of the ∼ 4. 2 V Inverter Assemblies. (The output for other
uses includes the DC bus at 28 V and the AC bus at 61
V) Even though electrical power degrades with time (see
Section VIII D), at −41 F the essential platform temper-
ature as of the year 2000 is still between the acceptable
limits of −63 F to 180 F. The RF power output from the
traveling-wave-tube ampliﬁer is still operating normally .
The equipment compartment is insulated from extreme
heat inﬂux with aluminized mylar and kapton blankets.
Adequate warmth is provided by dissipation of 70 to 120
watts of electrical power by electronic units within the
compartment; louvers regulating the release of this heat
below the mounting platform maintain temperatures in
the vicinity of the spacecraft equipment and scientiﬁc in-
struments within operating limits. External component
temperatures are controlled, where necessary, by appro-
priate coating and, in some cases, by radioisotope or elec-
trical heaters.
The energy production from the radioactive decay
obeys an exponential law. Hence, 29 years after launch,
the radiation from Pioneer 10’s RTGs was about 80 per-
cent of its original intensity. However the electrical powe r

## Page 5

5
delivered to the equipment compartment has decayed at
a faster rate than the 238Pu decays radioactively. Specif-
ically, the electrical power ﬁrst decayed very quickly and
then slowed to a still fast linear decay [22]. By 1987 the
degradation rate was about −2. 6 W/yr for Pioneer 10
and even greater for the sister spacecraft.
This fast depletion rate of electrical power from the
RTGs is caused by normal deterioration of the thermo-
couple junctions in the thermoelectric devices.
The spacecraft needs 100 W to power all systems, in-
cluding 26 W for the science instruments. Previously,
when the available electrical power was greater than 100
W, the excess power was either thermally radiated into
space by a shunt-resistor radiator or it was used to charge
a battery in the equipment compartment.
At present only about 65 W of power is available to
Pioneer 10 [23]. Therefore, all the instruments are no
longer able to operate simultaneously. But the power
subsystem continues to provide suﬃcient power to sup-
port the current spacecraft load: transmitter, receiver,
command and data handling, and the Geiger Tube Tele-
scope (GTT) science instrument. As pointed out in Sec.
II E, the science package and transmitter are turned oﬀ
in extended cruise mode to provide enough power to ﬁre
the attitude control thrusters.
D. Communication system
The Pioneer 10/11 communication systems use S-band
(λ ≃ 13 cm) Doppler frequencies [24]. The communica-
tion uplink from Earth is at approximately 2.11 GHz.
The two spacecraft transmit continuously at a power of
eight watts. They beam their signals, of approximate fre-
quency 2.29 GHz, to Earth by means of the parabolic 2.74
m high-gain antenna. Phase coherency with the ground
transmitters, referenced to H-maser frequency standards,
is maintained by means of an S-band transponder with
the 240/221 frequency turnaround ratio (as indicated by
the values of the above mentioned frequencies).
The communications subsystem provides for: i) up-
link and down-link communications; ii) Doppler coher-
ence of the down-link carrier signal; and iii) generation
of the conscan [18] signal for closed loop precession of
the spacecraft spin axis towards Earth. S-band carrier
frequencies, compatible with DSN, are used in conjunc-
tion with a telemetry modulation of the down-link signal.
The high-gain antenna is used to maximize the teleme-
try data rate at extreme ranges. The coupled medium-
gain/omni-directional antenna with fore and aft elements
respectively, provided broad-angle communications at in-
termediate and short ranges. For DSN acquisition, these
three antennae radiate a non-coherent RF signal, and for
Doppler tracking, there is a phase coherent mode with a
frequency translation ratio of 240/221.
Two frequency-addressable phase-lock receivers are
connected to the two antenna systems through a ground-
commanded transfer switch and two diplexers, provid-
ing access to the spacecraft via either signal path. The
receivers and antennae are interchangeable through the
transfer switch by ground command or automatically, if
needed.
There is a redundancy in the communication systems,
with two receivers and two transmitters coupled to two
traveling-wave-tube ampliﬁers. Only one of the two re-
dundant systems has been used for the extended mis-
sions, however.
At launch, communication with the spacecraft was at
a data rate 256 bps for Pioneer 10 (1024 bps for Pioneer
11). Data rate degradation has been −1. 27 mbps/day for
Pioneer 10 ( −8. 78 mbps/day for Pioneer 11). The DSN
still continues to provide good data with the received sig-
nal strength of about −178 dBm (only a few dB from the
receiver threshold). The data signal to noise ratio is still
mainly under 0.5 dB. The data deletion rate is often be-
tween 0 and 50 percent, at times more. However, during
the test of 11 March 2000, the average deletion rate was
about 8 percent. So, quality data are still available.
E. Status of the extended mission
The Pioneer 10 mission oﬃcially ended on 31 March
1997 when it was at a distance of 67 AU from the Sun.
(See Figure 3.) At a now nearly constant velocity relative
to the Sun of ∼12.2 km/s, Pioneer 10 will continue its
motion into interstellar space, heading generally for the
red star Aldebaran, which forms the eye of Taurus (The
Bull) Constellation. Aldebaran is about 68 light years
away and it would be expected to take Pioneer 10 over 2
million years to reach its neighborhood.
FIG. 3: Ecliptic pole view of Pioneer 10, Pioneer 11, and
Voyager trajectories. Pioneer 11 is traveling approximate ly
in the direction of the Sun’s orbital motion about the galact ic
center. The galactic center is approximately in the directi on
of the top of the ﬁgure. [Digital artwork by T. Esposito.
NASA ARC Image # AC97-0036-3.]

## Page 6

6
A switch failure in the Pioneer 11 radio system on 1
October 1990 disabled the generation of coherent Doppler
signals. So, after that date, when the spacecraft was ∼ 30
AU away from the Sun, no useful data have been gen-
erated for our scientiﬁc investigation. Furthermore, by
September 1995, its power source was nearly exhausted.
Pioneer 11 could no longer make any scientiﬁc observa-
tions, and routine mission operations were terminated.
The last communication from Pioneer 11 was received
in November 1995, when the spacecraft was at distance
of ∼ 40 AU from the Sun. (The relative Earth motion
carried it out of view of the spacecraft antenna.) The
spacecraft is headed toward the constellation of Aquila
(The Eagle), northwest of the constellation of Sagittarius ,
with a velocity relative to the Sun of ∼11.6 km/s Pioneer
11 should pass close to the nearest star in the constella-
tion Aquila in about 4 million years [6]. (Pioneer 10 and
11 orbital parameters are given in the Appendix.)
However, after mission termination the Pioneer 10 ra-
dio system was still operating in the coherent mode when
commanded to do so from the Pioneer Mission Opera-
tions center at the NASA Ames Research Center (ARC).
As a result, after 31 March 1997, JPL’s DSN was still able
to deliver high-quality coherent data to us on a regular
schedule from distances beyond 67 AU.
Recently, support of the Pioneer spacecraft has been on
a non-interference basis to other NASA projects. It was
used for the purpose of training Lunar Prospector con-
trollers in DSN coordination of tracking activities. Un-
der this training program, ARC has been able to main-
tain contact with Pioneer 10. This has required careful
attention to the DSN’s ground system, including the in-
stallation of advanced instrumentation, such as low-noise
digital receivers. This extended the lifetime of Pioneer
10 to the present. [Note that the DSN’s early estimates,
based on instrumentation in place in 1976, predicted that
radio contact would be lost about 1980.]
At the present time it is mainly the drift of the space-
craft relative to the solar velocity that necessitates ma-
neuvers to continue keeping Pioneer 10 pointed towards
the Earth. The latest successful precession maneuver to
point the spacecraft to Earth was accomplished on 11
February 2000, when Pioneer 10 was at a distance from
the Sun of 75 AU. [The distance from the Earth was ∼ 76
AU with a corresponding round-trip light time of about
21 hour.] The signal level increased 0.5-0.75 dBm [25] as
a result of the maneuver.
This was the seventh successful maneuver that has
been done in the blind since 26 January 1997. At that
time it had been determined that the electrical power to
the spacecraft had degraded to the point where the space-
craft transmitter had to be turned oﬀ to have enough
power to perform the maneuver. After 90 minutes in
the blind the transmitter was turned back on again. So,
despite the continued weakening of Pioneer 10’s signal,
radio Doppler measurements were still available. The
next attempt at a maneuver, on 8 July 2000, turned out
in the end to be successful. Signal was tracked on 9 July
2001. Contact was reestablished on the 30th anniversary
of launch, 2 March 2002.
F. The Galileo and Ulysses missions and spacecraft
1. The Galileo mission
The Galileo mission to explore the Jovian system [26]
was launched 18 October 1989 aboard the Space Shuttle
Discovery. Due to insuﬃcient launch power to reach its
ﬁnal destination at 5.2 AU, a trajectory was chosen with
planetary ﬂybys to gain gravity assists. The spacecraft
ﬂew by Venus on 10 February 1990 and twice by the
Earth, on 8 December 1990 and on 8 December 1992. The
current Galileo Millennium Mission continues to study
Jupiter and its moons, and coordinated observations with
the Cassini ﬂyby in December 2000.
The dynamical properties of the Galileo spacecraft are
very well known. At launch the orbiter had a mass of
2,223 kg. This included 925 kg of usable propellant,
meaning over 40% of the orbiter’s mass at launch was
for propellant! The science payload was 118 kg and the
probe’s total mass was 339 kg. Of this latter, the probe
descent module was 121 kg, including a 30 kg science
payload. The tensor of inertia of the spacecraft had the
following components at launch: Jxx = 4454 . 7, J yy =
4061. 2, J zz = 5967 . 6, J xy = −52. 9, J xz = 3 . 21, J yz =
−15. 94 in units of kg m 2. Based on the area of the
sun-shade plus the booms and the RTGs we obtained
a maximal cross-sectional area of 19.5 m 2. Each of the
two of the Galileo’s RTGs at launch delivered of 285 W
of electric power to the subsystems.
Unlike previous planetary spacecraft, Galileo featured
an innovative “dual spin” design: part of the orbiter
would rotate constantly at about three rpm and part of
the spacecraft would remain ﬁxed in (solar system) in-
ertial space. This means that the orbiter could easily
accommodate magnetospheric experiments (which need
to made while the spacecraft is sweeping) while also pro-
viding stability and a ﬁxed orientation for cameras and
other sensors. The spin rate could be increased to 10 rev-
olutions per minute for additional stability during major
propulsive maneuvers.
Apparently there was a mechanical problem between
the spinning and non-spinning sections. Because of this,
the project decided to often use an all-spinning mode,
of about 3.15 rpm. This was especially true close to the
Jupiter Orbit Insertion (JOI), when the entire spacecraft
was spinning (with a slower rate, of course).
Galileo’s original design called for a deployable high-
gain antenna (HGA) to unfurl. It would provide approx-
imately 34 dB of gain at X-band (10 GHz) for a 134 kbps
downlink of science and priority engineering data. How-
ever, the X-band HGA failed to unfurl on 11 April 1991.
When it again did not deploy following the Earth ﬂy-
by in 1992, the spacecraft was reconﬁgured to utilize the
S-band, 8 dB, omni-directional low-gain antenna (LGA)

## Page 7

7
for downlink.
The S-band frequencies are 2.113 GHz - up and
2.295 GHz - down, a conversion factor of 240/221 at
the Doppler frequency transponder. This conﬁguration
yielded much lower data rates than originally scheduled,
8-16 bps through JOI [27]. Enhancements at the DSN
and reprogramming the ﬂight computers on Galileo in-
creased telemetry bit rate to 8-160 bps, starting in the
spring of 1996.
Currently, two types of Galileo navigation data are
available, namely Doppler and range measurements. As
mentioned before, an instantaneous comparison between
the ranging signal that goes up with the ranging signal
that comes down would yield an “instantaneous” two-
way range delay. Unfortunately, an instantaneous com-
parison was not possible in this case. The reason is that
the signal-to-noise ratio on the incoming ranging signal
is small and a long integration time (typically minutes)
must be used (for correlation purposes). During such
long integration times, the range to the spacecraft is con-
stantly changing. It is therefore necessary to “electron-
ically freeze” the range delay long enough to permit an
integration to be performed. The result represents the
range at the moment of freezing [28, 29].
2. The Ulysses mission
Ulysses was launched on 6 October 1990, also from
the Space Shuttle Discovery, as a cooperative project of
NASA and the European Space Agency (ESA). JPL man-
ages the US portion of the mission for NASA’s Oﬃce of
Space Science. Ulysses’ objective was to characterize the
heliosphere as a function of solar latitude [30]. To reach
high solar latitudes, its voyage took it to Jupiter on 8
February 1992. As a result, its orbit plane was rotated
about 80 degrees out of the ecliptic plane.
Ulysses explored the heliosphere over the Sun’s south
pole between June and November, 1994, reaching maxi-
mum Southern latitude of 80.2 degrees on 13 September
1994. It continued in its orbit out of the plane of the
ecliptic, passing perihelion in March 1995 and over the
north solar pole between June and September 1995. It
returned again to the Sun’s south polar region in late
2000.
The total mass at launch was the sum of two parts: a
dry mass of 333.5 kg plus a propellant mass of 33.5 kg.
The tensor of inertia is given by its principal components
Jxx = 371 . 62, J yy = 205 . 51, J zz = 534 . 98 in units kg m 2.
The maximal cross section is estimated to be 10.056 m 2.
This estimation is based on the radius of the antenna 1.65
m (8.556 m 2) plus the areas of the RTGs and part of the
science compartment (yielding an additional ≈ 1.5 m 2).
The spacecraft was spin-stabilized at 4.996 rpm. The
electrical power is generated by modern RTGs, which
are located much closer to the main bus than are those
of the Pioneers. The power generated at launch was 285
W.
Communications with the spacecraft are performed at
X-band (for downlink at 20 W with a conversion factor
of 880/221) and S-band (both for uplink 2111.607 MHz
and downlink 2293.148 MHz, at 5 W with a conversion
factor of 240/221). Currently both Doppler and range
data are available for both frequency bands. While the
main communication link is S-up/X-down, the S-down
link was used only for radio-science purposes.
Because of Ulysses’ closeness to the Sun and also be-
cause of its construction, any hope to model Ulysses for
small forces might appear to be doomed by solar radia-
tion pressure and internal heat radiation from the RTGs.
However, because the Doppler signal direction is towards
the Earth while the radiation pressure varies with dis-
tance and has a direction parallel the Sun-Ulysses line,
in principle these eﬀects could be separated. And again,
there was range data. This all would make it easier to
model non-gravitational acceleration components normal
to the line of sight, which usually are poorly and not sig-
niﬁcantly determined.
The Ulysses spacecraft spins at ∼ 5 rpm around its
antenna axis (4.996 rpm initially). The angle of the spin
axis with respect to the spacecraft-Sun line varies from
near zero at Jupiter to near 50 degrees at perihelion.
Any on-board forces that could perturb the spacecraft
trajectory are restricted to a direction along the spin axis .
[The other two components are canceled out by the spin.]
As the spacecraft and the Earth travel around the Sun,
the direction from the spacecraft to the Earth changes
continuously. Regular changes of the attitude of the
spacecraft are performed throughout the mission to keep
the Earth within the narrow beam of about one degree
full width of the spacecraft–ﬁxed parabolic antenna.
III. DATA ACQUISITION AND PREP ARATION
Discussions of radio-science experiments with space-
craft in the solar system requires at least a general knowl-
edge of the sophisticated experimental techniques used at
the DSN complex. Since its beginning in 1958 the DSN
complex has undergone a number of major upgrades and
additions. This was necessitated by the needs of particu-
lar space missions. [The last such upgrade was conducted
for the Cassini mission when the DSN capabilities were
extended to cover the Ka radio frequency bandwidth.
For more information on DSN methods, techniques, and
present capabilities, see [31].] For the purposes of the
present analysis one will need a general knowledge of the
methods and techniques implemented in the radio-science
subsystem of the DSN complex.
This section reviews the techniques that are used to
obtain the radio tracking data from which, after analysis,
results are generated. Here we will brieﬂy discuss the
DSN hardware that plays a pivotal role for our study of
the anomalous acceleration.

## Page 8

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

## Page 9

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

## Page 10

10
stability of the hydrogen maser and the resolution of the
“resolver.”
Consequently, the JPL Doppler records are not fre-
quency measurements. Rather, they are digitally counted
measurements of the Doppler phase diﬀerence between
the transmitted and received S-band frequencies, divided
by the count time.
Therefore, the Doppler observables, we will refer to,
have units of cycles per second or Hz. Since total count
phase observables are Doppler observables multiplied by
the count interval T c, they have units of cycles. The
Doppler integration time refers to the total counting of
the elapsed periods of the wave with the reference fre-
quency of the hydrogen maser. The usual Doppler in-
tegrating times for the Pioneer Doppler signals refers to
the data sampled over intervals of 10 s, 60 s, 600 s, or
1980 s.
2. Range measurements
A range measurement is made by phase modulating a
signal onto the up-link carrier and having it echoed by the
transponder. The transponder demodulates this ranging
signal, ﬁlters it, and then re-modulates it back onto the
down-link carrier. At the ground station, this returned
ranging signal is demodulated and ﬁltered. An instanta-
neous comparison between the outbound ranging signal
and the returning ranging signal that comes down would
yield the two-way delay. Cross correlating the returned
phase modulated signal with a ground duplicate yields
the time delay. (See [28] and references therein.) As the
range code is repeated over and over, an ambiguity can
exist. The orbit determination programs are then used
to infer (some times with great diﬃculty) the number of
range codes that exist between a particular transmitted
code and its own corresponding received code.
Thus, the ranging data are independent of the Doppler
data, which represents a frequency shift of the radio car-
rier wave without modulation. For example, solar plasma
introduces a group delay in the ranging data but a phase
advance in the Doppler data.
Ranging data can also be used to distinguish an ac-
tual range change from a ﬁctitious range change seen in
Doppler data that is caused by a frequency error [39].
The Doppler frequency integrated over time (the accu-
mulated phase) should equal the range change except for
the diﬀerence introduced by charged particles
3. Inferring position information from Doppler
It is also possible to infer the position in the sky of
a spacecraft from the Doppler data. This is accom-
plished by examining the diurnal variation imparted to
the Doppler shift by the Earth’s rotation. As the ground
station rotates underneath a spacecraft, the Doppler shift
is modulated by a sinusoid. The sinusoid’s amplitude de-
pends on the declination angle of the spacecraft and its
phase depends upon the right ascension. These angles
can therefore be estimated from a record of the Doppler
shift that is (at least) of several days duration. This al-
lows for a determination of the distance to the spacecraft
through the dynamics of spacecraft motion using stan-
dard orbit theory contained in the orbit determination
programs.
C. Data preparation
In an ideal system, all scheduled observations would
be used in determining parameters of physical interest.
However, there are inevitable problems that occur in data
collection and processing that corrupt the data. So, at
various stages of the signal processing one must remove
or “edit” corrupted data. Thus, the need arises for ob-
jective editing criteria. Procedures have been developed
which attempt to excise corrupted data on the basis of
objective criteria. There is always a temptation to elim-
inate data that is not well explained by existing models,
to thereby “improve” the agreement between theory and
experiment. Such an approach may, of course, eliminate
the very data that would indicate deﬁciencies in the a pri-
ori model. This would preclude the discovery of improved
models.
In the processing stage that ﬁts the Doppler samples,
checks are made to ensure that there are no integer cycle
slips in the data stream that would corrupt the phase.
This is done by considering the diﬀerence of the phase
observations taken at a high rate (10 times a second)
to produce Doppler. Cycle slips often are dependent on
tracking loop bandwidths, the signal to noise ratios, and
predictions of frequencies. Blunders due to out-of-lock
can be determined by looking at the original tracking
data. In particular, cycle slips due to loss-of-lock stand
out as a 1 Hz blunder point for each cycle slipped.
If a blunder point is observed, the count is stopped and
a Doppler point is generated by summing the preceding
points. Otherwise the count is continued until a spec-
iﬁed maximum duration is reached. Cases where this
procedure detected the need for cycle corrections were
ﬂagged in the database and often individually examined
by an analyst. Sometimes the data was corrected, but
nominally the blunder point was just eliminated. This
ensures that the data is consistent over a pass. However,
it does not guarantee that the pass is good, because other
errors can aﬀect the whole pass and remain undetected
until the orbit determination is done.
To produce an input data ﬁle for an orbit determina-
tion program, JPL has a software package known as the
Radio Metric Data Selection, Translation, Revision, In-
tercalation, Processing and Performance Evaluation Re-
porting (RMD-STRIPPER) Program. As we discussed
in Section III B 1, this input ﬁle has data that can be in-
tegrated over intervals with diﬀerent durations: 10 s, 60

## Page 11

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

## Page 12

12
After a maneuver in mid-1993, there was not enough
power left to support the IPP. But analysts still could get
a rough determination approximately every six months
using information obtained from the conscan maneuvers.
No spin determinations were made after 1995. However,
the archived conscan data could still yield spin data at
every maneuver time if such work was approved. Further,
as the phase center of the main antenna is slightly oﬀset
from the spin axis, a very small (but detectable) sine-
wave signal appears in the high-rate Doppler data. In
principle, this could be used to determine the spin rate for
passes taken after 1993, but it has not been attempted.
Also, the failure of one of the spin-down thrusters pre-
vented precise spin calibration of the Pioneer 11 data.
Because the spin rate of the Pioneers was changing over
the data span, the calibrations also provide an indication
of gas leaks that aﬀect the acceleration of the spacecraft.
A careful look at the records shows how this can be a
problem. This will be discussed in Sections VI A and
VIII F.
IV. BASIC THEOR Y OF SP ACECRAFT
NA VIGATION
Accuracy of modern radio tracking techniques has pro-
vided the means necessary to explore the gravitational
environment in the solar system up to a limit never be-
fore possible [45]. The major role in this quest belongs to
relativistic celestial mechanics experiments with planet s
(e.g., passive radar ranging) and interplanetary space-
craft (both Doppler and range experiments). Celestial
mechanics experiments with spacecraft have been carried
out by JPL since the early 1960’s [46, 47]. The motiva-
tion was to improve both the ephemerides of solar system
bodies and also the knowledge of the solar system’s dy-
namical environment. This has become possible due to
major improvements in the accuracy of spacecraft navi-
gation, which is still a critical element for a number of
space missions. The main objective of spacecraft navi-
gation is to determine the present position and velocity
of a spacecraft and to predict its future trajectory. This
is usually done by measuring changes in the spacecraft’s
position and then, using those measurements, correcting
(ﬁtting and adjusting) the predicted spacecraft trajec-
tory.
In this section we will discuss the theoretical founda-
tion that is used for the analysis of tracking data from
interplanetary spacecraft. We describe the basic physical
models used to determine a trajectory, given the data.
A. Relativistic equations of motion
The spacecraft ephemeris, generated by a numerical
integration program, is a ﬁle of spacecraft positions and
velocities as functions of ephemeris (or coordinate) time
(ET). The integrator requires the input of various param-
eters. These include adopted constants ( c, G, planetary
mass ratios, etc.) and parameters that are estimated
from ﬁts to observational data (e.g., corrections to plan-
etary orbital elements).
The ephemeris programs use equations for point-mass
relativistic gravitational accelerations. They are deriv ed
from the variation of a time-dependent, Lagrangian-
action integral that is referenced to a non-rotating, solar -
system, barycentric, coordinate frame. In addition to
modeling point-mass interactions, the ephemeris pro-
grams contain equations of motion that model terrestrial
and lunar ﬁgure eﬀects, Earth tides, and lunar phys-
ical librations [48]-[50]. The programs treat the Sun,
the Moon, and the nine planets as point masses in the
isotropic, parameterized post-Newtonian, N-body metric
with Newtonian gravitational perturbations from large,
main-belt asteroids.
Responding to the increasing demand of the naviga-
tional accuracy, the gravitational ﬁeld in the solar sys-
tem is modeled to include a number of relativistic ef-
fects that are predicted by the diﬀerent metric theories
of gravity. Thus, within the accuracy of modern exper-
imental techniques, the parameterized post-Newtonian
(PPN) approximation of modern theories of gravity pro-
vides a useful starting point not only for testing these
predictions, but also for describing the motion of self-
gravitating bodies and test particles. As discussed in
detail in [51], the accuracy of the PPN limit (which is
slow motion and weak ﬁeld) is adequate for all foresee-
able solar system tests of general relativity and a number
of other metric theories of gravity. (For the most general
formulation of the PPN formalism, see the works of Will
and Nordtvedt [51, 52].)
For each body i (a planet or spacecraft anywhere in
the solar system), the point-mass acceleration is written
as [41, 42, 48, 53, 54]
¨ri =
∑
j̸=i
µ j(rj − ri)
r3
ij
(
1 − 2(β + γ )
c2
∑
k̸=i
µ k
rik
− 2β − 1
c2
∑
k̸=j
µ k
rjk
− 3
2c2
[ (rj − ri)˙rj
rij
]2
+ 1
2c2 (rj − ri)¨rj − 2(1 + γ )
c2 ˙ri ˙rj +
+ γ
(vi
c
)2
+ (1 + γ )
(vj
c
)2
)
+ 1
c2
∑
j̸=i
µ j
r3
ij
(
[ri − rj )] ·[(2 + 2γ )˙ri − (1 + 2γ )˙rj]
)
(˙ri − ˙rj) + 3 + 4γ
2c2
∑
j̸=i
µ j¨rj
rij
(3)

## Page 13

13
where µ i is the “gravitational constant” of body i. It
actually is its mass times the Newtonian constant: µ i =
Gmi. Also, ri(t) is the barycentric position of body i,
rij = |rj − ri|and vi = |˙ri|. For planetary motion, each of
these equations depends on the others. So they must be
iterated in each step of the integration of the equations
of motion.
The barycentric acceleration of each body j due to
Newtonian eﬀects of the remaining bodies and the aster-
oids is denoted by ¨rj. In Eq. (3), β and γ are the PPN
parameters [51, 52]. General relativity corresponds to
β = γ = 1, which we choose for our study. The Brans-
Dicke theory is the most famous among the alternative
theories of gravity. It contains, besides the metric tensor ,
a scalar ﬁeld ϕ and an arbitrary coupling constant ω , re-
lated to the two PPN parameters as γ = 1+ω
2+ω , β = 1.
Equation (3) allows the consideration of any problem in
celestial mechanics within the PPN framework.
B. Light time solution and time scales
In addition to planetary equations of motion Eq. (3),
one needs to solve the relativistic light propagation equa-
tion in order to get the solution for the total light time
travel. In the solar system, barycentric, space-time frame
of reference this equation is given by:
t2 − t1 = r21
c + (1 + γ )µ ⊙
c3 ln
[ r⊙
1 + r⊙
2 + r⊙
12
r⊙
1 + r⊙
2 − r⊙
12
]
+
+
∑
i
(1 + γ )µ i
c3 ln
[ ri
1 + ri
2 + ri
12
ri
1 + ri
2 − ri
12
]
, (4)
where µ ⊙ is the gravitational constant of the Sun and µ i
is the gravitational constant of a planet, an outer plan-
etary system, or the Moon. r⊙
1 , r ⊙
2 andr⊙
12 are the he-
liocentric distances to the point of RF signal emission
on Earth, to the point of signal reﬂection at the space-
craft, and the relative distance between these two points.
Correspondingly, ri
1, r i
2, and ri
12 are similar distances rel-
ative to a particular i-th body in the solar system. In
the spacecraft light time solution, t1 refers to the trans-
mission time at a tracking station on Earth, and t2 refers
to the reﬂection time at the spacecraft or, for one-way
[36] data, the transmission time at the spacecraft. The
reception time at the tracking station on Earth or at an
Earth satellite is denoted by t3. Hence, Eq. (4) is the
up-leg light time equation. The corresponding down-leg
light time equation is obtained by replacing subscripts as
follows: 1 → 2 and 2 → 3. (See the details in [42].)
The spacecraft equations of motion relative to the so-
lar system barycenter are essentially the same as given by
Eq. (3). The gravitational constants of the Sun, planets
and the planetary systems are the values associated with
the solar system barycentric frame of reference, which are
obtained from the planetary ephemeris [54]. We treat a
distant spacecraft as a point-mass particle. The space-
craft acceleration is integrated numerically to produce
the spacecraft ephemeris. The ephemeris is interpolated
at the ephemeris time ( ET) value of the interpolation
epoch. This is the time coordinate t in Eqs. (3) and
(4), i.e., t ≡ ET. As such, ephemeris time means coor-
dinate time in the chosen celestial reference frame. It is
an independent variable for the motion of celestial bod-
ies, spacecraft, and light rays. The scale of ET depends
upon which reference frame is selected and one may use a
number of time scales depending on the practical applica-
tions. It is convenient to express ET in terms of Interna-
tional Atomic Time ( TAI). TAI is based upon the second
in the International System of Units ( SI). This second
is deﬁned to be the duration of 9,192,631,770 periods
of the radiation corresponding to the transition between
two hyperﬁne levels of the ground state of the cesium-133
atom [55].
The diﬀerential equation relating ephemeris time ( ET)
in the solar system barycentric reference frame to TAI at
a tracking station on Earth or on Earth satellite can be
obtained directly from the Newtonian approximation to
the N-body metric [54]. This expression has the form
d TAI
d ET = 1 − 1
c2
(
U − ⟨U ⟩ + 1
2 v2 − 1
2 ⟨v2⟩
)
+ O( 1
c4 ), (5)
where U is the solar system gravitational potential eval-
uated at the tracking station and v is the solar system
barycentric velocity of the tracking station. The brack-
ets ⟨ ⟩ on the right side of Eq. (5) denote long-time
average of the quantity contained within them. This av-
eraging amounts to integrating out periodic variations in
the gravitational potential, U , and the barycentric veloc-
ity, v2, at the location of a tracking station. The desired
time scale transformation is then obtained by using the
planetary ephemeris to calculate the terms in Eq. (5).
The vector expression for the ephemeris/coordinate
time ( ET) in the solar system barycentric frame of ref-
erence minus the TAI obtained from an atomic clock at
a tracking station on Earth has the form [54]
ET − TAI = 32 . 184 s + 2
c2 (˙r⊙
B ·r⊙
B ) + 1
c2 (˙rSSB
B ·rB
E) +
+ 1
c2 (˙rSSB
E ·rE
A) + µ J
c2(µ ⊙ + µ J ) (˙r⊙
J ·r⊙
J ) +
+ µ Sa
c2(µ ⊙ + µ Sa) (˙r⊙
Sa ·r⊙
Sa) + 1
c2 (˙rSSB
⊙ ·r⊙
B ), (6)
where rj
i and ˙rj
i position and velocity vectors of point
i relative to point j (they are functions of ET); super-
script or subscript SSB denotes solar system barycenter;
⊙ stands for the Sun; B for the Earth-Moon barycen-
ter; E, J, Sa denote the Earth, Jupiter, and Saturn corre-
spondingly, and A is for the location of the atomic clock
on Earth which reads TAI. This approximated analytic
result contains the clock synchronization term which de-
pends upon the location of the atomic clock and ﬁve
location-independent periodic terms. There are several
alternate expressions that have up to several hundred
additional periodic terms which provide greater accura-
cies than Eq. (6). The use of these extended expressions

## Page 14

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

## Page 15

15
the expected error in the acceleration error estimations.
This is on the order of
σ 0 ∼ 2 × 10− 8 cm/ s2, (7)
where σ 0 is a single determination accuracy related to ac-
celeration measurements averaged over number of days.
This would contribute to our result as σ N ∼ σ 0/
√
N .
Thus, if no systematics are involved then σ N will just
tend to zero as time progresses.
Therefore, the important thing is to know that these ef-
fects (systematics) are not too large, thereby overwhelm-
ing any possibly important signal (such as our anomalous
acceleration). This will be demonstrated in Sections VII
and VIII.
D. Solar corona model and weighting
The electron density and density gradient in the so-
lar atmosphere inﬂuence the propagation of radio waves
through the medium. So, both range and Doppler obser-
vations at S-band are aﬀected by the electron density in
the interplanetary medium and outer solar corona. Since,
throughout the experiment, the closest approach to the
center of the Sun of a radio ray path was greater than 3.5
R⊙ , the medium may be regarded as collisionless. The
one way time delay associated with a plane wave passing
through the solar corona is obtained [44, 46, 59] by inte-
grating the group velocity of propagation along the ray’s
path, ℓ:
∆t = ± 1
2c ncrit(ν )
∫ SC
⊕
dℓ n e(t, r),
ncrit(ν ) = 1 . 240 × 104
( ν
1 MHz
)2
cm− 3, (8)
where ne(t, r) is the free electron density in the solar
plasma, c is the speed of light, and ncrit(ν ) is the critical
plasma density for the radio carrier frequency ν . The
plus sign is applied for ranging data and the minus sign
for Doppler data [60].
Therefore, in order to calibrate the plasma contribu-
tion, one should know the electron density along the
path. One usually decomposes the electron density, ne,
into a static, steady-state part,
ne(r), plus a ﬂuctuation
δn e(t, r), i.e., ne(t, r) = ne(r) + δn e(t, r). The physical
properties of the second term are hard to quantify. But
luckily, its eﬀect on Doppler observables and, therefore,
on our results is small. (We will address this issue in Sec.
VII B.) On the contrary, the steady-state corona behav-
ior is reasonably well known and several plasma models
can be found in the literature [59]-[62].
Consequently, while studying the eﬀect of a system-
atic error from propagation of the S-band carrier wave
through the solar plasma, both analyses adopted the fol-
lowing model for the electron density proﬁle [44]:
ne(t, r) = A
(R⊙
r
)2
+ B
(R⊙
r
)2.7
e−
[
φ
φ0
] 2
+ C
(R⊙
r
)6
. (9)
r is the heliocentric distance to the immediate ray tra-
jectory and φ is the helio-latitude normalized by the ref-
erence latitude of φ 0 = 10 ◦. The parameters r and φ
are determined from the trajectory coordinates on the
tracking link being modeled. The parameters A, B, C
are parameters chosen to describe the solar electron den-
sity. (They are commonly given in two sets of units,
meters or cm − 3 [63].) They can be treated as stochas-
tic parameters, to be determined from the ﬁt. But in
both analyses we ultimately chose to use the values de-
termined from the recent solar corona studies done for
the Cassini mission. These newly obtained values are:
A = 6. 0 × 103, B = 2. 0 × 104, C = 0. 6 × 106, all in meters
[64]. [This is what we will refer to as the “Cassini corona
model.”]
Substitution of Eq. (9) into Eq. (8) results in the
following steady-state solar corona contribution to the
range model that we used in our analysis:
∆SCrange = ±
(ν 0
ν
)2[
A
(R⊙
ρ
)
F +
+ B
(R⊙
ρ
)1.7
e
−
[
φ
φ0
] 2
+ C
(R⊙
ρ
)5]
. (10)
ν 0 and ν are a reference frequency and the actual fre-
quency of radio-wave [for Pioneer 10 analysis ν 0 = 2295
MHz], ρ is the impact parameter with respect to the Sun
and F is a light-time correction factor. For distant space-
craft this function is given as follows:
F = F (ρ, r T , r E) = (11)
= 1
π
{
ArcTan
[ √
r2
T − ρ 2
ρ
]
+ ArcTan
[ √
r2
E − ρ 2
ρ
]}
,
where rT and rE are the heliocentric radial distances to
the target and to the Earth, respectively. Note that the
sign of the solar corona range correction is negative for
Doppler and positive for range. The Doppler correction
is obtained from Eq. (10) by simple time diﬀerentiation.
Both analyses use the same physical model, Eq. (10),
for the steady-state solar corona eﬀect on the radio-wave
propagation through the solar plasma. Although the ac-
tual implementation of the model in the two codes is dif-
ferent, this turns out not to be signiﬁcant. (See Section
IX B.)
CHASMP can also consider the eﬀect of temporal vari-
ation in the solar corona by using the recorded history
of solar activity. The change in solar activity is linked to
the variation of the total number of sun spots per year
as observed at a particular wavelength of the solar radia-
tion, λ =10.7 cm. The actual data corresponding to this
variation is given in Ref. [65]. CHASMP averages this
data over 81 days and normalizes the value of the ﬂux by
150. Then it is used as a time-varying scaling factor in
Eq. (10). The result is referred to as the “F10.7 model.”
Next we come to corona data weighting. JPL’s ODP
does not apply corona weighting. On the other hand,
Aerospace’s CHASMP can apply corona weighting if de-
sired. Aerospace uses a standard weight augmented by

## Page 16

16
a weight function that accounts for noise introduced by
solar plasma and low elevation. The weight values are ad-
justed so that i) the post-ﬁt weighted sum of the squares
is close to unity and ii) approximately uniform noise in
the residuals is observed throughout the ﬁt span.
Thus, the corresponding solar-corona weight function
is:
σ r = k
2
(ν 0
ν
)2(R⊙
ρ
)3
2
, (12)
where, for range data, k is an input constant nominally
equal to 0.005 light seconds, ν 0 and ν are a reference
frequency and the actual frequency, ρ is the trajectory’s
impact parameter with respect to the Sun in km, and R⊙
is the solar radius in km [66]. The solar-corona weight
function for Doppler is essentially the same, but obtained
by numerical time diﬀerentiation of Eq. (12).
E. Modeling of maneuvers
There were 28 Pioneer 10 maneuvers during our data
interval from 3 January 1987 to 22 July 1998. Imperfect
coupling of the hydrazine thrusters used for the spin ori-
entation maneuvers produced integrated velocity changes
of a few millimeters per second. The times and durations
of each maneuver were provided by NASA/Ames. JPL
used this data as input to ODP. The Aerospace team
used a slightly diﬀerent approach. In addition to the orig-
inal data, CHASMP used the spin-rate data ﬁle to help
determine the times and duration of maneuvers. The
CHASMP determination mainly agreed with the data
used by JPL. [There were minor variations in some of
the times, one maneuver was split in two, and one extra-
neous maneuver was added to Interval II to account for
data not analyzed (see below).]
Because the eﬀect on the spacecraft acceleration could
not be determined well enough from the engineering
telemetry, JPL included a single unknown parameter in
the ﬁtting model for each maneuver. In JPL’s ODP anal-
ysis, the maneuvers were modeled by instantaneous ve-
locity increments at the beginning time of each maneu-
ver (instantaneous burn model). [Analyses of individual
maneuver ﬁts show the residuals to be small.] In the
CHASMP analysis, a constant acceleration acting over
the duration of the maneuver was included as a param-
eter in the ﬁtting model (ﬁnite burn model). Analyses
of individual maneuver ﬁts show the residuals are small.
Because of the Pioneer spin, these accelerations are im-
portant only along the Earth-spacecraft line, with the
other two components averaging out over about 50 revo-
lutions of the spacecraft over a typical maneuver duration
of 10 minutes.
By the time Pioneer 11 reached Saturn, the pattern
of the thruster ﬁrings was understood. Each maneuver
caused a change in spacecraft spin and a velocity incre-
ment in the spacecraft trajectory, immediately followed
by two to three days of gas leakage, large enough to be
observable in the Doppler data [67].
Typically the Doppler data is time averaged over 10
to 33 minutes, which signiﬁcantly reduces the high-
frequency Doppler noise. The residuals represent our ﬁt.
They are converted from units of Hz to Doppler velocity
by the formula [38]
[∆v]DSN = c
2
[∆ν ]DSN
ν 0
, (13)
where ν 0 is the downlink carrier frequency, ∼ 2. 29 GHz,
∆ν is the Doppler residual in Hz from the ﬁt, and c is
the speed of light.
As an illustration, consider the ﬁt to one of the Pio-
neer 10 maneuvers, # 17, on 22 December 1993, given in
Figure 5. This was particularly well covered by low-noise
FIG. 5: The Doppler residuals after a ﬁt for maneuver # 17
on 23 December 1993.
Doppler data near solar opposition. Before the start of
the maneuver, there is a systematic trend in the residu-
als which is represented by a cubic polynomial in time.
The standard error in the residuals is 0.095 mm/s. After
the maneuver, there is a relatively small velocity discon-
tinuity of −0. 90 ± 0. 07 mm/s. The discontinuity arises
because the model ﬁts the entire data interval. In fact,
the residuals increase after the maneuver. By 11 January
1994, 19 days after the maneuver, the residuals are scat-
tered about their pre-maneuver mean of −0. 15 mm/s.
For purposes of characterizing the gas leak immedi-
ately after the maneuver, we ﬁt the post-maneuver resid-
uals by a two-parameter exponential curve,
∆v = −v0 exp
[
− t
τ
]
− 0. 15 mm / s. (14)
The best ﬁt yields v0 = 0 . 808 mm/s and the time con-
stant τ is 13.3 days, a reasonable result. The time deriva-
tive of the exponential curve yields a residual acceleratio n
immediately after the maneuver of 7.03 × 10− 8 cm/s2.
This is close to the magnitude of the anomalous acceler-
ation inferred from the Doppler data, but in the opposite

## Page 17

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

## Page 18

18
searches for an aP that is generated by a random pro-
cess. One therefore expects that an aP estimated from
one batch is statistically independent (uncorrelated) fro m
those estimated from other batches. Also, the use of ﬁ-
nite correlation times indicates one is considering an aP
that may show a temporal variation within the data in-
terval. We experimented with a number of possible cor-
relation times and will discuss the corresponding assump-
tions when needed.
In each batch one estimates solutions for the set of de-
sired parameters at a speciﬁed epoch within the batch.
One usually chooses to report solutions corresponding to
the beginning, middle, or end of the batch. General co-
ordinate and time transformations (discussed in Section
IV B) are then used to report the solution in the epoch
chosen for the entire data interval. One may also adjust
the solutions among adjacent batches by accounting for
possible correlations. This process produces a smoothed
solution for the set of solved-for parameters. More de-
tails on this so called “batch–sequential algorithm with
smoothing ﬁlter” are available in Refs. [41]-[43].
Even without process noise, the inversion algorithms of
the Kalman formulation and the weighted least-squares
method seem radically diﬀerent. But as shown in [71],
if one uses a single batch for all the data and if one
uses certain assumptions about, for instance, the pro-
cess noise and the smoothing algorithms, then the two
methods are mathematically identical. When introduc-
ing process noise, an additional process noise matrix is
also added into the solution algorithm. The elements
of this matrix are chosen by the user as prescribed by
standard statistical techniques used for navigational dat a
processing.
For the recent results reported in Section VI, JPL used
both the batch-sequential and the weighted least-squares
estimation approaches. JPL originally implemented only
the batch-sequential method, which yielded the detec-
tion (at a level smaller than could be detected with any
other spacecraft) of an annual oscillatory term smaller in
size than the anomalous acceleration [13]. (This term is
discussed in Section IX C.) The recent studies included
weighted least-squares estimation to see if this annual
term was a calculational anomaly.
The Aerospace Corporation uses only the weighted
least-squares approach with its CHASMP software. A χ 2
test is used as an indicator of the quality of the ﬁt. In this
case, the anomalous acceleration is treated as a constant
parameter over the entire data interval. To solve for aP
one estimates the statistical weights for the data points
and then uses these in a general weighted least-squares
fashion. Note that the weighted least-squares method can
obtain a result similar to that from a batch-sequential ap-
proach (with smoothing ﬁlter, zero correlation time and
without process noise) by cutting the data interval into
smaller pieces and then looking at the temporal variation
among the individual solutions.
As one will see in the following, in the end, both pro-
grams yielded very similar results. The diﬀerences be-
tween them can be mainly attributed to (other) system-
atics. This gives us conﬁdence that both programs and
their implemented estimation algorithms are correct to
the accuracy of this investigation.
V. ORIGINAL DETECTION OF THE
ANOMALOUS ACCELERATION
A. Early JPL studies of the anomalous Pioneer
Doppler residuals
As mentioned in the introduction, by 1980 Pioneer 10
was at 20 AU, so the solar radiation pressure accelera-
tion had decreased to < 5 × 10− 8 cm/s2. Therefore, a
search for unmodeled accelerations (at ﬁrst with the fur-
ther out Pioneer 10) could begin at this level. With the
acceptance of a proposal of two of us (JDA and ELL)
to participate in the Heliospheric Mission on Pioneer 10
and 11, such a search began in earnest [72].
The JPL analysis of unmodeled accelerations used the
JPL’s Orbit Determination Program (ODP) [41]-[42].
Over the years the data continually indicated that the
largest systematic error in the acceleration residuals is a
constant bias of aP ∼ (8 ± 3) × 10− 8 cm/s2, directed to-
ward the Sun (to within the beam-width of the Pioneers’
antennae [73]).
As stated previously, the analyses were modeled to
include the eﬀects of planetary perturbations, radiation
pressure, the interplanetary media, general relativity, t o-
gether with bias and drift in the Doppler signal. Plane-
tary coordinates and the solar system masses were taken
from JPL’s Export Planetary Ephemeris DE405, refer-
enced to ICRF. The analyses used the standard space-
ﬁxed J2000 coordinate system with its associated JPL
planetary ephemeris DE405 (or earlier, DE200). The
time-varying Earth orientation in J2000 coordinates is
deﬁned by a 1998 version of JPL’s EOP ﬁle, which ac-
counts for the inertial precession and nutation of the
Earth’s spin axis, the geophysical motion of the Earth’s
pole with respect to its spin axis, and the Earth’s time
varying spin rate. The three-dimensional locations of
the tracking stations in the Earth’s body-ﬁxed coordi-
nate system (geocentric radius, latitude, longitude) were
taken from a set recommended by ICRF for JPL’s DE405.
Consider ν obs, the frequency of the re-transmitted sig-
nal observed by a DSN antennae, and ν model, the pre-
dicted frequency of that signal. The observed, two-way
anomalous eﬀect can be expressed to ﬁrst order in v/c as
[38]
[ν obs(t) − ν model(t)]DSN = −ν 0
2aP t
c ,
ν model = ν 0
[
1 − 2vmodel(t)
c
]
. (15)
Here, ν 0 is the reference frequency, the factor 2 is because
we use two- and three-way data [36]. vmodel is the mod-
eled velocity of the spacecraft due to the gravitational

## Page 19

19
and other large forces discussed in Section IV. (This ve-
locity is outwards and hence produces a red shift.) We
have already included the sign showing that aP is inward.
(Therefore, aP produces a slight blue shift on top of the
larger red shift.) By DSN convention [38], the ﬁrst of Eqs.
(15) is [∆ ν obs − ∆ν model]usual = −[∆ν obs − ∆ν model]DSN.
Over the years the anomaly remained in the data of
both Pioneer 10 and Pioneer 11 [74]. (See Figure 6.)
FIG. 6: ODP plots, as a function of distance from the Sun,
of accelerations on Pioneers 10/11. The accelerations are a )
the calculated solar radiation acceleration (top line), b) the
unmodeled acceleration (bottom line), and c) the sum of the
two above (middle line) [75].
In order to model any unknown forces acting on Pi-
oneer 10, the JPL group introduced a stochastic accel-
eration, exponentially correlated in time, with a time
constant that can be varied. This stochastic variable is
sampled in ten-day batches of data. We found that a
correlation time of one year produces good results. We
did, however, experiment with other time constants as
well, including a zero correlation time (white noise). The
result of applying this technique to 6.5 years of Pioneer
10 and 11 data is shown in Figure 7. The plotted points
represent our determination of the stochastic variable at
ten-day sample intervals. We plot the stochastic variable
as a function of heliocentric distance, not time, because
that is more fundamental in searches for trans-Neptunian
sources of gravitation.
As possible “perturbative forces” to explain this bias,
we considered gravity from the Kuiper belt, gravity from
the galaxy, spacecraft “gas leaks,” errors in the plane-
tary ephemeris, and errors in the accepted values of the
Earth’s orientation, precession, and nutation. We found
that none of these mechanisms could explain the appar-
ent acceleration, and some were three orders of magni-
tude or more too small. [We also ruled out a number
FIG. 7: An ODP plot of the early unmodeled accelerations
of Pioneer 10 and Pioneer 11, from about 1981 to 1989 and
1977 to 1989, respectively [75].
of speciﬁc mechanisms involving heat radiation or “gas
leaks,” even though we feel these are candidates for the
cause of the anomaly. We will return to this in Sections
VII and VIII.]
We concluded [12], from the JPL-ODP analysis, that
there is an unmodeled acceleration, aP , towards the Sun
of (8 . 09 ± 0. 20) × 10− 8 cm/s2 for Pioneer 10 and of
(8. 56 ± 0. 15) × 10− 8 cm/s2 for Pioneer 11. The error was
determined by use of a ﬁve-day batch sequential ﬁlter
with radial acceleration as a stochastic parameter sub-
ject to white Gaussian noise ( ∼ 500 independent ﬁve-day
samples of radial acceleration) [76]. No magnitude varia-
tion of aP with distance was found, within a sensitivity of
σ 0 = 2 × 10− 8 cm/s2 over a range of 40 to 60 AU. All our
errors are taken from the covariance matrices associated
with the least–squares data analysis. The assumed data
errors are larger than the standard error on the post–ﬁt
residuals. [For example, the Pioneer S–band Doppler er-
ror was set at 1 mm/s at a Doppler integration time of 60
s, as opposed to a characteristic χ 2 value of 0.3 mm/s.]
Consequently, the quoted errors are realistic, not formal,
and represent our attempt to include systematics and a
reddening of the noise spectrum by solar plasma. Any
spectral peaks in the post-ﬁt Pioneer Doppler residuals
were not signiﬁcant at a 90% conﬁdence level [12].
B. First Aerospace study of the apparent Pioneer
acceleration
With no explanation of this data in hand, our atten-
tion focused on the possibility that there was some error
in JPL’s ODP. To investigate this, an analysis of the raw

## Page 20

20
data was performed using an independent program, The
Aerospace Corporation’s Compact High Accuracy Satel-
lite Motion Program (CHASMP) [77] – one of the stan-
dard Aerospace orbit analysis programs. CHASMP’s or-
bit determination module is a development of a program
called POEAS (Planetary Orbiter Error Analysis Study
program) that was developed at JPL in the early 1970’s
independently of JPL’s ODP. As far as we know, not a
single line of code is common to the two programs [78].
Although, by necessity, both ODP and CHASMP use
the same physical principles, planetary ephemeris, and
timing and polar motion inputs, the algorithms are oth-
erwise quite diﬀerent. If there were an error in either
program, they would not agree.
Aerospace analyzed a Pioneer 10 data arc that was
initialized on 1 January 1987 at 16 hr (the data itself
started on 3 January) and ended at 14 December 1994, 0
hr. The raw data set was averaged to 7560 data points of
which 6534 points were used. This CHASMP analysis of
Pioneer 10 data also showed an unmodeled acceleration
in a direction along the radial toward the Sun [79]. The
value is (8 . 65 ± 0. 03) × 10− 8 cm/s2, agreeing with JPL’s
result. The smaller error here is because the CHASMP
analysis used a batch least-squares ﬁt over the whole orbit
[76, 77], not looking for a variation of the magnitude of
aP with distance.
Without using the apparent acceleration, CHASMP
shows a steady frequency drift [38] of about −6 × 10− 9
Hz/s, or 1.5 Hz over 8 years (one-way only). (See Fig-
ure 8.) This equates to a clock acceleration, −at, of
−2. 8 × 10− 18 s/s2. The identity with the apparent Pio-
neer acceleration is
at ≡ aP /c. (16)
The drift in the Doppler residuals (observed minus com-
puted data) is seen in Figure 9.
The drift is clear, deﬁnite, and cannot be removed
without either the added acceleration, aP , or the inclu-
sion in the data itself of a frequency drift, i.e., a “clock
acceleration” at. If there were a systematic drift in the
atomic clocks of the DSN or in the time-reference stan-
dard signals, this would appear like a non-uniformity of
time; i.e., all clocks would be changing with a constant
acceleration. We now have been able to rule out this
possibility. (See Section XI D.)
Continuing our search for an explanation, we consid-
ered the possibilities: i) that the Pioneer 10/11 spacecraf t
had internal systematic properties, undiscovered because
they are of identical design, and ii) that the accelera-
tion was due to some not-understood viscous drag force
(proportional to the approximately constant velocity of
the Pioneers). Both these possibilities could be investi-
gated by studying spin-stabilized spacecraft whose spin
axes are not directed towards the Sun, and whose orbital
velocity vectors are far from being radially directed.
Two candidates were Galileo in its Earth-Jupiter mis-
sion phase and Ulysses in Jupiter-perihelion cruise out
of the plane of the ecliptic. As well as Doppler, these
FIG. 8: CHASMP two-way Doppler residuals (observed
Doppler velocity minus model Doppler velocity) for Pioneer
10 vs. time. 1 Hz is equal to 65 mm/s range change per
second. The model is fully-relativistic. The solar system’ s
gravitational ﬁeld is represented by the Sun and its planeta ry
systems [49].
FIG. 9: CHASMP best ﬁt for the Pioneer 10 Doppler residuals
with the anomalous acceleration taken out. After adding one
more parameter to the model (a constant radial acceleration )
the residuals are distributed about zero Doppler velocity w ith
a systematic variation ∼ 3.0 mm/s on a time scale of ∼ 3
months. The outliers on the plot were rejected from the ﬁt.
[The quality of the ﬁt may be determined by the ratio of
residuals to the downlink carrier frequency, ν 0 ≈ 2.29 GHz.]
spacecraft also yielded a considerable quantity of range
data. By having range data one can tell if a spacecraft
is accumulating a range eﬀect due to a spacecraft accel-
eration or if the orbit determination process is fooled by
a Doppler frequency rate bias.

## Page 21

21
C. Galileo measurement analysis
We considered the dynamical behavior of Galileo’s tra-
jectory during its cruise ﬂight from second Earth en-
counter (on 8 December 1992) to arrival at Jupiter. [This
period ends just before the Galileo probe release on 13
July 1995. The probe reached Jupiter on 7 December
1995.] During this time the spacecraft traversed a dis-
tance of about 5 AU with an approximately constant ve-
locity of 7.19(4) km/s.
A quick JPL look at limited Galileo data (241 days
from 8 January 1994 to 6 September 1994) demonstrated
that it was impossible to separate solar radiation eﬀects
from an anomalous constant acceleration. The Sun was
simply too close and the radiation cross-section too large.
The nominal value obtained was ∼ 8 × 10− 8 cm/s2.
The Aerospace’s analysis of the Galileo data covered
the same arc as JPL and a second arc from 2 December
1992 to 24 March 1993. The analysis of Doppler data
from the ﬁrst arc resulted in a determination for aP of
∼ (8 ± 3) × 10− 8 cm/s2, a value similar to that from
Pioneer 10. But the correlation with solar pressure was
so high (0.99) that it is impossible to decide whether solar
pressure is a contributing factor [80].
The second data arc was 113 days long, starting six
days prior to the second Earth encounter. This solution
was also too highly correlated with solar pressure, and
the data analysis was complicated by many mid-course
maneuvers in the orbit. The uncertainties in the maneu-
vers were so great, a standard null result could not be
ruled out.
However, there was an additional result from the data
of this second arc. This arc was chosen for study because
of the availability of ranging data. It had 11596 Doppler
points of which 10111 were used and 5643 range points
of which 4863 used. The two-way range change and time
integrated Doppler are consistent (see Figure 10) to ∼
4 m over a time interval of one day. For comparison,
note that for a time of t = 1 day, ( aP t2/ 2) ∼ 3 m. For
the apparent acceleration to be the result of hardware
problems at the tracking stations, one would need a linear
frequency drift at all the DSN stations, a drift that is not
observed.
D. Ulysses measurement analysis
1. JPL’s analysis
An analysis of the radiation pressure on Ulysses, in
its out-of-the-ecliptic journey from 5.4 AU near Jupiter
in February 1992 to the perihelion at 1.3 AU in Febru-
ary 1995, found a varying proﬁle with distance [81]. The
orbit solution requires a periodic updating of the solar
radiation pressure. The radio Doppler and ranging data
can be ﬁt to the noise level with a time-varying solar con-
stant in the ﬁtting model [82]. We obtained values for
the time-varying solar constant determined by Ulysses
FIG. 10: Galileo best ﬁt Doppler and range residuals using
CHASMP.
navigational data during this south polar pass [81]. The
inferred solar constant is about 40 percent larger at per-
ihelion (1.3 AU) than at Jupiter (5.2 AU), a physical
impossibility!
We sought an alternative explanation. Using physical
parameters of the Ulysses spacecraft, we ﬁrst converted
the time-varying values of the solar constant to a posi-
tive (i.e., outward) radial spacecraft acceleration, ar, as
a function of heliocentric radius. Then we ﬁt the values
of ar with the following model:
ar = Kf⊙ A
cM
cos θ (r)
r2 − aP (U), (17)
where r is the heliocentric distance in AU, M is the to-
tal mass of the spacecraft, f⊙ = 1367 W / m2(AU)2 is
the (eﬀective-temperature Stefan-Boltzmann) “solar ra-
diation constant” at 1 AU, A is the cross-sectional area
of the spacecraft and θ (r) is the angle between the di-
rection to the Sun at distance r and orientation of the
antennae. [For the period analyzed θ (r) was almost a
constant. Therefore its average value was used which
corresponded to ⟨cos θ (r)⟩ ≈ 0. 82.] Optical parameters

## Page 22

22
deﬁning the reﬂectivity and emissivity of the spacecraft’s
surface were taken to yield K ≈ 1. 8. (See Section VII A
for a discussion on solar radiation pressure.) Finally, the
parameter aP (U) was determined by linear least squares.
The best–ﬁt value was obtained
aP (U) = (12 ± 3) × 10− 8 cm/ s2, (18)
where both random and systematic errors are included.
So, by interpreting this time variation as a true r− 2 so-
lar pressure plus a constant radial acceleration, we found
that Ulysses was subjected to an unmodeled acceleration
towards the Sun of (12 ± 3) ×10− 8 cm/s2.
Note, however, that the determined constant aP (U) is
highly correlated with solar radiation pressure (0.888).
This shows that the constant acceleration and the solar-
radiation acceleration are not independently determined,
even over a heliocentric distance variation from 5.4 to 1.3
AU.
2. Aerospace’s analysis
The next step was to perform a detailed calculation of
the Ulysses orbit from near Jupiter encounter to Sun per-
ihelion, using CHASMP to evaluate Doppler and ranging
data. The data from 30 March 1992 to 11 August 1994
was processed. It consisted of 50213 Doppler points of
which 46514 were used and 9851 range points of which
8465 were used.
Such a calculation would in principle allow a more pre-
cise and believable diﬀerentiation between an anomalous
constant acceleration towards the Sun and systematics.
Solar radiation pressure and radiant heat systematics are
both larger on Ulysses than on the Pioneers.
However, this calculation turned out to be a much
more diﬃcult than imagined. Because of a failed nutation
damper, an inordinate number of spacecraft maneuvers
were required (257). Even so, the analysis was completed.
But even though the Doppler and range residuals were
consistent as for Galileo, the results were disheartening.
For an unexpected reason, any ﬁt is not signiﬁcant. The
anomaly is dominated by (what appear to be) gas leaks
[83]. That is, after each maneuver the measured anomaly
changes. The measured anomalies randomly change sign
and magnitude. The values go up to about an order of
magnitude larger than aP . So, although the Ulysses data
was useful for range/Doppler checks to test models (see
Section XI D), like Galileo it could not provide a good
number to compare to aP .
VI. RECENT RESUL TS
Recent changes to our strategies and orbit determi-
nation programs, leading to new results, are threefold.
First, we have added a longer data arc for Pioneer 10,
extending the data studied up to July 1998. The entire
data set used (3 Jan. 1987 to 22 July 1998) covers a he-
liocentric distance interval from 40 AU to 70.5 AU [84].
[Pioneer 11 was much closer in (22.42 to 31.7 AU) than
Pioneer 10 during its data interval (5 January 1987 to
1 October 1990).] For later use in discussing systemat-
ics, we here note that in the ODP calculations, masses
used for the Pioneers were MP io 10 = 251 . 883 kg and
MP io 11 = 239 . 73 kg. CHASMP used 251.883 kg for
both [16]. As the majority of our results are from Pio-
neer 10, we will make M0 = 251. 883 kg to be our nominal
working mass.
Second, and as we discuss in the next subsection, we
have studied the spin histories of the craft. In particular,
the Pioneer 10 history exhibited a very large anomaly in
the period 1990.5 to 1992.5. This led us to take a closer
look at any possible variation of aP among the three time
intervals: The JPL analysis deﬁned the intervals as I (3
Jan. 1987 to 17 July 1990); II (17 July 1990 to 12 July
1992) bounded by 49.5 to 54.8 AU; and III (12 July 1992
to 22 July 1998). (CHASMP used slightly diﬀerent in-
tervals [85]) The total updated data set now consists of
20,055 data points for Pioneer 10. (10,616 data points
were used for Pioneer 11.) This helped us to better un-
derstand the systematic due to gas leaks, which is taken
up in Section VIII F.
Third, in looking at the detailed measurements of aP
as a function of time using ODP, we found an anomalous
oscillatory annual term, smaller in size than the anoma-
lous acceleration [13]. As mentioned in Section IV G, and
as will be discussed in detail in Section IX C, we wanted
to make sure this annual term was not an artifact of our
computational method. For the latest results, JPL used
both the batch-sequential and the least-squares methods.
All our recent results obtained with both the JPL and
The Aerospace Corporation software have given us a bet-
ter understanding of systematic error sources. At the
same time they have increased our conﬁdence in the de-
termination of the anomalous acceleration. We present
a description and summary of the new results in the rest
of this section.
A. Analysis of the Pioneer spin history
Both Pioneers 10 and 11 were spinning down during
the respective data intervals that determined their aP
values. Because any changes in spacecraft spin must be
associated with spacecraft torques (which for lack of a
plausible external mechanism we assume are internally
generated), there is also a possibility of a related inter-
nally generated translational force along the spin axis.
Therefore, it is important to understand the eﬀects of
the spin anomalies on the anomalous acceleration. In
Figures 11 and 12 we show the spin histories of the two
craft during the periods of analysis.
Consider Pioneer 10 in detail. In time Interval I
there is a slow spin down at an average rate (slope) of
∼ (−0. 0181± 0. 0001) rpm/yr. Indeed, a closer look at the

## Page 23

23
FIG. 11: The spin history of Pioneer 10. The vertical lines in -
dicate the times when precession maneuvers were made. How
this spin data was obtained is described in Section III E. The
ﬁnal data points were obtained at the times of maneuvers, the
last being in 1995.
FIG. 12: The spin history of Pioneer 11 over the period of
analysis. The vertical lines indicate the times when preces sion
maneuvers were made. This spin calibration was done by
the DSN until 17 July 1990. At that time the DSN ceased
doing spin calibrations. From 1990 until the loss of coheren t
Doppler, orbit analysts made estimates of the spin rate.
curve (either by eye or from an expanded graph) shows
that the spin down is actually slowing with time (the
curve is ﬂattening). This last feature will be discussed in
Sections VIII B and VIII D.
Every time thrusters are used, there tends to be a
short-term leakage of gas until the valves set (perhaps a
few days later). But there can also be long-term leakages
due to some mechanism which does not quickly correct
itself. The major Pioneer 10 spin anomaly that marks the
boundary of Intervals I and II, is a case in point. During
this interval there was a major factor of ∼ 4. 5 increase
in the average spin-rate change to ∼ (−0. 0861 ± 0. 0009)
rpm/yr. One also notices kinks during the interval.
Few values of the Pioneer 10 spin rate were obtained
after mid-1993, so the long-term spin-rate change is not
well-determined in Interval III. But from what was mea-
sured, there was ﬁrst a short-term transition region of
about a year where the spin-rate change was ∼ − 0. 0160
rpm/yr. Then things settled down to a spin-rate change
of about ∼ (−0. 0073 ± 0. 0015) rpm/yr, which is small
and less than that of interval I.
The eﬀects of the maneuvers on the values of aP will
allow an estimation of the gas leak systematic in Section
VIII F. Note, however, that in the time periods studied,
only orientation maneuvers were made, not trajectory
maneuvers.
Shortly after Pioneer 11 was launched on 5 April 1973,
the spin period was 4.845 s. A spin precession maneuver
on 18 May 1973 reduced the period to 4.78 s and after-
wards, because of a series of precession maneuvers, the
period lengthened until it reached 5.045 s at encounter
with Jupiter in December 1974. The period was fairly
constant until 18 December 1976, when a mid-course
maneuver placed the spacecraft on a Saturn-encounter
trajectory. Before the maneuver the period was 5.455 s,
while after the maneuver it was 7.658 s. At Saturn en-
counter in December 1979 the period was 7.644 s, little
changed over the three-year post maneuver cruise phase.
At the start of our data interval on 5 January 1987, the
period was 7.321 s, while at the end of the data interval
in October 1990 it was 7.238 s.
Although the linear ﬁt to the Pioneer 11 spin rate
shown in Figure 12 is similar to that for Pioneer 10 in
Interval I, ∼ (−0. 0234 ± 0. 0003) rpm/yr, the causes ap-
pear to be very diﬀerent. (Remember, although iden-
tical in design, Pioneers 10 and 11 were not identical
in quality [14].) Unlike Pioneer 10, the spin period for
Pioneer 11 was primarily aﬀected at the time of spin pre-
cession maneuvers. One sees that at maneuvers the spin
period decreases very quickly, while in between maneu-
vers the spin rate actually tends to increase at a rate of
∼ (+0. 0073 ± 0. 0003) rpm/yr (perhaps due to a gas leak
in the opposite direction).
All the above observations aid us in the interpretation
of systematics in the following three sections.
B. Recent results using JPL software
The latest results from JPL are based on an upgrade,
Sigma, to JPL’s ODP software [86]. Sigma, developed for
NASA’s Cassini Mission to Saturn, eliminates structural
restrictions on memory and architecture that were im-
posed 30 years ago when JPL space navigation depended
solely on a Univac 1108 mainframe computer. Five ODP
programs and their interconnecting ﬁles have been re-
placed by the single program Sigma to support ﬁltering,
smoothing, and mapping functions.
We used Sigma to reduce the Pioneer 10 (in three time
intervals) and 11 Doppler of the unmodeled acceleration,
aP , along the spacecraft spin axis. As mentioned, the
Pioneer 10 data interval was extended to cover the to-

## Page 24

24
TABLE I: Determinations of aP in units of 10 − 8 cm/s2 from the three time intervals of Pioneer 10 data and from Pion eer
11. As described in the text, results from various ODP/ Sigma and CHASMP calculations are listed. For ODP/ Sigma, “ WLS”
signiﬁes a weighted least-squares calculation, which was u sed with i) no solar corona model and ii) the ‘Cassini’ solar c orona
model. Also for ODP/ Sigma, “ BSF” signiﬁes a batch-sequential ﬁlter calculation, which was done with iii) the ‘Cassini’ solar
corona model. Further (see Section IX C), a 1-day batch-sequ ential estimation for the entire data interval of 11.5 years for
Pioneer 10 yielded a result aP = (7. 77 ± 0. 16) × 10− 8 cm/s2. The CHASMP calculations were all WLS. These calculations were
done with i) no solar corona model, ii) the ‘Cassini’ solar co rona model, iii) the ‘Cassini’ solar corona model with coron a data
weighting and F10.7 time variation calibration. Note that t he errors given are only formal calculational errors. The mu ch
larger deviations of the results from each other indicate th e sizes of the systematics that are involved.
Program/Estimation method Pio 10 (I) Pio 10 (II) Pio 10 (III) Pio 11
Sigma, WLS,
no solar corona model 8. 02 ± 0. 01 8. 65 ± 0. 01 7. 83 ± 0. 01 8. 46 ± 0. 04
Sigma, WLS,
with solar corona model 8. 00 ± 0. 01 8. 66 ± 0. 01 7. 84 ± 0. 01 8. 44 ± 0. 04
Sigma, BSF, 1-day batch,
with solar corona model 7. 82 ± 0. 29 8. 16 ± 0. 40 7. 59 ± 0. 22 8. 49 ± 0. 33
CHASMP, WLS,
no solar corona model 8. 25 ± 0. 02 8. 86 ± 0. 02 7. 85 ± 0. 01 8. 71 ± 0. 03
CHASMP, WLS,
with solar corona model 8. 22 ± 0. 02 8. 89 ± 0. 02 7. 92 ± 0. 01 8. 69 ± 0. 03
CHASMP, WLS, with
corona, weighting, and F10.7 8. 25 ± 0. 03 8. 90 ± 0. 03 7. 91 ± 0. 01 8. 91 ± 0. 04
tal time interval 3 January 1987 to 22 July 1998. Of
the total data set of 20,055 Pioneer 10 Doppler points,
JPL used ∼19,403, depending on the initial conditions
and editing for a particular run. Of the available 10,616
(mainly shorter time-averaged) Pioneer 11 data points,
10,252 were used (4919 two-way and 5333 three-way).
We wanted to produce independent (i.e., uncorrelated)
solutions for aP in the three Pioneer 10 segments of data.
The word independent solution in our approach means
only the fact that data from any of the three segments
must not have any information (in any form) passed
onto it from the other two intervals while estimating the
anomaly. We moved the epoch from the beginning of
one data interval to the next by numerically integrating
the equations of motion and not iterating on the data
to obtain a better initial conditions for this consequent
segment. Note that this numerical iteration provided us
only with an a priori estimate for the initial conditions
for the data interval in question.
Other parameters included in the ﬁtting model were
the six spacecraft heliocentric position and velocity co-
ordinates at the 1987 epoch of 1 January 1987, 01:00:00
ET, and 84 (i.e., 28 × 3) instantaneous velocity increments
along the three spacecraft axes for 28 spacecraft attitude
(or spin orientation) maneuvers. If these orientation ma-
neuvers had been performed at exactly six month inter-
vals, there would have been 23 maneuvers over our 11.5
year data interval. But in fact, ﬁve more maneuvers were
performed than expected over this 11.5 year interval giv-
ing a total of 28 maneuvers in all.
As noted previously, in ﬁtting the Pioneer 10 data over
11.5 years we used the standard space-ﬁxed J2000 coordi-
nate system with planetary ephemeris DE405, referenced
to ICRF. The three-dimensional locations of the track-
ing stations in the Earth’s body-ﬁxed coordinate system
(geocentric radius, latitude, longitude) were taken from a
set recommended by ICRF for JPL’s DE405. The time-
varying Earth orientation in J2000 coordinates was de-
ﬁned by a 1998 version of JPL’s EOP ﬁle. This accounted
for the geophysical motion of the Earth’s pole with re-
spect to its spin axis and the Earth’s time varying spin
rate.
JPL used both the weighted least-squares ( WLS) and
the batch-sequential ﬁlter ( BSF) algorithms for the ﬁnal
calculations. In the ﬁrst three rows of Table I are shown
the ODP results for i) WLS with no corona, ii) WLS with
the Cassini corona model, and iii) BSF with the Cassini
corona model.
Observe that the WLS acceleration values for Pioneer
10 in Intervals I, II, and III are larger or smaller, re-
spectively, just as the spin-rate changes in these inter-
vals are larger or smaller, respectively. This indicates
that the small deviations may be due to a correlation
with the large gas leak/spin anomaly. We will argue this
quantitatively in Section VIII F. For now we just note
that we therefore expect the number from Interval III,
aP = 7 . 83 × 10− 8cm/s2, to be close to our basic (least
perturbed) JPL result for Pioneer 10. We also note that
the statistical errors and the eﬀect of the solar corona
are both small for WLS, and will be handled in our error
budget.
In Figure 13 we show ODP/ Sigma WLS Doppler residu-
als for the entire Pioneer 10 data set. The residuals were
obtained by ﬁrst solving for aP with no corona in each of
the three Now look at the batch-sequential results in row
3 of Table I. First, note that the statistical Intervals in-

## Page 25

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

## Page 26

26
for the extended-time Interval III values for Pioneer 10,
which interval had clean data. However there is more
disagreement with the values for Pioneer 10 in Intervals
I and II and for Pioneer 11. These three data sets all
were noisy and underwent more data-editing. Therefore,
it is signiﬁcant that the deviations between Sigma and
CHASMP in these arcs are all similar, but small, be-
tween 0 . 20 to 0 . 25 of our units. As before, the eﬀect
of the solar corona is small, even with the various model
variations. But most important, the numbers from Sigma
and CHASMP for Pioneer 10 Interval III are in excellent
agreement.
Further, CHASMP also found the annual term. (Re-
call that CHASMP can also look for a temporal varia-
tion by calculating short time averages.) Results on the
time variation in aP can be seen in Figure 14. Although
there could possibly be aP variations of ±2 × 10− 8 cm/s2
on a 200-day time scale, a comparison of the variations
with the error limits shown in Figure 14 indicate that our
measurements of these variations are not statistically sig -
niﬁcant. The 5-day averages of aP from ODP (using the
batch-sequential method) are not reliable at solar con-
junction in the middle (June) of each year, and hence
should be ignored there. The CHASMP 200-day aver-
ages suppress the solar conjunction bias inherent in the
ODP 5-day averages, and they reliably indicate a con-
stant value of aP . Most encouraging, these results clearly
indicate that the obtained solution is consistent, stable,
and its mean value does not strongly depend on the esti-
mation procedure used. The presence of the small annual
term on top of the obtained solution is apparent.
D. Our solution, before systematics, for the
anomalous acceleration
From Table I we can intuitively draw a number of con-
clusions:
A) The eﬀect of the corona is small. This systematic
will be analyzed in Section VII B.
B) The numerical error is small. This systematic will
be analyzed in Section IX A.
C) The diﬀerences between the Sigma and CHASMP
Pioneer 10 results for Interval I and Interval II, respec-
tively, we attribute to two main causes: especially i) the
diﬀerent data rejection techniques of the two analyses but
also ii) the diﬀerent maneuver simulations. Both of these
eﬀects were especially signiﬁcant in Interval II, where the
data arc was small and a large amount of noisy data was
present. Also, to account for the discontinuity in the spin
data that occurred on 28 January 1992 (see Figure 11),
Aerospace introduced a ﬁctitious maneuver for this in-
terval. Even so, the deviation in the two values of aP
was relatively small, namely 0 . 23 and 0 . 21, respectively,
×10− 8 cm/s2.
D) The changes in aP in the diﬀerent Intervals, corre-
lated with the changes in spin-rate change, are likely (at
least partially) due to gas leakage. This will be discussed
FIG. 14: Consistency of the ODP/ Sigma and CHASMP time-
variation signals. The dots show 5-day sample averages of
the anomalous acceleration of Pioneer 10 from ODP/ Sigma
using BSF with a 200-day correlation time. From this data,
the solid lines show the mean values of aP in the three inter-
vals corresponding to the three separate spin down historie s.
The dashed lines represent the large batch-sequential comp u-
tational error bounds on the three values of aP . The 200-
day acceleration values using CHASMP are the solid squares.
At the time positions where there are CHASMP results, the
agreement between the CHASMP and the ODP/ Sigma results
is clear.
in Section VIII F.
But independent of the origin, this last correlation be-
tween shifts in aP and changes in spin rate actually allows
us to calculate the best “experimental” base number for
Pioneer 10. To do this, assume that the spin-rate change
is directly contributing to an anomalous acceleration oﬀ-
set. Mathematically, this is saying that in any interval
i = I, II, III, for which the spin-rate change is an approx-
imate constant, one has
aP (¨θ ) = aP (0) − κ ¨θ, (19)
where κ is a constant with units of length and aP (0) ≡
aP (¨θ = 0) is the Pioneer acceleration without any spin-
rate change.
One now can ﬁt the data to Eq. (19) to obtain solutions
for κ and aP (0). The three intervals i = I , II, III provide
three data combinations {aP (i)(¨θ ), ¨θ i}. We take our base
number, with which to reference systematics, to be the
weighted average of the Sigma and CHASMP results for
aP (0) when no corona model was used. Start ﬁrst with the
Sigma Pioneer 10 solutions in row one of Table I and the
Pioneer 10 spin-down rates given in Section VI B and Fig-
ure 11: aSigma
P (i) = (8. 02 ± 0. 01, 8. 65 ± 0. 01, 7. 83 ± 0. 01) in
units of 10 − 8 cm/s2 and ¨θ i = −(0. 0181± 0. 0001, 0. 0861±
0. 0009, 0. 0073 ± 0. 0015) in units of rpm/yr, where
1 rpm / year = 5 . 281 × 10− 10 rev/ s2
= 3 . 318 × 10− 9 radians/ s2. (20)

## Page 27

27
With these data we use the maximum likelihood
and minimum variance approach to ﬁnd the optimally
weighted least-squares solution for aP (0):
aSigma
P (0) = (7 . 82 ± 0. 01) × 10− 8 cm/ s2, (21)
with solution for the parameter κ obtained as κ Sigma =
(29. 2 ± 0. 7) cm. Similarly, for CHASMP one takes the
values for aP from row four of Table I: aCHASMP
P (i) = (8. 25 ±
0. 02, 8. 86 ± 0. 02, 7. 85 ± 0. 01) and uses them with the
same ¨θ i as above. The solution for aP (0) in this case is
aCHASMP
P (0) = (7 . 89 ± 0. 02) × 10− 8 cm/ s2, (22)
together with κ CHASMP = (34 . 7 ± 1. 1) cm. The solutions
for Sigma and CHASMP are similar, 7.82 and 7.89 in our
units. We take the weighted average of these two to yield
our base line “experimental” number for aP :
aPio10
P (exper) = (7 . 84 ± 0. 01) × 10− 8 cm/ s2. (23)
[The weighted average constant κ is κ 0 = (30 . 7 ± 0. 6)
cm.]
For Pioneer 11, we only have the one 3 3
4 year data arc.
The weighted average of the two programs’ no corona re-
sults is (8. 62±0. 02)×10− 8 cm/s2. We observed in Section
VI A that between maneuvers (which are accounted for
- see Section IV E) there is actually a spin rate increase
of ∼ (+0. 0073 ± 0. 0003) rpm/yr. If one uses this spin-up
rate and the Pioneer 10 value for κ 0 = 30 . 7 cm given
above, one obtains a spin-rate change corrected value for
aP . We take this as the experimental value for Pioneer
11:
aPio11
P (exper) = (8. 55 ± 0. 02) × 10− 8 cm/ s2. (24)
VII. SOURCES OF SYSTEMATIC ERROR
EXTERNAL TO THE SP ACECRAFT
We are concerned with possible systematic acceleration
errors that could account for the unexplained anomalous
acceleration directed toward the Sun. There exist de-
tailed publications describing analytic recipes develope d
to account for non-gravitational accelerations acting on
spacecraft. (For a summary see Milani et al. [57].) With
regard to the speciﬁc Pioneer spacecraft, possible sources
of systematic acceleration have been discussed before for
Pioneer 10 and 11 at Jupiter [87] and Pioneer 11 at Sat-
urn [67].
External forces can produce three vector components
of spacecraft acceleration, unlike forces generated on
board the spacecraft, where the two non-radial compo-
nents (i.e., those that are eﬀectively perpendicular to
the spacecraft spin) are canceled out by spacecraft ro-
tation. However, non-radial spacecraft accelerations are
diﬃcult to observe by the Doppler technique, which mea-
sures spacecraft velocity along the Earth-spacecraft line
of sight. But with several years of Doppler data, it is in
principle possible to detect systematic non-radial accel-
eration components [73].
With our present analysis [73] we ﬁnd that the Doppler
data yields only one signiﬁcant component of unmodeled
acceleration, and that any acceleration components per-
pendicular to the spin axis are small. This is because
in the ﬁtting we tried including three unmodeled accel-
eration constants along the three spacecraft axes (spin
axis and two orthogonal axes perpendicular to the spin
axis). The components perpendicular to the spin axis
had values consistent with zero to a 1- σ accuracy of 2
× 10− 8 cm/s2 and the radial component was equal to
the reported anomalous acceleration. Further, the ra-
dial acceleration was not correlated with the other two
unmodeled acceleration components.
Although one could in principle set up complicated en-
gineering models to predict all or each of the systemat-
ics, often the uncertainty of the models is too large to
make them useful, despite the signiﬁcant eﬀort required.
A diﬀerent approach is to accept our ignorance about a
non-gravitational acceleration and assess to what extent
these can be assumed a constant bias over the time scale
of all or part of the mission. (In fact, a constant ac-
celeration produces a linear frequency drift that can be
accounted for in the data analysis by a single unknown
parameter.) In fact, we will use both approaches.
In most orbit determination programs some eﬀects, like
the solar radiation pressure, are included in the set of
routinely estimated parameters. Nevertheless we want
to demonstrate their inﬂuence on Pioneer’s navigation
from the general physics standpoint. This is not only to
validate our results, but also to be a model as to how
to study the inﬂuence of the other physical phenomena
that are not yet included in the standard navigational
packages for future more demanding missions. Such mis-
sions will involve either spacecraft that will be distant
or spacecraft at shorter distances where high-precision
spacecraft navigation will be required.
In this section we will discuss possible systematics (in-
cluding forces) generated external to the spacecraft which
might signiﬁcantly aﬀect our results. These start with
true forces due to (1) solar-radiation pressure and (2) so-
lar wind pressure. We go on to discuss (3) the eﬀect of the
solar corona and its mismodeling, (4) electro-magnetic
Lorentz forces, (5) the inﬂuence of the Kuiper belt, (6)
the phase stability of the reference atomic clocks, and
(7) the mechanical and phase stability of the DSN an-
tennae, together with inﬂuence of the station locations
and troposphere and ionosphere contributions.
A. Direct solar radiation pressure and mass
There is an exchange of momentum when solar pho-
tons impact the spacecraft and are either absorbed or
reﬂected. Models for this solar pressure eﬀect were de-
veloped before either Pioneer 10 or 11 were launched [88]

## Page 28

28
and have been reﬁned since then. The models take into
account various parts of the spacecraft exposed to solar
radiation, primarily the high-gain antenna. It computes
an acceleration directed away from the Sun as a function
of spacecraft orientation and solar distance.
The models for the acceleration due to solar radiation
can be formulated as
as.p.(r) = Kf⊙ A
c M
cos θ (r)
r2 . (25)
f⊙ = 1367 W / m2(AU)2 is the (eﬀective-temperature
Stefan-Boltzmann) “solar radiation constant” at 1 AU
from the Sun and A is the eﬀective size of the craft as
seen by the Sun [89]. (For Pioneer the area was taken
to be the antenna dish of radius 1.73 m.) θ is the an-
gle between the axis of the antenna and the direction of
the Sun, c is the speed of light, M is the mass of the
spacecraft (taken to be 251.883 for Pioneer 10), and r
is the distance from the Sun to the spacecraft in AU. K
[90] is the eﬀective [91] absorption/reﬂection coeﬃcient.
For Pioneer 10 the simplest approximately correct model
yields K0 = 1 . 71 [91]. Eq. (25) provides a good model
for analysis of the eﬀect of solar radiation pressure on
the motion of distant spacecraft and is accounted for by
most of the programs used for orbit determination.
However, in reality the absorptivities, emissivities, and
eﬀective areas of spacecraft parts parameters which, al-
though modeled by design, are determined by calibration
early in the mission [92]. One determines the magnitude
of the solar-pressure acceleration at various orientation s
using Doppler data. (The solar pressure eﬀect can be
distinguished from gravity’s 1 /r 2 law because cos θ varies
[45].) The complicated set of program input parameters
that yield the parameters in Eq. (25) are then set for
later use [92]. Such a determination of the parameters
for Pioneer 10 was done, soon after launch and later.
When applied to the solar radiation acceleration in the
region of Jupiter, this yields (from a 5 % uncertainty in
as.p. [87])
as.p.(r = 5. 2AU) = (70 . 0 ± 3. 5) × 10− 8 cm/ s2,
K5.2 = 1 . 77. (26)
The second of Eqs. (26) comes from putting the ﬁrst into
Eq. (25). Note, speciﬁcally, that in a ﬁt a too high input
mass will be compensated for by a higher eﬀective K.
Because of the 1 /r 2 law, by the time the craft reached
10 AU the solar radiation acceleration was 18 . 9 × 10− 8
cm/s2 going down to 0.39 of those units by 70 AU. Since
this systematic falls oﬀ as r− 2, it can bias the Doppler de-
termination of a constant acceleration at some level, even
though most of the systematic is correctly modeled by
the program itself. By taking the average of the r− 2 ac-
celeration curves over the Pioneer distance intervals, we
estimate that the systematic error from solar-radiation
pressure in units of 10 − 8 cm/ s2 is 0.001 for Pioneer 10
over an interval from 40 to 70 AU, and 0.006 for Pioneer
11 over an interval from 22 to 32 AU.
However, this small uncertainty is not our main prob-
lem. In actuality, since the parameters were ﬁt the mass
has decreased with the consumption of propellant. Eﬀec-
tively, the 1/r 2 systematic has changed its normalization
with time. If not corrected for, the diﬀerence between
the original 1 /r 2 and the corrected 1 /r 2 will be inter-
preted as a bias in aP . Unfortunately, exact information
on gas usage is unavailable [16]. Therefore, in dealing
with the eﬀect of the temporal mass variation during the
entire data span (i.e. nominal input mass vs. actual mass
history [15, 16]) we have to address two eﬀects on the so-
lutions for the anomalous acceleration aP . They are i)
the eﬀect of mass variation from gas consumption and ii)
the eﬀect of an incorrect input mass [15, 16].
To resolve the issue of mass variation uncertainty we
performed a sensitivity analysis of our solutions to dif-
ferent spacecraft input masses. We simply re-did the no-
corona, WLS runs of Table I with a range of diﬀerent
masses. The initial wet weight of the package was 259 kg
with about 36 kg of consumable propellant. For Pioneer
10, the input mass in the program ﬁt was 251.883 kg,
roughly corresponding to the mass after spin-down. By
our data period, roughly half the fuel (18 kg) was gone
so we take 241 kg as our nominal Pioneer 10 mass. Thus,
the eﬀect of going from 251.883 kg to 241 kg we take to
be our bias correction for Pioneer 10. We take the un-
certainty to be given by one half the eﬀect of going from
plus to minus 9 kg (plus or minus a quarter tank) from
the nominal mass of 241 kg.
For the three intervals of Pioneer 10 data, using
ODP/Sigma yields the following changes in the accel-
erations:
δa mass
P = [(0 . 040 ± 0. 035), (0. 029 ± 0. 025),
(0. 020 ± 0. 017)] × 10− 8 cm/ s2.
As expected,these results make aP larger. For our sys-
tematic bias we take the weighted average of δa mass
P for
the three intervals of Pioneer 10. The end result is
as.p. = (0. 03 ± 0. 01) × 10− 8 cm/ s2. (27)
For Pioneer 11 we did the same except our bias point
was 3/4 of the fuel gone (232 kg). Therefore the bias
results by going from the input mass of 239.73 to 232 kg.
The uncertainty is again deﬁned by ± 9 kg. The result
for Pioneer 11 is more sensitive to mass changes, and we
ﬁnd using ODP/ Sigma
as.p. = (0. 09 ± 0. 21) × 10− 8 cm/ s2. (28)
The bias number is three times larger than the similar
number for Pioneer 10, and the uncertainty much larger.
We return to this diﬀerence in Section VIII G.
The previous analysis also allowed us to perform
consistency checks on the eﬀective values of K which
the programs were using. By taking [ rminrmax]− 1 =
[
∫
(dr/r 2)/
∫
dr] for the inverse distance squared of a data
set, varying the masses, and determining the shifts in aP

## Page 29

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

## Page 30

30
Also, there is an upper limit to the charge that a space-
craft can hold. For the Pioneers that limit produced an
upper bound on the Lorentz acceleration at closest ap-
proach to Jupiter of 20 × 10− 8 cm/s2 [87]. With the
interplanetary ﬁeld being so much lower than at Jupiter,
we conclude that the electro-magnetic force on the Pio-
neer spacecraft in the outer solar system is at worst on
the order of 10 − 12 cm/s2, completely negligible [94].
Similarly, the magnetic torques acting on the space-
craft were about a factor of 10 − 5 times smaller than
those acting on Earth satellites, where they are a con-
cern. Therefore, for the Pioneers any observed changes
in spacecraft spin cannot be caused by magnetic torques.
E. The Kuiper belt’s gravity
From the study of the resonance eﬀect of Neptune upon
Pluto, two primary mass concentration resonances of 3:2
and 2:1 were discovered [95], corresponding to 39.4 AU
and 47.8 AU, respectively. Previously, Boss and Peale
had derived a model for a non-uniform density distribu-
tion in the form of an inﬁnitesimally thin disc extending
from 30 AU to 100 AU in the ecliptic plane [96]. We
combined the results of Refs. [95] and [96] to determine
if the matter in the Kuiper belt could be the source of
the anomalous acceleration of Pioneer 10 [97].
We speciﬁcally studied three distributions, namely: i)
a uniform distribution, ii) a 2:1 resonance distribution
with a peak at 47.8 AU, and iii) a 3:2 resonance distri-
bution with a peak at 39.4 AU. Figure 15 exhibits the
resulting acceleration felt by Pioneer 10, from 30 to 65
AU which encompassed our data set at the time.
FIG. 15: Possible acceleration caused by dust in the Kuiper
belt.
We assumed a total mass of one Earth mass, which is
signiﬁcantly larger than standard estimates. Even so, the
accelerations are only on the order of 10 − 9 cm/s2, which
is two orders of magnitude smaller than the observed
eﬀect. (See Figure 15.) Further, the accelerations are
not constant across the data range. Rather, they show
an increasing eﬀect as Pioneer 10 approaches the belt
and a decreasing eﬀect as Pioneer 10 recedes from the
belt, even with a uniform density model. For these two
reasons, we excluded the dust belt as a source for the
Pioneer eﬀect.
More recent infrared observations have ruled out more
than 0.3 Earth mass of Kuiper Belt dust in the trans-
Neptunian region [98, 99]. Therefore, we can now place
a limit of ±3 × 10− 10 cm/s2 for the contribution of the
Kuiper belt.
Finally, we note that searches for gravitational encoun-
ters of Pioneer with large Kuiper-belt objects have so far
not been successful [100].
F. Phase and frequency stability of clocks
After traversing the mechanical components of the an-
tenna, the radio signal enters the DSN antenna feed and
passes through a series of ampliﬁers, ﬁlters, and cables.
Averaged over many experiments, the net eﬀect of this
on the calculated dynamical parameters of a spacecraft
should be very small. We expect instrumental calibra-
tion instabilities to contribute 0 . 2 × 10− 8 cm/s2 to the
anomalous acceleration on a 60 s time interval. Thus,
in order for the atomic clocks [101] to have caused the
Pioneer eﬀect, all the atomic clocks used for signal refer-
encing clocks would have had to have drifted in the same
manner as the local DSN clocks.
In Section V we observed that without using the appar-
ent anomalous acceleration, the CHASMP residuals show
a steady frequency drift [38] of about −6 × 10− 9 Hz/s,
or 1.5 Hz over 8 years (one-way only). This equates to
a clock acceleration, −at, of −2. 8 × 10− 18 s/s2. (See Eq.
(16) and Figure 8.) To verify that it is actually not the
clocks that are drifting, we analyzed the calibration of
the frequency standards used in the DSN complex.
The calibration system itself is referenced to Hydro-
gen maser atomic clocks. Instabilities in these clocks
are another source of instrumental error which needs
to be addressed. The local reference is synchronized
to the frequency standards generated either at the Na-
tional Institute of Standards and Technology (NIST), lo-
cated in Boulder, Colorado or at the U. S. Naval Obser-
vatory (USNO), Washington, DC. These standards are
presently distributed to local stations by the Global Po-
sitioning System (GPS) satellites. [During the pre-GPS
era, the station clocks used signals from WWV to set the
Cesium or Hydrogen masers. WWV, the radio station
which broadcasts time and frequency services, is located
in Fort Collins, CO.] While on a track, the station is
“free-running,” i.e., the frequency and timing data are
generated locally at the station. The Allan variances are
about 10 − 13 for Cesium and 10 − 15 for Hydrogen masers.
Therefore, over the data-pass time interval, the data ac-
curacy is on the order of one part in 1000 GHz or better.

## Page 31

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

## Page 32

32
using both Sigma and CHASMP. Based on these stud-
ies we conclude that mechanical and phase stability of
the DSN antennae together with geographical locations
of the antennae, geophysical and atmospheric conditions
on the antennae site have negligible eﬀects on our solu-
tions for aP . At most their contributions are at the level
of σ DSN ≤ 10− 5aP .
VIII. SOURCES OF SYSTEMATIC ERROR
INTERNAL TO THE SP ACECRAFT
In this section we will discuss the forces that may be
generated by spacecraft systems. The mechanisms we
consider that may contribute to the found constant ac-
celeration, aP , and that may be caused by the on-board
mechanisms include: (1) the radio beam reaction force,
(2) RTG heat reﬂecting oﬀ the spacecraft, (3) diﬀeren-
tial emissivity of the RTGs, (4) non-isotropic radiative
cooling of the spacecraft, (5) expelled Helium produced
within the RTG, (6) thruster gas leakage, and (7) the dif-
ference in experimental results from the two spacecraft.
A. Radio beam reaction force
The Pioneer navigation does not require that the
spacecraft constantly beam its radio signal, but instead
it does so only when it is requested to do so from the
ground control. Nevertheless, the recoil force due to the
emitted radio-power must also be analyzed.
The Pioneers have a total nominal emitted radio power
of eight Watts. It is parameterized as
Prp =
∫ θmax
0
dθ sin θ P(θ ), (32)
P(θ ) being the antenna power distribution. The radiated
power has been kept constant in time, independent of
the coverage from ground stations. That is, the radio
transmitter is always on, even when not received by a
ground station.
The recoil from this emitted radiation produces an
acceleration bias, brp, on the spacecraft away from the
Earth of
brp = β P rp
M c . (33)
M is taken to be the Pioneer mass when half the fuel is
gone [15]. β is the fractional component of the radiation
momentum that is going in a direction opposite to aP :
β = 1
Prp
∫ θmax
0
dθ sin θ cos θ P(θ ). (34)
Ref [4] describes the HGA and shows its downlink an-
tenna pattern in Fig. 3.6-13. (Thermal antenna expan-
sion mismodeling is thought to be negligible.) The gain
is given as (33 . 3 ± 0. 4) dB at zero (peak) degrees. The
intensity is down by a factor of two ( −3 dB) at 1.8 de-
grees. It is down a factor of 10 ( −10 dB) at 2.7 degrees
and down by a factor of 100 ( −20 dB) at 3.75 degrees.
[The ﬁrst diﬀraction minimum is at a little over four de-
grees.] Therefore, the pattern is a very good conical
beam. Further, since cos[3 . 75◦] = 0 . 9978, we can take
β = (0. 99 ± 0. 01), yielding brp = 1. 10.
Finally, taking the error for the nominal 8 Watts power
to be given by the 0.4 dB antenna error (0 . 10) and the
error due to the uncertainty in our nominal mass (0 . 04),
we arrive at the result
arp = brp ± σ rp = (1. 10 ± 0. 11) × 10− 8 cm/ s2. (35)
B. R TG heat reﬂecting oﬀ the spacecraft
It has been argued that the anomalous acceleration
seen in the Pioneer spacecraft is due to anisotropic heat
reﬂection oﬀ of the back of the spacecraft high-gain an-
tennae, the heat coming from the RTGs [103]. Before
launch, the four RTGs had a total thermal fuel inventory
of 2580 W (now ∼ 2070 W). They produced a total elec-
trical power of 160 W (now ∼ 65 W). Presently ∼ 2000
W of RTG heat must be dissipated. Only ∼ 63 W of
directed power could explain the anomaly. Therefore, in
principle there is enough power to explain the anomaly
this way. However, there are two reasons that preclude
such a mechanism, namely:
i) The spacecraft geometry: The RTGs are located at
the end of booms, and rotate about the spacecraft in a
plane that contains the approximate base of the antenna.
From the closest axial center point of the RTGs, the an-
tenna is seen nearly “edge on” (the longitudinal angular
width is 24.5 o). The total solid angle subtended is ∼ 1-
2% of 4 π steradians [104]. Even though a more detailed
calculation yields a value of 1.5% [105], even taking the
higher bound of 2% means this proposal could provide at
most ∼ 40 W. But there is more [106].
ii) The RTGs’ radiation pattern: The above estimate
was based on the assumption that the RTGs are spher-
ical black bodies. But they are not. The main bodies
of the RTGs are cylinders and they are grouped in two
packages of two. Each package has the two cylinders end
to end extending away from the antenna. Every RTG has
six ﬁns separated by equal angles of 60 degrees that go
radially out from the cylinder. Presumably this results
in a symmetrical radiation of thermal power into space.
Thus, the ﬁns are “edge on” to the antenna (the ﬁns
point perpendicular to the cylinder axes). The largest
opening angle of the ﬁns is seen only by the narrow-angle
parts of the antenna’s outer edges. Ignoring these edge
eﬀects, only ∼2.5% of the surface area of the RTGs is
facing the antenna. This is a factor 10 less than that from
integrating the directional intensity from a hemisphere:
[(
∫ h.sph.
dΩ cos θ )/ (4π )] = 1 / 4. So, one has only 4 W
of directed power. This suggests a systematic bias of

## Page 33

33
∼ 0. 55 × 10− 8 cm/s2. Even adding an uncertainty of the
same size yields a systematic for heat reﬂection of
ah.r. = (−0. 55 ± 0. 55) × 10− 8 cm/ s2. (36)
But there are reasons to consider this an upper bound.
The Pioneer SNAP 19 RTGs have larger ﬁns than the
earlier test models and the packages were insulated so
that the end caps have lower temperatures. This results
in lower radiation from the end caps than from the cylin-
der/ﬁns [20, 21]. As a result, even though this is not
exact, we can argue that the vast majority of the heat
radiated by the RTGs is symmetrically directed to space
unobscured by the antenna. Further, for this mechanism
to work one still has to assume that the energy hitting
the antenna is completely reradiated in the direction of
the spin axis [106].
Finally, if this mechanism were the cause, ultimately
an unambiguous decrease in the size of aP should be seen
because the RTGs’ radioactively produced radiant heat
is decreasing. As noted previously, the heat produced is
now about 80% of the original magnitude. In fact, one
would similarly expect a decrease of about 0 . 75 × 10− 8
cm/s2 in aP over the 11.5 year Pioneer 10 data interval
if this mechanism were the origin of aP .
So, even though a complete thermal/physical model of
the spacecraft might be able to ascertain if there are any
other unsuspected heat systematics, we conclude that
this particular mechanism does not provide enough power
to explain the Pioneer anomaly [107].
In addition to the observed constancy of the anomalous
acceleration, any explanation involving thermal radiatio n
must also discuss the absence of a disturbance to the spin
of the spacecraft. There may be a small correlation of
the spin angular acceleration with the anomalous linear
acceleration. However, as described in Section VI, the
linear acceleration is much more constant than the spin.
This suggests that most of the linear acceleration is not
caused by whatever disturbs the spin, thermal or not.
However, a careful look at the Interval I results of Fig-
ure 11 shows that the nearly steady, background spin-rate
change of about 6 × 10− 5 rpm/day is slowly decreasing.
In principle this could be caused by heat.
The spin-rate change produced by the torque of radiant
power directed against the rotation with a lever arm d is
¨θ = P d
c Iz
, (37)
where Iz is the moment of inertia, 588.3 kg m 2 [17]. We
take a base unit of ¨θ 0 for a power of one Watt and a lever
arm of one meter. This is
¨θ 0 = 5 . 63 × 10− 12 rad/ s2 = 4. 65 × 10− 6 rpm/ day =
= 1 . 71 × 10− 3 rpm/ yr. (38)
So, about 13 Watt-meters of directed power could cause
the base spin-rate change.
It turns out that such sources could, in principle, be
available. There are 3 × 3 = 9 radioisotope heater units
(RHUs) with one Watt power to heat the Thruster Clus-
ter Assembly (TCA). (See pages 3.4-4 and 3.8-1–3.8-17
of Ref. [4].) The units are on the edge of the antenna of
radius 1.37 m, in the housings of the TCAs which are ap-
proximately 180 ◦ apart from each other. At one position
there are six RHUs and at the other position there are
three. An additional RHU is near the sun sensor which
is located near the second assembly. The ﬁnal RHU is
located at the magnetometer, 6.6 meters out from the
center of the spacecraft.
The placement gives an “ideal” rotational asymmetry
of two Watts. But note, the real asymmetry should be
less, since these RHUs do not radiate only in one direc-
tion. Even one Watt unidirected at the magnetometer, is
not enough to cause the baseline spin rate decrease. Fur-
ther, since the base line is decreasing faster than what
would come from the change cause by radioactive decay
decrease, one cannot look for this eﬀect or some com-
plicated RTG source as the entire origin of the baseline
change. One would suspect a very small gas leak or a
combination of this and heat from the powered bus. (See
Section VIII D.) Indeed, the factor 1 /c in Eq. (37) is
a manifestation of the energy-momentum conservation
power needed to produce ¨θ by heat vs. massive particles.
But in any event, this baseline spin-rate change is not
signiﬁcantly correlated with the anomalous acceleration,
so we do not have to pursue it further.
C. Diﬀerential emissivity of the R TGs
Another suggestion related to the RTGs is the follow-
ing [108]: during the early parts of the missions, there
might have been a diﬀerential change of the radiant emis-
sivity of the solar-pointing sides of the RTGs with re-
spect to the deep-space facing sides. Note that, especially
closer in the Sun, the inner sides were subjected to the
solar wind. Contrariwise, the outer sides were sweeping
through the solar-system dust cloud. Therefore, it can
be argued that these two processes could have caused
the eﬀect. However, other information seems to make it
diﬃcult for this explanation to work.
The six ﬁns of each RTG, designed to “provide the
bulk of the heat rejection capacity,” were fabricated of
HM21A-T8 magnesium alloy plate [20]. The metal, after
being specially prepared, was coated with two to three
mils of zirconia in a sodium silicate binder to provide
a high emissivity ( ∼ 0. 9) and low absorptivity ( ∼ 0. 2).
Depending on how symmetrically fore-and-aft they ra-
diated, the relative fore-and-aft emissivity of the alloy
would have had to have changed by ∼ 10% to account
for aP (see below). Given our knowledge of the solar
wind and the interplanetary dust (see Section XI A), we
ﬁnd that this amount of a radiant change would be diﬃ-
cult to explain, even if it were of the right sign. (In fact,
even the brace bars holding the RTGs were built such
that radiation is roughly fore/aft symmetric,)
We also have “visual” evidence from the Voyager

## Page 34

34
spacecraft. As mentioned, the Voyagers are not spin-
stabilized. They have imaging video cameras attached
[109]. The cameras are mounted on a scan platform that
is pointed under both celestial and inertial attitude con-
trol modes [110]. The cameras do not have lens covers
[111]. During the outward cruise calibrations, the cam-
eras were sometimes pointed towards an imaging tar-
get plate mounted at the rear of the spacecraft. But
most often they were pointed all over the sky at speciﬁc
star ﬁelds in support of ultraviolet spectrometer observa-
tions. Meanwhile, the spacecraft antennae were pointed
towards Earth. Therefore, at an angle, the lenses were
sometimes hit by the solar wind and sometimes by the
interplanetary dust. Even so, there was no noticeable
deterioration of the images received, even when Voyager
2 reached Neptune [112]. We infer, therefore, that this
mechanism can not explain the Pioneer eﬀect.
It turned out that the greatest radiation damage oc-
curred during the ﬂybys. The peak Pioneer 10 radiation
ﬂux near Jupiter was about 10,000 times that of Earth
for electrons (1,000 times for protons). Pioneer 11 expe-
rienced an even higher radiation ﬂux and also went by
Saturn [3]. (We return to this in Section VIII G.) There-
fore, if radiation damage was a problem, one should have
seen an approximately uniform change in emissivity dur-
ing ﬂyby. Since the total heat ﬂux, F , from the RTGs was
a constant over a ﬂyby, there would have been a change
in the RTG surface temperature manifested by the radi-
ation formula F ∝ ǫ 1T 4
1 = ǫ 2T 4
2 , the ǫ i being the emissiv-
ities of the ﬁn material. There are several temperature
sensors mounted at RTG ﬁn bases. They measured aver-
age temperatures of approximately 330 F, roughly 440 K.
Therefore, a 10% change in the total average emissivity
would have produced a temperature change of ∼12.2 K
= 22 F. Such a change would have been noticed. (Mea-
surements would be compared from, say, 30 days before
and after ﬂyby to eliminate the ﬂyby power/thermal dis-
tortions.) Since (see below) a 10% diﬀerential fore/aft
emissivity could cause the Pioneer eﬀect, the lack of ob-
servation of a 10% total average emissivity change limits
the size of the diﬀerential emissivity systematic.
To obtain a reasonable estimate of the uncertainty,
consider if one side (fore or aft) of the RTGs had its
emissivity changed by 1% with respect to the other side.
In a simple cylindrical model of the RTGs, with 2000
W power (here we presume only radial emission with no
loss out the sides), the ratio of power emitted by the
two sides would be 0.99 = 995/1005, or a diﬀerential
emission between the half cylinders of 10 W. Therefore,
the fore/aft asymmetry towards the normal would be
[10 W] ×
∫ π
0 [sin φ ]dφ/π ≈ 6. 37 W. If one does a more
sophisticated ﬁn model, with 4 of the 12 ﬁns facing the
normal (two ﬂat and two at 30 ◦), one gets a number of
6.12 W. We take this to yield our uncertainty,
σ d.e. = 0. 85 × 10− 8 cm/ s2. (39)
Note that 10 σ d.e. almost equals our ﬁnal aP . This is the
origin of our previous statement that ∼ 10% diﬀerential
emissivity (in the correct direction) would be needed to
explain aP .
Finally, we want to comment on the signiﬁcance of ra-
dioactive decay for this mechanism. Even acknowledging
the Interval jumps due to gas leaks (see below), we re-
ported a one-day batch-sequential value (before system-
atics) for aP , averaged over the entire 11.5 year interval,
of aP = (7 . 77 ± 0. 16) × 10− 8 cm/s2. From radioactive
decay, the value of aP should have decreased by 0 . 75 of
these units over 11.5 years. This is 5 times the above
variance, which is very large with batch sequential. Even
more stringently, this bound is good for all radioactive
heat sources. So, what if one were to argue that emissiv-
ity changes occurring before 1987 were the cause of the
Pioneer eﬀect? There still should have been a decrease
in aP with time since then, which has not been observed.
We will return to these points in Section VIII G.
D. Non-isotropic radiative cooling of the spacecraft
It has also been suggested that the anomalous acceler-
ation seen in the Pioneer 10/11 spacecraft can be, “ex-
plained, at least in part, by non-isotropic radiative cool-
ing of the spacecraft [113].” So, the question is, does “at
least in part” mean this eﬀect comes near to explaining
the anomaly? We argue it does not [114].
Consider radiation of the main-bus electrical systems
power from the spacecraft rear. For the Pioneers, the
aft has a louver system, and “the louver system acts to
control the heat rejection of the radiating platform. A
bimetallic spring, thermally coupled radiatively to the
platform, provides the motive force for altering the angle
of each blade. In a closed position (below 40 F) the heat
rejection of the platform is minimized by virtue of the
blockage of the blades while open ﬁn louvers provide the
platform with a nearly unobstructed view of space [4].”
If these louvers were open (above ∼ 88 F) and all the
diminishing electrical-power heat was radiated only out
of the louvers, this mechanism could produce a signif-
icant eﬀect. However, by nine AU the actuator spring
temperature had already reached ∼40 F [4]. This means
the louver doors were closed (i.e., the louver angle was
zero) from where we obtained our data. Thus, from that
time on of the radiation properties, the contribution of
the thermal radiation to the Pioneer anomalous accelera-
tion should be small. Although one might speculate that
a louver stuck, there are 30 louvers on each craft. They
clearly worked as designed, or else the temperature of the
crafts’ interiors would have fallen to disastrous levels.
As shown in Figure 16, in 1984 Pioneer 10 was at about
33 AU and the power was about 105 W. (Always reduce
the total power numbers by 8 W to account for the radio
beam power.) In (1987, 1992, 1996) the spacecraft was
at ∼(41, 55, 65) AU and the power was ∼(95, 82, 73)
W. The louvers were inactive, and no decrease in aP was
seen.
In fact, during the entire 11.5 year period from 1987 to

## Page 35

35
FIG. 16: The Pioneer 10 electrical power generated at the
RTGs as a function of time from launch to near the end of
1994. By 1998.5, only ∼68 W was generated.
1998 the electrical power decreased from around 95 W to
around 68 W, a change of 27 W. Since we already have
noted that about ∼ 65 W is needed to cause our eﬀect,
such a large decrease in the “source” of the acceleration
would have been seen. But as shown in Section VI, it was
not. Even the small diﬀerences in the three intervals are
most likely to be from gas leaks (as will be demonstrated
in Section VIII F).
Later a double modiﬁcation of this idea was given. It
was ﬁrst suggested that “most, if not all, of the unmod-
eled acceleration” of Pioneer 10 and 11 is due to an es-
sentially constant supply of heat coming from the central
compartment, directed out the front of the craft through
the closed louvers [115]-(a). However, when one studies
the electrical power history in both parts (instruments
and experimental) of the central compartment, there is
no constancy of heat. (See the details in [116].) Indeed
during our data period the heat from this compartment
decreased from about 73 W to about 57 Watts, or a fac-
tor of 1.26. This is inconsistent with the constancy of our
result. Further, if one looks at the earlier, very roughly
analyzed [117] data in Figure 7 one sees nothing close to
the internal power change of 93 to 57 W (a factor of 1.6)
[116].
To address this inconsistency a second modiﬁcation
[115]-b,c was made. It was arbitrarily argued that
there was an incorrect determination of the reﬂec-
tion/absorption coeﬃcients by a large factor. But these
coeﬃcients are known to 5%. If they were as poorly de-
termined as speculated, the mission would have failed
early on. (Further discussion is in [116].)
We conclude that neither the original proposal [113]
nor the modiﬁcation [115] can explain the anomalous
Pioneer acceleration [114, 116]. A bound on the con-
stancy of aP comes from ﬁrst noting the 11.5 year 1-
day batch-sequential result, sensitive to time variation:
aP = (7. 77±0. 16)×10− 8 cm/s2. Also given the constancy
of the earlier imprecise date, it is conservative to take
three times this error to be our systematic uncertainty
for radiative cooling of the craft, σ r.c. = ±0. 48 × 10− 8
cm/s2.
Although doubtful, one can also speculate that some
mechanism like this might be involved with the baseline
spin-rate change discussed in Section VIII B. In 1986-7,
Pioneer 10 power was about 97 W, decreasing at about
2.5-3.0 W/yr. If you take a lever arm of 0.71 meters (the
hexagonal bus size), this is more than enough to pro-
vide the 13 W-meters necessary to produce the baseline
spin-rate change of Figure 11. Further for the ﬁrst three
years the decrease about matches the bus power loss rate.
Then after the complex changes associated with the end
of 1989 to 1990, there is a decrease in the base rate with
a continued similar slope.
Perhaps the “baseline” rate is indeed from the heat of
the bus being vented to the side. But the much larger
gas leaks would be on top of the baseline.
E. Expelled Helium produced within the R TGs
Another possible on-board systematic is from the ex-
pulsion of the He being created in the RTGs from the
α -decay of 238Pu. To make this mechanism work, one
would need that the He leakage from the RTGs be pref-
erentially directed away from the Sun, with a velocity
large enough to cause the acceleration.
The SNAP-19 Pioneer RTGs were designed in a such a
way that the He pressure has not been totally contained
within the Pioneer heat source over the life of RTGs [20].
Instead, the Pioneer heat source contains a pressure re-
lief device which allows the generated He to vent out
of the heat source and into the thermoelectric converter.
(The strength member and the capsule clad contain small
holes to permit He to escape into the thermoelectric con-
verter.) The thermoelectric converter housing-to-power
output receptacle interface is sealed with a viton O-ring.
The O-ring allows the helium gas within the converter
to be released by permeation to the space environment
throughout the mission life of the Pioneer RTGs.
Information on the fuel pucks [118] shows that they
each have heights of 0.212 inches with diameters of 2.145
inches. With 18 in each RTG and four RTGs per mission,
this gives a total volume of fuel of about 904 cm 3. The
fuel is PMC Pu conglomerate. The amount of 238Pu in
this fuel is about 5.8 kg. With a half life of 87.74 years,
that means the rate of He production (from Pu decay)
is about 0.77 gm/year, assuming it all leaves the cermet.
Taking on operational temperature on the RTG surface
of 320 F = 433 K, implies a 3 kT / 2 helium velocity of
1.22 km/s. (The possible energy loss coming out of the
viton is neglected for helium.) Using this in the rocket
equation,
a(t) = −v(t) d
dt
[
ln M (t)
]
(40)
with our nominal Pioneer mass with half the fuel gone
and the assumption that the gas is all unidirected, yields a
maximal bound on the possible acceleration of 1 . 16×10− 8

## Page 36

36
cm/s2. So, we can rule out helium permeating through
the O-rings as the cause of aP although it is a systematic
to be dealt with.
Of course, the gas is not totally unidirected. As one
can see by looking at Figures 2 and III-2 of [20]: the
connectors with the O-rings are on the RTG cylinder
surfaces, on the ends of the cylinders where the ﬁns are
notched. They are equidistant (30 degrees) from two of
the ﬁns. The placement is exactly at the “rear” direction
of the RTG cylinders, i.e., at the position closest to the
Sun/Earth. The axis through the O-rings is parallel to
the spin-axis. The O-rings, sandwiched by the receptacle
and connector plates, “see” the outside world through an
angle of about 90 ◦ in latitude [119]. (Overhead of the O-
rings is towards the Sun.) In longitude the O-rings see
the direction of the bus and space through about 90 ◦, and
“see” the ﬁns through most of the rest of the longitudinal
angle.
If one assumes a single elastic reﬂection, one can es-
timate the fraction of the bias away from the Sun. (In-
deed, multiple and back reﬂections will produce an even
greater bias. Therefore, we feel this approximation is
justiﬁed.) This estimate is (3 / 4) sin 30◦ times the av-
erage of the heat momentum component parallel to the
shortest distance to the RTG ﬁn. Using this, we ﬁnd the
bias would be 0 . 31 × 10− 8 cm/s2. This bias eﬀectively
increases the value of our solution for aP , which we hesi-
tate to accept given all the true complications of the real
system. Therefore we take the systematic expulsion to
be aHe = (0. 15 ± 0. 16) × 10− 8 cm/s2.
F. Propulsive mass expulsion due to gas leakage
The eﬀect of propulsive mass expulsion due to gas leak-
age has to be assessed. Although this eﬀect is largely un-
predictable, many spacecraft have experienced gas leaks
producing accelerations on the order of 10 − 7 cm/ s2. [The
reader will recall the even higher ﬁgure for Ulysses found
in Section V D 2.] As noted previously, gas leaks gener-
ally behave diﬀerently after each maneuver. The leakage
often decreases with time and becomes negligibly small.
Gas leaks can originate from Pioneer’s propulsion sys-
tem, which is used for mid-course trajectory maneu-
vers, for spinning-up or -down the spacecraft, and for
orientation of the spinning spacecraft. The Pioneers
are equipped with three pairs of hydrazine thrusters
which are mounted on the circumference of the Earth-
pointing high gain antenna. Each pair of thrusters forms
a Thruster Cluster Assembly (TCA) with two nozzles
aligned in opposition to each other. For attitude control,
two pairs of thrusters can be ﬁred forward or aft and are
used to precess the spinning antenna (See Section II B.)
The other pair of thrusters is aligned parallel to the rim
of the antenna with nozzles oriented in co- and contra-
rotation directions for spin/despin maneuvers.
During both observing intervals for the two Pioneers,
there were no trajectory or spin/despin maneuvers. So,
in this analysis we are mainly concerned with preces-
sion (i.e., orientation or attitude control) maneuvers onl y.
(See Section II B.) Since the valve seals in the thrusters
can never be perfect, one can ask if the leakages through
the hydrazine thrusters could be the cause of the anoma-
lous acceleration, aP .
However, when we investigate the total computational
accuracy of our solution in Section IX B, we will show
that the currently implemented models of propulsion ma-
neuvers may be responsible for an uncertainty in aP only
at the level of ±0. 01 × 10− 8 cm/s2. Therefore, the ma-
neuvers themselves are the main contributors neither to
the total error budget nor to the gas leak uncertainty, as
we now detail
The serious uncertainty comes from the possibility of
undetected gas leaks. We will address this issue in some
detail. First consider the possible action of gas leaks
originating from the spin/despin TCA. Each nozzle from
this pair of thrusters is subject to a certain amount of
gas leakage. But only a diﬀerential leakage from the two
nozzles would produce an observable eﬀect causing the
spacecraft to either spin-down or spin-up [120]. So, to
obtain a gas leak uncertainty (and we emphasize “uncer-
tainty” vs. “error” because we have no other evidence)
let us ask how large a diﬀerential force is needed to cause
the spin-down or spin-up eﬀects observed?
Using the moment of inertia about the spin axis, Iz =∼
588. 3 kg·m2 [17], and the antenna radius, R = 1. 37 m, as
the lever arm, one can calculate that the diﬀerential force
needed to torque the spin-rate change, ¨θ i, in Intervals
i =I,II,III is
F¨θi
= Iz ¨θ i
R =
(
2. 57, 12. 24, 1. 03
)
× 10− 3 dynes. (41)
It is possible that a similar mechanism of undetected
gas leakage could be responsible for the net diﬀerential
force acting in the direction along the line of sight. In
other words, what if there were some undetected gas leak-
age from the thrusters oriented along the spin axis of the
spacecraft that is causing aP ? How large would this have
to be? A force of ( M = 241 kg)
FaP = M a P = 21. 11 × 10− 3 dynes (42)
would be needed to produce our ﬁnal unbiased value of
aP . (See Section X. That is, one would need even more
force than is needed to produce the anomalously high
rotational gas leak of Interval II. Furthermore, the dif-
ferential leakage to produce this aP would have had to
have been constant over many years and in the same di-
rection for both spacecraft, without being detected as
a spin-rate change. That is possible, but certainly not
demonstrated. Furthermore if the gas leaks hypothesis
were true, one would expect to see a dramatic diﬀerence
in aP during the three Intervals of Pioneer 10 data. In-
stead an almost 500 % spin-down rate change between
Intervals I and II resulted only in a less than 8% change
in aP .

## Page 37

37
Given the small amount of information, we propose
to conservatively take as our gas leak uncertainties the
acceleration values that would be produced by diﬀerential
forces equal to
FaP (i)g.l. ≃ ±
√
2F¨θi
= (43)
=
(
± 3. 64, ± 17. 31, ± 1. 46
)
× 10− 3 dynes.
The argument for this is that, in the root sum of squares
sense, one is accounting for the diﬀerential leakages from
the two pairs of thrusters with their nozzles oriented
along the line of sight direction. This directly trans-
lates into the acceleration errors introduced by the leak-
age during the three intervals of Pioneer 10 data,
σ (aP (i)g.l.) = ±FaP (i)g.l./M = (44)
=
(
± 1. 51, ± 7. 18, ± 0. 61
)
× 10− 8 cm/ s2.
Assuming that these errors are uncorrelated and are nor-
mally distributed around zero mean, we ﬁnd the gas leak
uncertainty for the entire Pioneer 10 data span to be
σ g.l. = ±0. 56 × 10− 8 cm/ s2. (45)
This is one of our largest uncertainties.
The data set from Pioneer 11 is over a much smaller
time span, taken when Pioneer 11 was much closer to
the Sun (oﬀ the plane of the ecliptic), and during a max-
imum of solar activity. For Pioneer 11 the main eﬀects
of gas leaks occurred at the maneuvers, when there were
impulsive lowerings of the spin-down rate. These dom-
inated the over-all spin rate change of ¨θ 11 = −0. 0234
rpm/yr. (See Figure 12.) But in between maneuvers the
spin rate was actually increasing. One can argue that
this explains the higher value for aP (11) in Table I as
compared to aP (10). Unfortunately, one has no a priori
way of predicting the eﬀect here. We do not know that
the same speciﬁc gas leak mechanism applied here as did
in the case of Pioneer 10 and there is no well-deﬁned in-
terval set as there is for Pioneer 10. Therefore, although
we feel this “spin up” may be part of the explanation
of the higher value of aP for Pioneer 11, we leave the
diﬀerent numbers as a separate systematic for the next
subsection.
At this point, we must conclude that the gas leak mech-
anism for explaining the anomalous acceleration seems
very unlikely, because it is hard to understand why it
would aﬀect Pioneer 10 and 11 at the same level (given
that both spacecraft had diﬀerent quality of propulsion
systems, see Section II B). One also expects a gas leak
would obey the rules of a Poisson distribution. That
clearly is not true. Instead, our analyses of diﬀerent data
sets indicate that aP behaves as a constant bias rather
than as a random variable. (This is clearly seen in the
time history of aP obtained with batch-sequential esti-
mation.)
G. Variation between determinations from the two
spacecraft
Finally there is the important point that we have two
“experimental” results from the two spacecraft, given in
Eqs. (23) and (24): 7.84 and 8.55, respectively, in units
of 10 − 8 cm/s2. If the Pioneer eﬀect is real, and not a sys-
tematic, these numbers should be approximately equal.
The ﬁrst number, 7.84, is for Pioneer 10. In Section
VI D we obtained this number by correlating the values
of aP in the three data Intervals with the diﬀerent spin-
down rates in these Intervals. The weighted correlation
between a shift in aP and the spin-down rate is κ 0 =
(30. 7±0. 6) cm. (We argued in the previous Section VIII F
that this correlation is the manifestation of the rotationa l
gas leak systematic.) Therefore, this number represents
the entire 11.5 year data arc of Pioneer 10. Similarly,
Pioneer 11’s number, 8.55, represents a 3 3
4 year data arc.
Even though the Pioneer 11 number may be less re-
liable since the craft was so much closer to the Sun,
we calculate the time-weighted average of the exper-
imental results from the two craft: [(11 . 5)(7. 84) +
(3. 75)(8. 55)]/ (15. 25) = 8 . 01 in units of 10 − 8 cm/s2. This
implies a bias of b2
craft = +0 . 17 × 10− 8 cm/s2 with re-
spect to the Pioneer 10 experimental result aP (exper). We
also take this number to be our two spacecraft uncer-
tainty. This means
a2− craft = b2− craft ± σ 2
craft =
= (0 . 17 ± 0. 17) × 10− 8 cm/ s2. (46)
The diﬀerence between the two craft could be due to
diﬀerent gas leakage. But it also could be due to heat
emitted from the RTGs. In particular, the two sets of
RTGs have had diﬀerent histories and so might have dif-
ferent emissivities. Pioneer 11 spent more time in the
inner solar system (absorbing radiation). Pioneer 10 has
swept out more dust in deep space. Further, Pioneer 11
experienced about twice as much Jupiter/Saturn radia-
tion as Pioneer 10.
Further, note that [ aPio11
P (exper) − aPio10
P (exper)] and the uncer-
tainty from diﬀerential emissivity of the RTGs, σ d.e., are
of the same size: 0.71 and 0.85 ×10− 8 cm/s2. It could
therefore be argued that Pioneer 11’s oﬀset from Pioneer
10 comes from Pioneer 11 having obtained twice as large
a diﬀerential emissivity bias as Pioneer 10. Then our ﬁ-
nal value of aP , given in Section X, would be reduced
by about 0 . 7 of our units since σ d.e. would have become
mainly a negative bias, bd.e.. This would make the ﬁnal
number closer to 8 × 10− 8 cm/s2. Because this model
and our ﬁnal number are consistent, we present this ob-
servation only for completeness and as a possible reason
for the diﬀerent results of the two spacecraft.

## Page 38

38
IX. COMPUTATIONAL SYSTEMATICS
Given the very large number of observations for the
same spacecraft, the error contribution from observa-
tional noise is very small and not a meaningful measure of
uncertainty. It is therefore necessary to consider several
other eﬀects in order to assign realistic errors. Our ﬁrst
consideration is the statistical and numerical stability o f
of the calculations. We then go on to the cumulative
inﬂuence of all modeling errors and editing decisions. Fi-
nally we discuss the reasons for and signiﬁcance of the
annual term.
Besides the factors mentioned above, we will discuss in
this section errors that may be attributed to the speciﬁc
hardware used to run the orbit determination computer
codes, together with computational algorithms and sta-
tistical methods used to derive the solution.
A. Numerical stability of least-squares estimation
Having presented estimated solutions along with their
formal statistics, we should now attempt to characterize
the true accuracy of these results. Of course, the signiﬁ-
cance of the results must be assessed on the basis of the
expected measurement errors. These expected errors are
used to weight a least-squares adjustment to parameters
which describe the theoretical model. [Examination of
experimental systematics from sources both external to
and also internal to the spacecraft was covered in Sections
VII-VIII.]
First we look at the numerical stability of the least
squares estimation algorithm and the derived solution.
The leading computational error source turns out to be
subtraction of similar numbers. Due to the nature of
ﬂoating point arithmetic, two numbers with high order
digits the same are subtracted one from the other re-
sults in the low order digits being lost. This situation
occurs with time tags on the data. Time tags are refer-
enced to some epoch, such as say 1 January 1 1950 which
is used by CHASMP. As more than one billion seconds
have passed since 1950, time tags on the Doppler data
have a start and end time that have ﬁve or six common
leading digits. Doppler signal is computed by a diﬀer-
enced range formulation (see Section III B). This noise
in the time tags causes noise in the computed Doppler
at the 0.0006 Hz level for both Pioneers. This noise can
be reduced by shifting the reference epoch closer to the
data or increasing the word length of the computation,
however, it is not a signiﬁcant error source for this anal-
ysis.
In order to guard against possible computer com-
piler and/or hardware errors we ran orbit determina-
tion programs on diﬀerent computer platforms. JPL’s
ODP resides on an HP workstation. The Aerospace
Corporation ran the analysis on three diﬀerent com-
puter architectures: (i) Aerospace’s DEC 64-bit RISC
architecture workstation (Alphastation 500/266), (ii)
Aerospace’s DEC 32-bit CISC architecture workstation
(V AX 4000/60), and (iii) Pentium Pro PC. Comparisons
of computations performed for CHASMP in the three
machine show consistency to 15 digits which is just suﬃ-
cient to represent the data. While this comparison does
not eliminate the possibility of systematic errors that are
common to both systems, it does test the numerical sta-
bility of the analysis on three very diﬀerent computer
architectures.
The results of the individual programs were given
in Sections Vand VI. In a test we took the JPL re-
sults for a batch-sequential Sigma run with 50-day av-
erages of the anomalous acceleration of Pioneer 10, aP .
The data interval was from January 1987 to July 1998.
We compared this to an Aerospace determination using
CHASMP, where the was split into 200 day intervals,
over a shorter data interval ending in 1994. As seen in
Figure 14, the results basically agree.
Given the excellent agreement in these implementa-
tions of the modeling software, we conclude that diﬀer-
ences in analyst choices (parameterization of clocks, data
editing, modeling options, etc.) give rise to coordinate
discrepancies only at the level of 0 . 3 cm. This number
corresponds to an uncertainty in estimating the anoma-
lous acceleration on the order of 8 × 10− 12 cm/s2.
But there is a slightly larger error to contend with. In
principle the STRIPPER can give output to 16 signiﬁcant
ﬁgures. From the beginning the output was-rounded oﬀ
to 15 and later to 14 signiﬁcant ﬁgures. When Block
5 came on near the beginning of 1995, the output was
rounded oﬀ to 13 signiﬁcant ﬁgures. Since the Doppler
residuals are 1.12 mm/s this last truncation means an
error of order 0.01 mm/s. If we divide this number by 2
for an average round oﬀ, this translates to ±0. 04 × 10− 8
cm/s2. The roundoﬀ occurred in approximately all the
data we added for this paper. This is the cleanest 1/3
of the Pioneer 10 data. Considering this we take the
uncertainty to be
σ num ± 0. 02 × 10− 8 cm/ s2. (47)
It needs to be stressed that such tests examine only
the accuracy of implementing a given set of model codes,
without consideration of the inherent accuracy of the
models themselves. Numerous external tests, which we
have been discussing in the previous three sections, are
possible for assessing the accuracy of the solutions. Com-
parisons between the two software packages enabled us
to evaluate the implementations of the theoretical mod-
els within a particular software. Likewise, the results of
independent radio tracking observations obtained for the
diﬀerent spacecraft and analysis programs have enabled
us to compare our results to infer realistic error levels
from diﬀerences in data sets and analysis methods. Our
analysis of the Galileo and Ulysses missions (reported in
Sections V C and V D) was done partially for this pur-
pose.

## Page 39

39
B. Accuracy of consistency/model tests
a. Consistency of solutions: A code that models
the motion of solar system bodies and spacecraft in-
cludes numerous lengthy calculations. Therefore, the
software used to obtain solutions from the Doppler data
is, of necessity, very complex. To guard against poten-
tial errors in the implementation of these models, we
used two software packages; JPL’s ODP/ Sigma model-
ing software [41, 54] and The Aerospace Corporation’s
POEAS/CHASMP software package [77, 78]. The diﬀer-
ences between the JPL and Aerospace orbit determina-
tion program results are now examined.
As discussed in Section IV F, in estimating parame-
ters the CHASMP code uses a standard variation of pa-
rameters method whereas ODP uses the Cowell method
to integrate the equations of motion and the variational
equations. In other words, CHASMP integrates six ﬁrst-
order diﬀerential equation, using the Adams-Moulton
predictor-corrector method in the orbital elements. Con-
trariwise, ODP integrates three second-order diﬀerential
equations for the accelerations using the Gauss-Jackson
method. (For more details on these methods see Ref.
[121].)
As seen in our results of Sections Vand VI, agreement
was good; especially considering that each program uses
independent methods, models, and constants. Internal
consistency tests indicate that a solution is consistent at
the level of one part in 10 15. This implies an acceleration
error on the order of no more then one part in 10 4 in aP .
b. Earth orientation parameters: In order to check
for possible problems with Earth orientation, CHASMP
was modiﬁed to accept Earth orientation information
from three diﬀerent sources. (1) JPL’s STOIC pro-
gram that outputs UT1R-UTC, (2) JPL’s Earth Orienta-
tion Parameter ﬁles (UT1-UTC), and (3) The International
Earth Rotation Service’s Earth Orientation Parameter
ﬁle ( UT1-UTC). We found that all three sources gave vir-
tually identical results and changed the value of aP only
in the 4th digit [122].
c. Planetary ephemeris: Another possible source of
problems is the planetary ephemeris. To explore this a
ﬁt was ﬁrst done with CHASMP that used DE200. The
solution of that ﬁt was then used in a ﬁt where DE405
was substituted for DE200. The result produced a small
annual signature before the ﬁt. After the ﬁt, the maneu-
ver solutions changed a small amount (less then 10%)
but the value of the anomalous acceleration remained
the same to seven digits. The post-ﬁt residuals to DE405
were virtually unchanged from those using DE200. This
showed that the anomalous acceleration was unaﬀected
by changes in the planetary ephemeris.
This is pertinent to note for the following subsection.
To reemphasize the above, a small “annual term” can be
introduced by changing the planetary ephemerides. This
annual term can then be totally taken up by changing
the maneuver estimations. Therefore, in principle, any
possible mismodeling in the planetary ephemeris could be
at least partially masked by the maneuver estimations.
d. Diﬀerences in the codes’ model implementations:
The impact of an analyst’s choices is diﬃcult to address,
largely because of the time and expense required to pro-
cess a large data set using complex models. This is espe-
cially important when it comes to data editing. It should
be understood that small diﬀerences are to be expected
as models diﬀer in levels of detail and accuracy. The an-
alysts’ methods, experience, and judgment diﬀer. The
independence of the analysis of JPL and Aerospace has
been consistently and strictly maintained in order to pro-
vide conﬁdence on the validity of the analyses. Acknowl-
edging such diﬃculties, we still feel that using the very
limited tests given above is preferable to an implicit as-
sumption that all analysts’ choices were optimally made.
Another source for diﬀerences in the results presented
in Table I is the two codes’ modeling of spacecraft re-
orientation maneuvers. ODP uses a model that solves
for the resulted change in the Doppler observable ∆ v
(instantaneous burn model). This is a more convenient
model for Doppler velocity measurements. CHASMP
models the change in acceleration, solves for ∆ a (ﬁnite
burn model), and only then produces a solution for ∆ v.
Historically, this was done in order to incorporate range
observations (for Galileo and Ulysses) into the analysis.
Our best handle on this is the no-corona results, espe-
cially given that the two critical Pioneer 10 Interval III
results diﬀered by very little, 0 . 02 × 10− 8 cm/s2. This
data is least aﬀected by maneuver modeling, data edit-
ing, corona modeling, and spin calibration. Contrari-
wise, for the other data, the diﬀerences were larger. The
Pioneer Interval I and II results and the Pioneer 11 re-
sults diﬀered, respectively, by (0.21, 0.23, 0.25) in units
of 10 − 8 cm/s2. In these intervals models of maneuvers
and data editing were crucial. Assuming that these er-
rors are uncorrelated, we compute their combined eﬀect
on anomalous acceleration aP as
σ consist/model = ±0. 13 × 10− 8 cm/s2. (48)
e. Mismodeling of maneuvers: A small contribution
to the error comes from a possible mismodeling of the
propulsion maneuvers. In Section IV E we found that for
a typical maneuver the standard error in the residuals is
σ 0 ∼ 0. 095 mm/s.
Then we would expect that in the period between two
maneuvers, which on average is τ = 11.5/28 year, the ef-
fect of the mismodeling would produce a contribution to
the acceleration solution with a magnitude on the order
of δa man = σ 0/τ = 0. 07 × 10− 8 cm/s2. Now let us assume
that the errors in the Pioneer Doppler residuals are nor-
mally distributed around zero mean with the standard
deviation of δa man that constitute a single measurement
accuracy. Then, since there are N = 28 maneuvers in the
data set, the total error due to maneuver mismodeling is
σ man = δa man
√
N
= 0. 01 × 10− 8 cm/ s2. (49)

## Page 40

40
f. Mismodeling of the solar corona: Finally, recall
that our number for mismodeling of the solar corona,
±0. 02 × 10− 8 cm/s2, was already explained in Section
VII C.
C. Apparent annual/diurnal periodicities in the
solution
In Ref. [13] we reported, in addition to the constant
anomalous acceleration term, a possible annual sinusoid.
If approximated by a simple sine wave, the amplitude
of this oscillatory term is about 1 . 6 × 10− 8 cm/s2. The
integral of a sine wave in the acceleration, aP , with an-
gular velocity ω and amplitude A0 yields the following
ﬁrst-order Doppler amplitude in two-way fractional fre-
quency:
∆ν
ν = 2A0
c ω . (50)
The resulting Doppler amplitude for the annual angular
velocity ∼ 2 × 10− 7 rad/s is ∆ ν/ν = 5.3 × 10− 12. At
the Pioneer downlink S-band carrier frequency of ∼ 2. 29
GHz, the corresponding Doppler amplitude is 0.012 Hz
(i.e. 0.795 mm/s).
This term was ﬁrst seen in ODP using the BSF method.
As we discussed in Section IV G, treating aP as a stochas-
tic parameter in JPL’s batch–sequential analysis allows
one to search for a possible temporal variation in this
parameter. Moreover, when many short interval times
were used with least-squares CHASMP, the eﬀect was
also observed. (See Figure 14 in Section VI.)
The residuals obtained from both programs are of the
same magnitude. In particular, the Doppler residuals
are distributed about zero Doppler velocity with a sys-
tematic variation ∼ 3.0 mm/s on a time scale of ∼ 3
months. More precisely, the least-squares estimation
residuals from both ODP/ Sigma and CHASMP are dis-
tributed well within a half-width taken to be 0.012 Hz.
(See, for example, Figure 9.) Even the general structures
of the two sets of residuals are similar. The fact that
both programs independently were able to produce simi-
lar post-ﬁt residuals gives us conﬁdence in the solutions.
With this conﬁdence, we next looked in greater de-
tail at the acceleration residuals from solutions for aP .
Consider Figure 17, which shows the aP residuals from
a value for aP of (7 . 77 ± 0. 16) × 10− 8 cm/s2. The data
was processed using ODP/ Sigma with a batch-sequential
ﬁlter and smoothing algorithm. The solution for aP
was obtained using 1-day batch sizes. Also shown are
the maneuver times. At early times the annual term is
largest. During Interval II, the interval of the large spin-
rate change anomaly, coherent oscillation is lost. During
Interval III the oscillation is smaller and begins to die
out.
In attempts to understand the nature of this annual
term, we ﬁrst examined a number of possible sources, in-
cluding eﬀects introduced by imprecise modeling of ma-
neuvers, the solar corona, and the Earth’s troposphere.
FIG. 17: ODP 1-day batch-sequential acceleration residual s
using the entire Pioneer 10 data set. Maneuver times are
indicated by the vertical dashed lines.
We also looked at the inﬂuence of the data editing strate-
gies that were used. We concluded that these eﬀects
could not account for the annual term.
Then, given that the eﬀect is particularly large in the
out-of-the-ecliptic voyage of Pioneer 11 [13], we focused
on the possibility that inaccuracies in solar system mod-
eling are the cause of the annual term in the Pioneer so-
lutions. In particular, we looked at the modeling of the
Earth orbital orientation and the accuracy of the plane-
tary ephemeris.
g. Earth’s orientation: We speciﬁcally modeled the
Earth orbital elements ∆ p and ∆ q as stochastic parame-
ters. (∆ p and ∆ q are two of the Set III elements deﬁned
by Brouwer and Clemence [123].) Sigma was applied to
the entire Pioneer 10 data set with aP , ∆p, and ∆ q deter-
mined as stochastic parameters sampled at an interval of
ﬁve days and exponentially correlated with a correlation
time of 200 days. Each interval was ﬁt independently,
but with information on the spacecraft state (position
and velocity) carried forward from one interval to the
next. Various correlation times, 0-day, 30-day, 200-day,
and 400-day, were investigated. The a priori error and
process noise on ∆ p and ∆ q were set equal to 0, 5, and
10 µ rad in separate runs, but only the 10 µ rad case re-
moved the annual term. This value is at least three orders
of magnitude too large a deviation when compared to
the present accuracy of the Earth orbital elements. It is
most unlikely that such a deviation is causing the annual
term. Furthermore, changing to the latest set of EOP
has very little eﬀect on the residuals. [We also looked
at variations of the other four Set III orbital elements,
essentially deﬁning the Earth’s orbital shape, size, and
longitudinal phase angle. They had little or no eﬀect on
the annual term.]
h. Solar system modeling: We concentrated on In-
terval III, where the spin anomaly is at a minimum and
where aP is presumably best determined. Further, this
data was partially taken after the DSN’s Block 5 hard-

## Page 41

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

## Page 42

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

## Page 43

43
TABLE II: Error Budget: A Summary of Biases and Uncertaintie s.
Item Description of error budget constituents Bias Uncerta inty
10− 8 cm/ s2 10− 8 cm/ s2
1 Systematics generated external to the spacecraft:
a) Solar radiation pressure and mass +0 . 03 ±0. 01
b) Solar wind ± < 10− 5
c) Solar corona ±0. 02
d) Electro-magnetic Lorentz forces ± < 10− 4
e) Inﬂuence of the Kuiper belt’s gravity ±0. 03
f) Inﬂuence of the Earth orientation ±0. 001
g) Mechanical and phase stability of DSN antennae ± < 0. 001
h) Phase stability and clocks ± < 0. 001
i) DSN station location ± < 10− 5
j) Troposphere and ionosphere ± < 0. 001
2 On-board generated systematics:
a) Radio beam reaction force +1 . 10 ±0. 11
b) RTG heat reﬂected oﬀ the craft −0. 55 ±0. 55
c) Diﬀerential emissivity of the RTGs ±0. 85
d) Non-isotropic radiative cooling of the spacecraft ±0. 48
e) Expelled Helium produced within the RTGs +0 . 15 ±0. 16
f) Gas leakage ±0. 56
g) Variation between spacecraft determinations +0 . 17 ±0. 17
3 Computational systematics:
a) Numerical stability of least-squares estimation ±0. 02
b) Accuracy of consistency/model tests ±0. 13
c) Mismodeling of maneuvers ±0. 01
d) Mismodeling of the solar corona ±0. 02
e) Annual/diurnal terms ±0. 32
Estimate of total bias/error +0 . 90 ±1. 33
The eﬀect is clearly signiﬁcant and remains to be ex-
plained.
XI. POSSIBLE PHYSICAL ORIGINS OF THE
SIGNAL
A. A new manifestation of known physics?
With the anomaly still not accounted for, possible ef-
fects from applications of known physics have been ad-
vanced. In particular, Crawford [126] suggested a novel
new eﬀect: a gravitational frequency shift of the radio
signals that is proportional to the distance to the space-
craft and the density of dust in the intermediate medium.
In particular, he has argued that the gravitational inter-
action of the S-band radio signals with the interplanetary
dust may be responsible for producing an anomalous ac-
celeration similar to that seen by the Pioneer spacecraft.
The eﬀect of this interaction is a frequency shift that
is proportional to the distance and the square root of
the density of the medium in which it travels. Similarly,
Didon, Perchoux, and Courtens [127] proposed that the
eﬀect comes from resistance of the spacecraft antennae as
they transverse the interplanetary dust. This is related
to more general ideas that an asteroid or comet belt,
with its associated dust, might cause the eﬀect by gravi-
tational interactions (see Section VII E) or resistance to
dust particles.
However, these ideas have problems with known prop-
erties of the interplanetary medium that were outlined in
Section VII E. In particular, infrared observations rule
out more than 0.3 Earth mass from Kuiper Belt dust in
the trans-Neptunian region [98, 99]. Ulysses and Galileo
measurements in the inner solar system ﬁnd very few dust
grains in the 10 − 18 − 10− 12 kg range [128]. The density
varies greatly, up and down, within the belt (which pre-
cludes a constant force) and, in any event, the density is
not large enough to produce a gravitational acceleration
on the order of aP [95]-[97].

## Page 44

44
One can also speculate that there is some unknown in-
teraction of the radio signals with the solar wind. An
experimental answer could be given with two diﬀerent
transmission frequencies. Although the main communi-
cation link on the Ulysses mission is S-up/X-down mode,
a small fraction of the data is S-up/S-down. We had
hoped to utilize this option in further analysis. However,
using them in our attempt to study a possible frequency
dependent nature of the anomaly, did not provide any
useful results. This was in part due to the fact that X-
band data (about 1.5 % of the whole data available) were
taken only in the close proximity to the Sun, thus pro-
hibiting the study of a possible frequency dependence of
the anomalous acceleration.
B. Dark matter or modiﬁed gravity?
It is interesting to speculate on the unlikely possibility
that the origin of the anomalous signal is new physics
[129]. This is true even though the probability is that
some “standard physics” or some as-yet-unknown sys-
tematic will be found to explain this “acceleration.” The
ﬁrst paradigm is obvious. “Is it dark matter or a modiﬁ-
cation of gravity?” Unfortunately, neither easily works.
If the cause is dark matter, it is hard to understand. A
spherically-symmetric distribution of matter which goes
as ρ ∼ r− 1 produces a constant acceleration inside the
distribution. To produce our anomalous acceleration
even only out to 50 AU would require the total dark
matter to be greater than 3 × 10− 4M⊙ . But this is in
conﬂict with the accuracy of the ephemeris, which allows
only of order a few times 10 − 6M⊙ of dark matter even
within the orbit of Uranus [8]. (A 3-cloud neutrino model
also did not solve the problem [130].)
Contrariwise, the most commonly studied possible
modiﬁcation of gravity (at various scales) is an added
Yukawa force [131]. Then the gravitational potential is
V (r) = − GM m
(1 + α )r
[
1 + αe − r/λ
]
, (55)
where α is the new coupling strength relative to Newto-
nian gravity, and λ is the new force’s range. Since the
radial force is Fr = −drV (r) = ma, the power series for
the acceleration yields an inverse-square term, no inverse -
r term, then a constant term. Identifying this last term
as the Pioneer acceleration yields
aP = − αa 1
2(1 + α )
r2
1
λ 2 , (56)
where a1 is the Newtonian acceleration at distance r1 = 1
AU. (Out to 65 AU there is no observational evidence of
an r term in the acceleration.) Eq. (56) is the solution
curve; for example, α = −1 × 10− 3 for λ = 200 AU.
It is also of interest to consider some of the recent pro-
posals to modify gravity, as alternatives to dark matter
[132]-[135]. Consider Milgrom’s proposed modiﬁcation
of gravity [135], where the gravitational acceleration of
a massive body is a ∝ 1/r 2 for some constant a0 ≪ a
and a ∝ 1/r for a0 ≫ a. Depending on the value of H,
the Hubble constant, a0 ≈ aP ! Indeed, as a number of
people have noted,
aH = cH → 8 × 10− 8 cm/ s2, (57)
if H = 82 km/s/Mpc.
Of course, there are (fundamental and deep) theoreti-
cal problems if one has a new force of the phenomenolog-
ical types of those above. Even so, the deep space data
piques our curiosity. In fact, Capozziello et al. [136] note
the Pioneer anomaly in their discussion of astrophysical
structures as manifestations of Yukawa coupling scales.
This ties into the above discussion.
However, any universal gravitational explanation for
the Pioneer eﬀect comes up against a hard experimen-
tal wall. The anomalous acceleration is too large to
have gone undetected in planetary orbits, particularly
for Earth and Mars. NASA’s Viking mission provided
radio-ranging measurements to an accuracy of about 12
m [137, 138]. If a planet experiences a small, anomalous,
radial acceleration, aA, its orbital radius r is perturbed
by
∆r = − l 6aA
(GM⊙ )4 → − r a A
aN
, (58)
where l is the orbital angular momentum per unit mass
and aN is the Newtonian acceleration at r. (The right
value in Eq. (58) holds in the circular orbit limit.)
For Earth and Mars, ∆ r is about −21 km and −76
km. However, the Viking data determines the diﬀerence
between the Mars and Earth orbital radii to about a 100
m accuracy, and their sum to an accuracy of about 150
m. The Pioneer eﬀect is not seen.
Further, a perturbation in r produces a perturbation
to the orbital angular velocity of
∆ω = 2l aA
GM⊙
→ 2 ˙θ a A
aN
. (59)
The determination of the synodic angular velocity ( ω E −
ω M ) is accurate to 7 parts in 10 11, or to about 5 ms accu-
racy in synodic period. The only parameter that could
possibly mask the spacecraft-determined aR is ( GM⊙ ).
But a large error here would cause inconsistencies with
the overall planetary ephemeris [8, 49]. [Also, there
would be a problem with the advance of the perihelion
of Icarus [139].]
We conclude that the Viking ranging data limit any
unmodeled radial acceleration acting on Earth and Mars
to no more than 0 . 1 × 10− 8 cm/s2. Consequently, if the
anomalous radial acceleration acting on spinning space-
craft is gravitational in origin, it is not universal. That
is, it must aﬀect bodies in the 1000 kg range more than
bodies of planetary size by a factor of 100 or more. This

## Page 45

45
would be a strange violation of the Principle of Equiva-
lence [140]. (Similarly, the ∆ ω results rule out the uni-
versality of the at time-acceleration model. In the age of
the universe, T , one would have atT 2/ 2 ∼ 0. 7 T .)
A new dark matter model was recently proposed by
Munyaneza and Viollier [141] to explain the Pioneer
anomaly. The dark matter is assumed to be gravitation-
ally clustered around the Sun in the form of a spherical
halo of a degenerate gas of heavy neutrinos. However, al-
though the resulting mass distribution is consistent with
constraints on the mass excess within the orbits of the
outer planets previously mentioned, it turns out that the
model fails to produce a viable mechanism for the de-
tected anomalous acceleration.
C. New suggestions stimulated by the Pioneer
eﬀect
Due to the fact that the size of the anomalous acceler-
ation is of order cH, where H is the Hubble constant (see
Eq. (57)), the Pioneer results have stimulated a number
of new physics suggestions. For example, Rosales and
S´ anchez-Gomez [142] propose that aP is due to a local
curvature in light geodesics in the expanding spacetime
universe. They argue that the Pioneer eﬀect represents
a new cosmological Foucault experiment, since the solar
system coordinates are not true inertial coordinates with
respect to the expansion of the universe. Therefore, the
Pioneers are mimicking the role that the rotating Earth
plays in Foucault’s experiment. Therefore, in this picture
the eﬀect is not a “true physical eﬀect” and a coordinate
transformation to the co-moving cosmological coordinate
frame would entirely remove the Pioneer eﬀect.
From a similar viewpoint, Guruprasad [143] ﬁnds ac-
commodation for the constant term while trying to ex-
plain the annual term as a tidal eﬀect on the physical
structure of the spacecraft itself. In particular, he sug-
gests that the deformations of the physical structure of
the spacecraft (due to external factors such as the eﬀec-
tive solar and galactic tidal forces) combined with the
spin of the spacecraft are directly responsible for the de-
tected annual anomaly. Moreover, he proposes a hypoth-
esis of the planetary Hubble’s ﬂow and suggests that Pio-
neer’s anomaly does not contradict the existing planetary
data, but supports his new theory of relativistically elas-
tic space-time.
Østvang [144] further exploits the fact that the grav-
itational ﬁeld of the solar system is not static with re-
spect to the cosmic expansion. He does note, however,
that in order to be acceptable, any non-standard expla-
nation of the eﬀect should follow from a general theoret-
ical framework. Even so, Østvang still presents quite a
radical model. This model advocates the use of an ex-
panded PPN-framework that includes a direct eﬀect on
local scales due to the cosmic space-time expansion.
Belayev [145] considers a Kaluza-Klein model in 5 di-
mensions with a time-varying scale factor for the com-
pactiﬁed ﬁfth dimension. His comprehensive analysis led
to the conclusion that a variation of the physical con-
stants on a cosmic time scale is responsible for the ap-
pearance of the anomalous acceleration observed in the
Pioneer 10/11 tracking data.
Modanese [146] considers the eﬀect of a scale-
dependent cosmological term in the gravitational ac-
tion. It turns out that, even in the case of a static
spherically-symmetric source, the external solution of hi s
modiﬁed gravitational ﬁeld equations contains a non-
Schwartzschild-like component that depends on the size
of the test particles. He argues that this additional term
may be relevant to the observed anomaly.
Mansouri, Nasseri and Khorrami [147] argue that there
is an eﬀective time variation in the Newtonian gravi-
tational constant that in turn may be related to the
anomaly. In particular, they consider the time evolution
of G in a model universe with variable space dimensions.
When analyzed in the low energy limit, this theory pro-
duces a result that may be relevant to the long-range
acceleration discussed here. A similar analysis was per-
formed by Sidharth [148], who also discussed cosmologi-
cal models with a time-varying Newtonian gravitational
constant.
Inavov [149] suggests that the Pioneer anomaly is pos-
sibly the manifestation of a superstrong interaction of
photons with single gravitons that form a dynamical
background in the solar system. Every gravitating body
would experience a deceleration eﬀect from such a back-
ground with a magnitude proportional to Hubble’s con-
stant. Such a deceleration would produce an observable
eﬀect on a solar system scale.
All these ideas produce predictions that are close to
Eq. (57), but they certainly must be judged against dis-
cussions in the following two subsections.
In a diﬀerent framework, Foot and Volkas [150], sug-
gest the anomaly can be explained if there is mirror mat-
ter of mirror dust in the solar system. this could pro-
duce a drag force and not violate solar-system mass con-
straints.
Several scalar-ﬁeld ideas have also appeared. Mbelek
and Lachi` eze-Rey [151] have a model based on a long-
range scalar ﬁeld, which also predicts an oscillatory de-
cline in aP beyond about 100 AU. This model does ex-
plain the fact that aP stays approximately constant for
a long period (recall that Pioneer 10 is now past 70 AU).
From a similar standpoint Calchi Novati et al. [152] dis-
cuss a weak-limit, scalar-tensor extension to the standard
gravitational model. However, before any of these pro-
posals can be seriously considered they must explain the
precise timing data for millisecond binary pulsars, i.e.,
the gravitational radiation indirectly observed in PSR
1913+16 by Hulse and Taylor [153]. Furthermore, there
should be evidence of a distance-dependent scalar ﬁeld if
it is uniformly coupled to ordinary matter.
Consoli and Siringo [154] and Consoli [155] consider the
Newtonian regime of gravity to be the long wavelength
excitation of a scalar condensate from electroweak sym-

## Page 46

46
metry breaking. They speculate that the self-interactions
of the condensate could be the origins of both Milgrom’s
inertia modiﬁcation [132, 135] and also of the Pioneer
eﬀect.
Capozziello and Lambiase [156] argue that ﬂavor os-
cillations of neutrinos in the Brans-Dicke theory of grav-
ity may produce a quantum mechanical phase shift of
neutrinos. Such a shift would produce observable eﬀects
on astrophysical/cosmological length and time scales. In
particular, it results in a variation of the Newtonian grav-
itational constant and, in the low energy limit, might be
relevant to our study.
Motivated by the work of Mannheim [133, 157], Wood
and Moreau [158] investigated the theory of conformal
gravity with dynamical mass generation. They argue
that the Higgs scalar is a feature of the theory that cannot
be ignored. In particular, within this framework they ﬁnd
one can reproduce the standard gravitational dynamics
and tests within the solar system, and yet the Higgs ﬁelds
may leave room for the Pioneer eﬀect on small bodies.
In summary, as highly speculative as all these ideas
are, it can be seen that at the least the Pioneer anomaly
is inﬂuencing the phenomenological discussion of modern
gravitational physics and quantum cosmology [159].
D. Phenomenological time models
Having noted the relationships aP = c a t of Eq. (16)
and that of Eq. (57), we were motivated to try to
think of any (purely phenomenological) “time” distor-
tions that might fortuitously ﬁt the CHASMP Pioneer
results shown in Figure 8. In other words, are Eqs. (57)
and/or (16) indicating something? Is there any evidence
that some kind of “time acceleration” is being seen?
The Galileo and Ulysses spacecraft radio tracking data
was especially useful. We examined numerous “time”
models searching for any (possibly radical) solution. It
was thought that these models would contribute to the
deﬁnition of the diﬀerent time scales constructed on the
basis of Eq. (6) and discussed in the Section IV B. The
nomenclature of the standard time scales [54]-[55] was
phenomenologically extended in our hope to ﬁnd a desir-
able quality of the trajectory solution for the Pioneers.
In particular we considered:
i) Drifting Clocks. This model adds a constant accel-
eration term to the Station Time ( ST) clocks, i.e., in the
ST-UTC (Universal Time Coordinates) time transforma-
tion. The model may be given as follows:
∆ST = STreceived − STsent → ∆ST + 1
2 aclocks ·∆ST2
(60)
where STreceived and STsent are the atomic proper times
of sending and receiving the signal by a DSN antenna.
The model ﬁt Doppler well for Pioneer 10, Galileo, and
Ulysses but failed to model range data for Galileo and
Ulysses.
ii) Quadratic Time Augmentation. This model adds a
quadratic-in-time augmentation to the TAI-ET (Interna-
tional Atomic Time – Ephemeris Time) time transforma-
tion, as follows
ET → ET + 1
2 aET ·ET2. (61)
The model ﬁts Doppler fairly well but range very badly.
iii) Frequency Drift. This model adds a constant fre-
quency drift to the reference S-band carrier frequency:
ν S− band(t) = ν 0
(
1 + afr.drift ·TAI
c
)
. (62)
The model also ﬁts Doppler well but again ﬁts range
poorly.
iv) Speed of Gravity . This model adds a “light time”
delay to the actions of the Sun and planets upon the
spacecraft:
vgrav = c
(
1 + asp.grav · |⃗ rbody − ⃗ rPioneer|
c2
)
. (63)
The model ﬁts Pioneer 10 and Ulysses well. But the
Earth ﬂyby of Galileo ﬁt was terrible, with Doppler resid-
uals as high as 20 Hz.
All these models were rejected due either to poor ﬁts
or to inconsistent solutions among spacecraft.
E. Quadratic in time model
There was one model of the above type that was espe-
cially fascinating. This model adds a quadratic in time
term to the light time as seen by the DSN station. Take
any labeled time Ta to be
Ta = ta − t0 → ta − t0 + 1
2 at
(
t2
a − t2
0
)
. (64)
Then the light time is
∆TAI = TAIreceived − TAIsent →
→ ∆TAI + 1
2 aquad ·
(
TAI2
received − TAI2
sent
)
. (65)
It mimics a line of sight acceleration of the spacecraft,
and could be thought of as an expanding space model.
Note that aquad aﬀects only the data. This is in contrast
to the at of Eq. (16) that aﬀects both the data and the
trajectory.
This model ﬁt both Doppler and range very well. Pi-
oneers 10 and 11, and Galileo have similar solutions al-
though Galileo solution is highly correlated with solar
pressure; however, the range coeﬃcient of the quadratic
is negative for the Pioneers and Galileo while positive for
Ulysses. Therefore we originally rejected the model be-
cause of the opposite signs of the coeﬃcients. But when
we later appreciated that the Ulysses anomalous accelera-
tion is dominated by gas leaks (see Section V D 2), which

## Page 47

47
makes the diﬀerent-sign coeﬃcient of Ulysses meaning-
less, we reconsidered it.
The fact that the Pioneer 10 and 11, Galileo, and
Ulysses are spinning spacecraft whose spin axis are pe-
riodically adjusted so as to point towards Earth turns
out to make the quadratic in time model and the con-
stant spacecraft acceleration model highly correlated and
therefore very diﬃcult to separate. The quadratic in time
model produces residuals only slightly ( ∼ 20%) larger
than the constant spacecraft acceleration model. How-
ever, when estimated together with no a priori input i.e.,
based only the tracking data, even though the correlation
between the two models is 0.97, the value aquad deter-
mined for the quadratic in time model is zero while the
value for the constant acceleration model aP remains the
same as before.
The orbit determination process clearly prefers the
constant acceleration model, aP , over that the quadratic
in time model, aquad of Eq. (65). This implies that a
real acceleration is being observed and not a pseudo ac-
celeration. We have not rejected this model as it may
be too simple in that the motions of the spacecraft and
the Earth may need to be included to produce a true
expanding space model. Even so, the numerical relation-
ship between the Hubble constant and aP , which many
people have observed (cf. Section XI C), remains an in-
teresting conjecture.
XII. CONCLUSIONS
In this paper we have discussed the equipment, theo-
retical models, and data analysis techniques involved in
obtaining the anomalous Pioneer acceleration aP . We
have also reviewed the possible systematic errors that
could explain this eﬀect. These included computational
errors as well as experimental systematics, from systems
both external to and internal to the spacecraft. Thus,
based on further data for the Pioneer 10 orbit determi-
nation (the extended data spans 3 January 1987 to 22
July 1998) and more detailed studies of all the systemat-
ics, we can now give a total error budget for our analysis
and a latest result of aP = (8. 74 ± 1. 33) × 10− 8 cm/s2.
This investigation was possible because modern radio
tracking techniques have provided us with the means
to investigate gravitational interactions to an accuracy
never before possible. With these techniques, relativis-
tic solar-system celestial mechanical experiments using
the planets and interplanetary spacecraft provide critica l
new information.
Our investigation has emphasized that eﬀects that pre-
viously thought to be insigniﬁcant, such as rejected ther-
mal radiation or mass expulsion, are now within (or near)
one order of magnitude of possible mission requirements.
This has unexpectedly emphasized the need to carefully
understand all systematics to this level.
In projects proposed for the near future, such as a
Doppler measurement of the solar gravitational deﬂection
using the Cassini spacecraft [160] and the Space Interfer-
ometry Mission [161], navigation requirements are more
stringent than those for current spacecraft. Therefore, al l
the eﬀects we have discussed will have to be well-modeled
in order to obtain suﬃciently good trajectory solutions.
That is, a better understanding of the nature of these
extra small forces will be needed to achieve the stringent
navigation requirements for these missions.
Currently, we ﬁnd no mechanism or theory that ex-
plains the anomalous acceleration. What we can say with
some conﬁdence is that the anomalous acceleration is a
line of sight constant acceleration of the spacecraft to-
ward the Sun [73]. Even though ﬁts to the Pioneers ap-
pear to match the noise level of the data, in reality the
ﬁt levels are as much as 50 times above the fundamental
noise limit of the data. Until more is known, we must ad-
mit that the most likely cause of this eﬀect is an unknown
systematic. (We ourselves are divided as to whether “gas
leaks” or “heat” is this “most likely cause.”)
The arguments for “gas leaks” are: i) All spacecraft
experience a gas leakage at some level. ii) There is enough
gas available to cause the eﬀect. iii) Gas leaks require no
new physics. However, iv) it is unlikely that the two
Pioneer spacecraft would have gas leaks at similar rates,
over the entire data interval, especially when the valves
have been used for so many maneuvers. [Recall also that
one of the Pioneer 11 thrusters became inoperative soon
after launch. (See Section II B.)] v) Most importantly,
it would require that these gas leaks be precisely pointed
towards the front [19] of the spacecraft so as not to cause
a large spin-rate changes. But vi) it could still be true
anyway.
The main arguments for “heat” are: i) There is so
much heat available that a small amount of the total
could cause the eﬀect. ii) In deep space the spacecraft
will be in approximate thermal equilibrium. The heat
should then be emitted at an approximately constant
rate, deviating from a constant only because of the slow
exponential decay of the Plutonium heat source. It is
hard to resist the notion that this heat somehow must
be the origin of the eﬀect. However, iii) there is no solid
explanation in hand as to how a speciﬁc heat mechanism
could work. Further, iv) the decrease in the heat supply
over time should have been seen by now.
Further experiment and analysis is obviously needed
to resolve this problem.
On the Pioneer 10 experimental front, there now exists
data up to July 2000. Further, there exists archived high-
rate data from 1978 to the beginning of our data arc in
Jan 1987 that was not used in this analysis. Because this
early data originated when the Pioneers were much closer
in to the Sun, greater eﬀort would be needed to perform
the data analyses and to model the systematics.
As Pioneer 10 continues to recede into interstellar
space, its signal is becoming dimmer. Even now, the
return signal is hard to detect with the largest DSN an-
tenna. However, with appropriate instrumentation, the
305-meter antenna of the Arecibo Observatory in Puerto

## Page 48

48
Rico will be able to detect Pioneer’s signal for a longer
time. If contact with Pioneer 10 can be maintained with
conscan maneuvers, such further extended data would be
very useful, since the spacecraft is now so far from the
Sun.
Other spacecraft can also be used in the study of aP .
The radio Doppler and range data from the Cassini mis-
sion could oﬀer a potential contribution. This mission
was launched on 15 October 1997. The potential data
arc will be the cruise phase from after the Jupiter ﬂyby
(30 December 2000) to the vicinity of Saturn (just before
the Huygens probe release) in July 2004. Even though
the Cassini spacecraft is in three-axis-stabilization mod e,
using on-board active thrusters, it was built with very so-
phisticated radio-tracking capabilities, with X-band be-
ing the main navigation frequency. (There will also be S-
and K-band links.) Further, during much of the cruise
phase, reaction wheels will be used for stabilization in-
stead of thrusters. Their use will aid relativity exper-
iments at solar conjunction and gravitational wave ex-
periments at solar opposition. (Observe, however, that
the relatively large systematic from the close in Cassini
RTGs will have to be accounted for.)
Therefore, Cassini could yield important orbit data, in-
dependent of the Pioneer hyperbolic-orbit data. A simi-
lar opportunity may exist, out of the plane of the ecliptic,
from the proposed Solar Probe mission. Under considera-
tion is a low-mass module to be ejected during solar ﬂyby.
On a longer time scale, the reconsidered Pluto/Kuiper
mission (with arrival at Pluto around 2029) could even-
tually provide high-quality data from very deep space.
All these missions might help test our current mod-
els of precision navigation and also provide a new test
for the anomalous aP . In particular, we anticipate that,
given our analysis of the Pioneers, in the future preci-
sion orbital analysis may concentrate more on systemat-
ics. That is, data/systematic modeling analysis may be
assigned more importance relative to the astronomical
modeling techniques people have concentrated on for the
past 40 years [162]-[164].
Finally, we observe that if no convincing explanation
is to be obtained, the possibility remains that the eﬀect
is real. It could even be related to cosmological quanti-
ties, as ha]s been intimated. [See Eq. (16) and Sec. XI,
especially the text around Eq. (57).] This possibility ne-
cessitates a cautionary note on phenomenology: At this
point in time, with the limited results available, there is
a phenomenological equivalence between the aP and at
points of view. But somehow, the choice one makes af-
fects one’s outlook and direction of attack. If one has to
consider new physics one should be open to both points
of view. In the unlikely event that there is new physics,
one does not want to miss it because one had the wrong
mind set.
Acknowledgments
Firstly we must acknowledge the many people who
have helped us with suggestions, comments, and con-
structive criticisms. Invaluable information on the his-
tory and status of Pioneer 10 came from Ed Batka,
Robert Jackson, Larry Kellogg, Larry Lasher, David
Lozier, and Robert Ryan. E. Myles Standish critically
reviewed the manuscript and provided a number of im-
portant insights, especially on time scales, solar system
dynamics and planetary data analysis. We also thank
John E. Ekelund, Jordan Ellis, William Folkner, Gene
L. Goltz, William E. Kirhofer, Kyong J. Lee, Margaret
Medina, Miguel Medina, Neil Mottinger, George W. Null,
William L. Sjogren, S. Kuen Wong, and Tung-Han You
of JPL for their aid in obtaining and understanding DSN
Tracking Data. Ralph McConahy provided us with very
useful information on the history and current state of the
DSN complex at Goldstone. R. Rathbun and A. Parker
of TR W provided information on the mass of the Pio-
neers. S. T. Christenbury of Teledyne-Brown, to whom
we are very grateful, supplied us with critical informa-
tion on the RTGs. Information was also supplied by
G. Reinhart of LANL, on the RTG fuel pucks, and by
C. J. Hansen of JPL, on the operating characteristics of
the Voyager image cameras. We thank Christopher S.
Jacobs of JPL for encouragement and stimulating dis-
cussions on present VLBI capabilities. Further guidance
and information were provided by John W. Dyer, Alfred
S. Goldhaber, Jack G. Hills, Timothy P. McElrath, Ir-
win I. Shapiro, Edward J. Smith, and Richard J. Terrile.
Edward L. Wright sent useful observations on the RTG
emissivity analysis. We also thank Henry S. Fliegel, Gary
B. Green, and Paul Massatt of The Aerospace Corpora-
tion for suggestions and critical reviews of the present
manuscript.
This work was supported by the Pioneer Project,
NASA/Ames Research Center, and was performed at
the Jet Propulsion Laboratory, California Institute of
Technology, under contract with the National Aeronau-
tics and Space Administration. P.A.L. and A.S.L. were
supported by a grant from NASA through the Ultravi-
olet, Visible, and Gravitational Astrophysics Program.
M.M.N. acknowledges support by the U.S. DOE.
Finally, the collaboration especially acknowledges the
contributions of our friend and colleague, Tony Liu, who
passed away while the manuscript was nearing comple-
tion.

## Page 49

49
APPENDIX A: APPENDIX
In Table III we give the hyperbolic orbital parame-
ters for Pioneer 10 and Pioneer 11 at epoch 1 January
1987, 01:00:00 UTC. The semi-major axis is a, e is the
eccentricity, I is the inclination, Ω is the longitude of the
ascending node, ω is the argument of the perihelion, M0
is the mean anomaly, f0 is the true anomaly at epoch,
and r0 is the heliocentric radius at the epoch. The direc-
tion cosines of the spacecraft position for the axes used
are ( α, β, γ ). These direction cosines and angles are re-
ferred to the mean equator and equinox of J2000. The
ecliptic longitude ℓ 0 and latitude b0 are also listed for an
obliquity of 23 ◦26
′
21.
′′
4119. The numbers in parentheses
denote realistic standard errors in the last digits.
TABLE III: Orbital parameters for Pioneer 10 and Pioneer
11 at epoch 1 January 1987, 01:00:00 UTC.
Parameter Pioneer 10 Pioneer 11
a [km] −1033394633(4) −1218489295(133)
e 1. 733593601(88) 2. 147933251(282)
I [Deg] 26. 2488696(24) 9. 4685573(140)
Ω [Deg] −3. 3757430(256) 35. 5703012(799)
ω [Deg] −38. 1163776(231) −221. 2840619(773)
M0 [Deg] 259. 2519477(12) 109. 8717438(231)
f0 [Deg] 112. 1548376(3) 81. 5877236(50)
r0 [km] 5985144906(22) 3350363070(598)
α 0. 3252905546(4) −0. 2491819783(41)
β 0. 8446147582(66) −0. 9625930916(22)
γ 0. 4252199023(133) −0. 1064090300(223)
ℓ 0 [Deg] 70. 98784378(2) −105. 06917250(31)
b0 [Deg] 3. 10485024(85) 16. 57492890(127)
[1] See the special issue of Science 183, No. 4122, 25 Jan-
uary 1974; speciﬁcally, J. D. Anderson, G. W. Null, and
S. K. Wong, Science 183, 322 (1974).
[2] R. O. Fimmel, W. Swindell, and E. Burgess, Pioneer
Odyssey: Encounter with a Giant , NASA document No.
SP-349 (NASA, Washington D.C., 1974).
[3] R. O. Fimmel, J. Van Allen, and E. Burgess, Pio-
neer: First to Jupiter, Saturn, and beyond , NASA re-
port NASA–SP-446 (NASA, Washington D.C., 1980).
[4] Pioneer F/G Project: Spacecraft Operational Character-
istics, Pioneer Project NASA/ARC document No. PC-
202 (NASA, Washington, D.C., 1971).
[5] Pioneer Extended Mission Plan , Revised, NASA/ARC
document No. PC-1001 (NASA, Washington, D.C.,
1994).
[6] For web summaries of Pioneer, go to:
http://quest.arc.nasa.gov/pioneer10,
http://spaceprojects.arc.nasa.gov/
Space
Projects/ pioneer/PNhome.html
[7] J. D. Anderson, E. L. Lau, K. Scherer, D. C. Rosen-
baum, and V. L. Teplitz, Icarus 131, 167 (1998).
[8] J. D. Anderson, E. L. Lau, T. P. Krisher, D. A. Dicus,
D. C. Rosenbaum, and V. L. Teplitz, Astrophys. J. 448,
885 (1995).
[9] K. Scherer, H. Fichtner, J. D. Anderson, and E. L. Lau,
Science 278, 1919 (1997).
[10] J. D. Anderson and B. Mashoon, Astrophys. J. 290, 445
(1985).
[11] J. D. Anderson, J. W. Armstrong, and E. L.Lau, Astro-
phys. J. 408, 287 (1993).
[12] J. D. Anderson, P. A. Laing, E. L. Lau, A. S. Liu, M. M.
Nieto, and S. G. Turyshev, Phys. Rev. Lett. 81, 2858
(1998). Eprint gr-qc/9808081.
[13] S. G. Turyshev, J. D. Anderson, P. A. Laing, E. L. Lau,
A. S. Liu, and M. M. Nieto, in: Gravitational Waves
and Experimental Gravity, Proceedings of the XVIIIth
Moriond Workshop of the Rencontres de Moriond , ed.
by J. Dumarchez and J. Tran Thanh Van (World Pub.,
Hanoi, 2000), pp. 481-486. Eprint gr-qc/9903024.
[14] There were four Pioneers built of this particular desig n.
After testing, the best components were placed in Pi-
oneer 10. (This is probably why Pioneer 10 has lasted
so long.) The next best were placed in Pioneer 11. The
third best were placed in the “proof test model.” Un-
til recently, the structure and many components of this
model were included in an exhibit at the National Air
and Space Museum. The other model eventually was
dismantled. We thank Robert Ryan of JPL for telling
us this.
[15] Figures given for the mass of the entire Pioneer package
range from under 250 kg to over 315 kg. However, we
eventually found that the total (“wet”) weight at launch
was 259 kg (571 lbs), including 36 kg of hydrazine (79.4
lbs). Credit and thanks for these numbers are due to
Randall Rathbun, Allen Parker, and Bruce A. Giles of
TR W, who checked and rechecked for us including going
to their launch logs. Consistent total mass with lower
fuel (27 kg) numbers were given by Larry Kellogg of
NASA/Ames. (We also thank V. J. Slabinski of USNO
who ﬁrst asked us about the mass.)
[16] Information about the gas usage is by this time diﬃcult
to ﬁnd or lost. During the Extended Mission the col-
laboration was most concerned with power to the craft.
The folklore is that most of Pioneer 11’s propellant was
used up going to Saturn and used very little for Pio-
neer 10. In particular, a Pioneer 10 nominal input mass
of 251.883 kg and a Pioneer 11 mass of 239.73 kg were
used by the JPL program and the Aerospace program
used 251.883 for both. The 251 number approximates
the mass lost during spin down, and the 239 number
models the greater fuel usage. These numbers were not
changed in the programs. For reference, we will use 241
kg, the mass with half the fuel used, as our number with
which to calibrate systematics.
[17] We take this number from Ref. [4], where the design,
boom-deployed moment of inertia is given as 433.9 slug
(ft)2 (= 588.3 kg m 2). This should be a little low since
we know a small amount of mass was added later in the

## Page 50

50
development. A much later order-of-magnitude number
770 kg m 2 was obtained with a too large mass [15, 16].
See J. A. Van Allen, Episodic Rate of Change in Spin
Rate of Pioneer 10, Pioneer Project Memoranda, 20
March 1991 and 5 April 1991. Both numbers are dom-
inated by the RTGs and magnetometer at the ends of
long booms.
[18] Conscan stands for conical scan. The receiving antenna
is moved in circles of angular size corresponding to one
half of the beam-width of the incoming signal. This pro-
cedure, possibly iterated, allows the correct pointing di-
rection of the antenna to be found. When coupled with
a maneuver, it can also be used to ﬁnd the correct point-
ing direction for the spacecraft antenna. The precession
maneuvers can be open-loop, for orientation towards or
away from Earth-pointing, or closed-loop, for homing on
the uplink radio-frequency transmission from the Earth.
[19] When a Pioneer antenna points toward the Earth, this
deﬁnes the “rear” direction on the spacecraft. The
equipment compartment placed on the other side of of
the antenna deﬁnes the “front” direction on the space-
craft. (See Figure 2.)
[20] SNAP 19 Pioneer F & G Final Report , Teledyne re-
port IESD 2873-172, June, 1973, tech. report No.
DOE/ET/13512-T1; DE85017964, gov. doc. # E 1.9,
and S. T. Christenbury, private communications.
[21] F. A. Russo, in: Proceedings of the 3rd RTG Working
Group Meeting (Atomic Energy Commission, Washing-
ton, DC, 1972), ed. by P. A. O’Rieordan, papers # 15
and 16.
[22] L. Lasher, Pioneer Project Manager, recently reminded
us (March 2000) that not long after launch, the electrical
power had decreased to about 155 W, and degraded
from there. [Plots of the available power with time are
available.]
[23] This is a “theoretical value,” which does not account fo r
inverter losses, line losses, and such. It is interesting to
note that at mission acceptance, the total “theoretical”
power was 175 Watts.
[24] We take the S-band to be deﬁned by the frequen-
cies 1.55-5.20 GHz. We take the X-band to be de-
ﬁned by the frequencies 5.20-10.90 GHz. It turns
out there is no consistent international deﬁnition of
these bands. The deﬁnitions vary from ﬁeld to ﬁeld,
with geography, and over time. The above deﬁnitions
are those used by radio engineers and are consistent
with the DSN usage. (Some detailed band deﬁnitions
can be found at http://www.eecs.wsu.edu/∼hudson/
Teaching/ee432/spectrum.htm.) [We especially thank
Ralph McConahy of DSN Goldstone on this point.]
[25] dBm is used by radio engineers as a measure of received
power. It stands for decibels in milliwatts.
[26] For a description of the Galileo mission see T. V. John-
son, C. M. Yeats, and R. Young, Space Sci. Rev. 60,
3–21 (1992). For a description of the trajectory design
see L. A. D’Amario, L. E. Bright, and A. A. Wolf, Space
Sci. Rev. 60, 22–78 (1992).
[27] The LGA was originally supposed to “trickle” down low-
rate engineering data. It was also to be utilized in case a
fault resulted in the spacecraft “saﬁng” and shifting to
a Sun-pointed attitude, resulting in loss of signal from
the HGA. [“Saﬁng” refers to a spacecraft entering the
so called “safe mode.” This happens in case of an emer-
gency when systems are shut down.]
[28] J. D. Anderson, P. B. Esposito, W. Martin, C. L. Thorn-
ton, and D. O. Muhleman, Astrophys. J. 200, 221
(1975).
[29] P. W. Kinman, IEEE Transactions on Microwave The-
ory and Techniques 40, 1199 (1992).
[30] For descriptions of the Ulysses mission see E. J. Smith
and R. G. Marsden, Sci. Am. 278, No. 1, 74 (1998); B.
M. Bonnet, Alexander von Humboldt Magazin, No. 72,
27 (1998).
[31] A technical description, with a history and pho-
tographs, of the Deep Space Network can be
found at http://deepspace.jpl.nasa.gov/dsn/. The
document describing the radio science system is
at http://deepspace.jpl.nasa.gov/dsndocs/810-5/
810-5.html.
[32] N. A. Renzetti, J. F. Jordan, A. L. Berman, J. A. Wack-
ley, T. P. Yunck, The Deep Space Network – An Instru-
ment for Radio Navigation of Deep Space Probes , Jet
Propulsion Laboratory Technical Report 82-102 (1982).
[33] J. A. Barnes, A. R. Chi, L. S. Cutler, D. J. Healey,
D. B. Leeson, T. E. McGunigal, J. A. Mullen, Jr., W. L.
Smith, R. L. Sydnor, R. F. C. Vessot, and G. M. R. Win-
kler, IEEE Transactions on Instrumentation and Mea-
surement 20, 105 (1971).
[34] R. F. C. Vessot, in: Experimental Gravitation , ed. B.
Bertotti, ( Academic Press, New York and London,
1974), p.111.
[35] O. J. Sovers, J. L. Fanselow, and C. S. Jacobs, Rev.
Mod. Phys., 70, 1393 (1998).
[36] One-way data refers to a transmission and reception,
only. Two-way data is a transmission and reception, fol-
lowed by a retransmission and reception at the original
transmission site. This would be, for example, a trans-
mission from a radio antenna on Earth to a spacecraft
and then a retransmission back from the spacecraft to
the same antenna. Three-way refers to the same as two-
way, except the ﬁnal receiving antenna is diﬀerent from
the original transmitting antenna.
[37] Much, but not all, of the data we used has been
archived. Since the Extended Pioneer Mission is com-
plete, the resources have not been available to properly
convert the entire data set to easily accessible format.
[38] The JPL and DSN convention for Doppler frequency
shift is (∆ ν )DSN = ν 0 − ν , where ν is the measured fre-
quency and ν 0 is the reference frequency. It is positive
for a spacecraft receding from the tracking station (red
shift), and negative for a spacecraft approaching the
station (blue shift), just the opposite of the usual con-
vention, (∆ν )usual = ν −ν 0. In consequence, the velocity
shift, ∆ v = v − v0, has the same sign as (∆ ν )DSN but the
opposite sign to (∆ ν )usual. Unless otherwise stated, we
will use the DSN frequency shift convention in this pa-
per. We thank Matthew Edwards for asking us about
this.
[39] As we will come to in Section XI D, this property al-
lowed us to test and reject several phenomenological
models of the anomalous acceleration that ﬁt Doppler
data well but failed to ﬁt the range data.
[40] D. L. Cain, JPL Technical Report (1966).
[41] T. D. Moyer, Mathematical Formulation of the Dou-
ble Precision Orbit Determination Program (DPODP) ,
Jet Propulsion Laboratory Technical Report 32-1527
(1971).
[42] T. D. Moyer, Formulation for Observed and Computed

## Page 51

51
Values of Deep Space Network (DSN) Data Types for
Navigation, JPL Publication 00-7 (October 2000).
[43] A. Gelb, ed. Applied Optimal Estimation (M.I.T. Press,
Cambridge, MA, 1974).
[44] D. O. Muhleman and J. D. Anderson, Astrophys. J.
247, 1093 (1981).
[45] Once in deep space, all major forces on the spacecraft
are gravitational. The Principle of Equivalence holds
that the inertial mass ( mI ) and the gravitational mass
(mG) are equal. This means the mass of the craft should
cancel out in the dynamical gravitational equations. As
a result, the people who designed early deep-space pro-
grams were not as worried as we are about having the
correct mass. When non-gravitational forces were mod-
eled, an incorrect mass could be accounted for by mod-
ifying other constants. For example, in the solar radia-
tion pressure force the eﬀective sizes of the antenna and
the albedo could take care of mass inaccuracies.
[46] J. D. Anderson, in: Experimental Gravitation , ed.
B. Bertotti (New York and London, Academic Press,
1974), p.163.
[47] J. D. Anderson, G. S. Levy, and N. A. Renzetti, “Appli-
cation of the Deep Space Network (DSN) to the testing
of general relativity,” in Relativity in Celestial Mechan-
ics and Astrometry, eds. J. Kovalevsky and V. A. Brum-
berg. (Kluwer Academic, Dordrecht, Boston, 1986), p.
329.
[48] X X Newhall, E. M. Standish, and J. G. Williams, As-
tron. Astrophys. 125, 150 (1983).
[49] E. M. Standish, Jr., X X Newhall, J. G. Williams, and
D. K. Yeomans, “Orbital ephemeris of the Sun, Moon,
and Planets,” in: Ref. [55], p. 279. Also see E. M. Stan-
dish, Jr. and R. W. Hellings, Icarus 80, 326 (1989).
[50] E. M. Standish, Jr., X X Newhall, J. G. Williams, and
W. M. Folkner, JPL Planetary and Lunar Ephemeris,
DE403/LE403, Jet Propulsion Laboratory Internal
IOM No. 314.10-127 (1995).
[51] C. M. Will, Theory and Experiment in Gravitational
Physics, (Rev. Ed.) (Cambridge University Press, Cam-
bridge, 1993).
[52] C. M. Will and K. Nordtvedt, Jr, Astrophys. J. 177,
757 (1972).
[53] F. E. Estabrook, Astrophys. J. 158, 81 (1969).
[54] T. D. Moyer, Parts. 1 and 2, Celest. Mech. 23, 33, 57
(1981).
[55] P. K. Seidelmann, ed., Explanatory Supplement to the
Astronomical Almanac (University Science Books, Mill
Valley, CA, 1992).
[56] C. Ma, E. F. Arias, T. M. Eubanks, A. L. Fey, A.-M.
Gontier, C. S. Jacobs, O. J. Sovers, B. A. Archinal, and
P. Charlot, Astron. J. 116, 516 (1998).
[57] A. Milani, A. M. Nobili, and P. Farinella, Non-
Gravitational Perturbations and Satellite Geodesy ,
(Adam Hilger, Bristol, 1987). See, especially, p. 125.
[58] J. M. Longuski, R. E. Todd, and W. W. K¨ onig, J. Guid-
ance, Control, and Dynamics, 15, 545 (1992).
[59] D.O. Muhleman, P.B. Esposito, and J. D. Anderson,
Astrophys. J. 211, 943 (1977).
[60] The propagation speed for the Doppler signal is the
phase velocity, which is greater than c. Hence, the neg-
ative sign in Eq. (8) applies. The ranging signal propa-
gates at the group velocity, which is less than c. Hence,
there the positive sign applies.
[61] B.-G. Anderssen and S. G. Turyshev, JPL Internal IOM
1998-0625, and references therein.
[62] M. K. Bird, H. Volland, M. P¨ atzold, P. Edenhofer ,
S. W. Asmar and J. P. Brenkle, Astrophys. J. 426, 373
(1994).
[63] The units conversion factor for A, B, C from m to cm − 3
is 2 Nc(S)/R ⊙ = 0. 01877, where Nc(S) = 1 . 240 × 104ν 2
is the S band (in MHz) critical plasma density, and R⊙
is the radius of the Sun.
[64] These values of parameters A, B, C were kindly pro-
vided to us by John E. Ekelund of JPL. They represent
the best solution for the solar corona parameters ob-
tained during his simulations of the solar conjunction
experiments that will be performed with the Cassini
mission spacecraft in 2001 and 2002.
[65] This model is explained and described at
http://science.msfc.nasa.gov/ssl/pad/solar/
predict.htm
[66] These come from the adjustment in the system of data
weights (inverse of the variance on each measurement)
for Mariner 6/7 range measurements. Private communi-
cation by Inter-oﬃce Memorandum from D. O. Muhle-
man of Caltech to P. B. Esposito of JPL, dated 7 July
1971.
[67] G. W. Null, E. L. Lau, E. D. Biller, and J. D. Anderson,
Astron. J. 86, 456 (1981).
[68] P. A. Laing, “Implementation of J2000.0 reference fram e
in CHASMP,” The Aerospace Corporation’s Internal
Memorandum # 91(6703)-1. January 28, 1991.
[69] J. H. Lieske, Astron. Astrophys. 73, 282 (1979). Also,
see FK5/J2000.0 for DSM Applications, Applied Tech-
nology Associates, 6 June 1985.
[70] E. M. Standish, Astron. Astrophys. 114, 297 (1982)
[71] J. Sherman and W. Morrison. Ann. Math. Stat. 21, 124
(1949)
[72] J. D. Anderson, Quarterly Report to NASA/Ames Re-
search Center, Celestial Mechanics Experiment, Pioneer
10/11, 22 July 1992. Also see the later quarterly report
for the period 1 Oct. 1992 to 31 Dec. 1992, dated 17
Dec. 1992, Letter of Agreement ARC/PP017. This last,
speciﬁcally, contains the present Figure 7.
[73] We only measure Earth-spacecraft Doppler frequency
and, as we will discuss in Sec. VIII A, the down link
antenna yields a conical beam of width 3.6 degrees at
half-maximum power. Therefore, between Pioneer 10’s
past and present (May 2001) distances of 20 to 78 AU,
the Earth-spacecraft line and Sun-spacecraft line are so
close that one can not resolve whether the force direc-
tion is towards the Sun or if the force direction is to-
wards the Earth. If we could have used a longer arc ﬁt
that started earlier and hence closer, we might have able
to separate the Sun direction from the Earth direction.
[74] A preliminary discussion of these results appeared in M .
M. Nieto, T. Goldman, J. D. Anderson, E. L. Lau, and
J. P´ erez-Mercader, in:Proc. Third Biennial Conference
on Low-Energy Antiproton Physics, LEAP’94 , ed. by
G. Kernel, P. Krizan, and M. Mikuz (World Scientiﬁc,
Singapore, 1995), p. 606. Eprint hep-ph/9412234.
[75] Since both the gravitational and radiation pressure
forces become so large close to the Sun, the anoma-
lous contribution close to the Sun in Figures 6 and 7 is
meant to represent only what anomaly can be gleaned
from the data, not a measurement.
[76] B. D. Tapley, in Recent Advances in Dynamical As-
tronomy, eds. B. D. Tapley and V. Szebehely (Reidel,

## Page 52

52
Boston, 1973), p.396.
[77] P. A. Laing, Thirty Years of CHASMP , Aerospace re-
port (in preparation).
[78] P. A. Laing, Software Speciﬁcation Document, Radio
Science Subsystem, Planetary Orbiter Error Analysis
Study Program (POEAS) , Jet Propulsion Laboratory
Technical Report DUK-5127-OP-D, 19 February 1981.
POEAS was originally developed to support the Mariner
Mars program.
[79] P. A. Laing and A. S. Liu. NASA Interim Technical
Report, Grant NAGW-4968, 4 October 1996.
[80] Galileo is less sensitive to either an aP - or an at = aP /c -
model eﬀect than the Pioneers. Pioneers have a smaller
solar pressure and a longer light travel time. Sensitivity
to a clock acceleration is proportional to the light travel
time squared.
[81] T. McElrath, private communication.
[82] T. P. McElrath, S. W. Thurman, and K. E. Criddle,
in Astrodynamics 1993 , edited by A. K. Misra, V. J.
Modi,R. Holdaway, and P. M. Bainum (Univelt, San
Diego CA, 1994), Ad. Astodynamical Sci. 85, Part II,
p. 1635, paper No. AAS 93-687.
[83] The gas leaks found in the Pioneers are about an or-
der of magnitude too small to explain aP . Even so, we
feel that some systematic or combination of systemat-
ics (such as heat or gas leaks) will likely explain the
anomaly. However, such an explanation has yet to be
demonstrated. We will discuss his point further in Sec-
tions VI and VIII.
[84] More information on the “Heliocentric Trajecto-
ries for Selected Spacecraft, Planets, and Comets,”
can be found at http://nssdc.gsfc.nasa.gov/space/
helios/heli.html.
[85] ODP/ Sigma took the Interval I/II boundary as 22 July
1990, the date of a maneuver. CHASMP took this
boundary date as 31 August 1990, when a clear anomaly
in the spin data was seen. We have checked, and these
choices produce less than one percent diﬀerences in the
results.
[86] J. A. Estefan, L. R. Stavert, F. M. Stienon, A. H. Tay-
lor, T. M. Wang, and P. J. Wolﬀ, Sigma User’s Guide.
Navigation Filtering/Mapping Program , JPL document
699-FSOUG/NA V-601 (Revised: 14 Dec. 1998).
[87] G. W. Null, Astron. J. 81, 1153 (1976).
[88] R. M. Georgevic, Mathematical model of the solar radi-
ation force and torques acting on the components of a
spacecraft, JPL Technical Memorandum 33-494 (1971).
[89] Data is available at http://www.ngdc.noaa.gov/stp/
SOLAR/IRRADIANCE/irrad.html
[90] For an ideal ﬂat surface facing the Sun, K = (α + 2ǫ) =
(1 + 2 µ + 2 ν ). α and ǫ are, respectively, the absorp-
tion and reﬂection coeﬃcients of the spacecraft’s sur-
face. ODP uses the second formulation in terms of reﬂec-
tivity coeﬃcients, ODP’s input µ and ν for Pioneer 10,
are obtained from design information and early ﬁts to
the data. (See the following paragraph.) These numbers
by themselves yield K′ = 1 . 71. When a ﬁrst (negative)
correction is made for the antenna’s parabolic surface,
K → 1. 66.
[91] There are complicating eﬀects that modify the ideal an-
tenna. The craft actually has multiple diﬀerent-shaped
surfaces (such as the RTGs), that are composed of dif-
ferent materials oriented at diﬀerent angles to the spin
axis, and which degrade with time. But far from the
Sun, and given M and A, the sum of all such correc-
tions can be subsumed, for our purposes, in an eﬀective
K. It is still expected to be of order 1.7.
[92] Eq. (25) is combined with information on the spacecraft
surface geometry and it’s local orientation to determine
the magnitude of its solar radiation acceleration as it
faces the Sun. As with other non-gravitational forces, an
incorrect mass in modeling the solar radiation pressure
force can be accounted for by modifying other constants
such as the eﬀective sizes of the antenna and the albedo.
[93] E. J. Smith, L. Davis, Jr., D. E. Jones, D. S. Colburn,
P. J. Coleman, Jr., P. Dyal, and C. P. Sonnett, Science
183, 306 (1974); ibid. 188, 451 (1975).
[94] This result was obtained from a limit for positive charg e
on the spacecraft [87]. No measurement dealt with neg-
ative charge, but such a charge would have to be pro-
portionally larger to have a signiﬁcant eﬀect.
[95] R. Malhotra, Astron. J. 110, 420 (1995); ibid. 111, 504
(1996).
[96] A. P. Boss and S. J. Peale, Icarus 27, 119 (1976).
[97] A. S. Liu, J. D. Anderson, and E. Lau, Proc. AGU (Fall
Meeting, San Francisco, 16-18 December 1996), paper
# SH22B-05.
[98] G. E. Backman, A. Dasgupta, and R. E. Stencel, Astro-
phys. J. 450, L35 (1995). Also see S. A. Stern, Astron.
Astrophys. 310, 999 (1996).
[99] V. L. Teplitz, S. A. Stern, J. D. Anderson, D. Rosen-
baum, R. J. Scalise, and P. Wentzler, Astrophys. J. 516,
425 (1999).
[100] J. D. Anderson, G. Giampieri, P. A. Laing, and E. L.
Lau, work in progress.
[101] R. F. C. Vessot, “Space experiments with high stabilit y
clocks,” in proceedings of the “Workshop on the Scien-
tiﬁc Applications of Clocks in Space,” (November 7-8,
1996. Pasadena, CA). Edited by L. Maleki. JPL Publi-
cation 97-15 (JPL, Pasadena, CA, 1997), p. 67.
[102] O. J. Sovers and C. S. Jacobs, Observational Model and
Parameter Partials for the JPL VLBI Parameter Es-
timation Software “MODEST” - 1996 , Jet Propulsion
Laboratory Technical Report 83-39, Rev. 6 (1996).
[103] J. I. Katz, Phys. Rev. Lett. 83, 1892 (1999).
[104] There is an intuitive way to understand this. Set up a
coordinate system at the closest axial point of an RTG
pair. Have the antenna be in the (+z,-x) direction, and
the RTG pair in the positive x direction. Then from the
RTGs the antenna is in 1/4 of a sphere (positive z and
negative x). The ‘antenna occupies about 1/3 of 180
degrees in azimuthal angle. Its form is the base part of
the parabola. Thus, it resembles a “ﬂat” triangle of the
same width, producing another factor of ∼ (1/ 2 − 2/ 3)
compared to the angular size of a rectangle. It occupies
of order (1/4-1/3) of the latitudinal-angle phase space
angle of 90 o. This yields a total reduction factor of ∼
(1/ 96 − 2/ 108), or about 1 to 2 %.
[105] The value of 1.5% is obtained by doing an explicit cal-
culation of the solid angle subtended by the antenna
from the middle of the RTG modules using the Pioneer’s
physical dimensions. V. J. Slabinski of USNO indepen-
dently obtained a ﬁgure of 1.6%.
[106] Our high estimate of 40 W is not compromised by im-
precise geometry. If the RTGs were completely in the
plane of the top of the dish, then the maximum factor
multiplying the 40 W directed power would be κ z = 1.
This would presume all the energy was reﬂected and/or

## Page 53

53
absorbed and re-emitted towards the rear of the craft.
(If the RTGs were underneath the antenna, then the
total factor could ideally go as high as ”2”, from adding
the RTG heat going out the opposite direction.) The
real situation is that the average sine of the latitudinal
angle up to the antenna from the RTGs is about 0.3.
This means that the heat gong out the opposite direc-
tion might cause an eﬀective factor κ z to go as high
as 1.3. However, the real reﬂection oﬀ of the antenna
is not straight backwards. It is closer to 45 o. The ab-
sorbed and re-emitted radiation is also at an angle to
the rotation axis, although smaller. (This does not even
consider reﬂected/reemitted heat that does not go di-
rectly backwards but rather bounces oﬀ of the central
compartment.) So, the original estimate of κ = 1 is a
good bound.
[107] J. D. Anderson, P. A. Laing, E. L. Lau, A. S. Liu, M. M.
Nieto, and S. G. Turyshev, Phys. Rev. Lett. 83, 1893
(1999).
[108] We acknowledge R. E. Slusher of Bell Labs for raising
this possibility.
[109] B. A. Smith, G. A. Briggs, G. E. Danielson, A. F.
Cook, II, M. E. Davies, G. E. Hunt, H. Masursky, L.
A. Soderblom, T. C. Owen, C. Sagan, and V. E. Suomi,
Space Sci. Rev. 21, 103 (1977).
[110] C. E. Kohlhase and P. A. Penzo, Space Sci. Rev. 21, 77
(1977).
[111] We are grateful to C. J. Hansen of JPL, who kindly
provided us with operational information on the Voy-
ager video cameras.
[112] B. A. Smith, L. A. Soderblom, D. Banﬁeld, C. Barnet,
T. Basilevsky, R. F. Beebe, K. Bollinger, J. M. Boyce,
A. Brahic, G. A. Briggs, R. H. Brown, C. Chyba, S.
A. Collins, T. Colvin, A. F. Cook, II, D. Crisp, S. K.
Croft, D. Cruikshank, J. N. Cuzzi, G. E. Danielson,
M. E. Davies, E. De Jong, L. Dones, D. Godfrey, J.
Goguen, I. Grenier, V. R. Haemmerle, H. Hammel, C.
J. Hansen, C. P. Helfenstein, C. Howell, G. E. Hunt, A.
P. Ingersoll, T. V. Johnson, J. Kargel, R. Kirk, D. I.
Kuehn, S. Limaye, H. Masursky, A. McEwen, D. Morri-
son, T. Owen, W. Owen, J. B. Pollack, C. C. Porco, K.
Rages, P. Rogers, D. Rudy, C. Sagan, J. Schwartz, E.
M. Shoemaker, M. Showalter, B. Sicardy, D. Simonelli,
J. Spencer, L. A. Sromovsky, C. Stoker, R. G. Strom,
V. E. Suomi, S. P. Synott, R. J. Terrile, P. Thomas, W.
R. Thompson, A. Verbiscer, and J. Veverka, Science
246, 1432 1989.
[113] E. M. Murphy, Phys. Rev. Lett. 83, 1890 (1999).
[114] J. D. Anderson, P. A. Laing, E. L. Lau, A. S. Liu, M.
M. Nieto, and S. G. Turyshev, Phys. Rev. Lett. 83,
1891 (1999).
[115] L. K. Scheﬀer, (a) eprint gr-qc/0106010, the original
modiﬁcation; (b) eprint gr-qc/0107092; (c) eprint gr-
qc/0108054.
[116] J. D. Anderson, P. A. Laing, E. L. Lau, M. M. Nieto,
and S. G. Turyshev, eprint gr-qc/0107022.
[117] These results were not treated for systematics, used d if-
ferent time-evolving estimation procedures, were done
by three separate JPL navigation specialists, separated
and smoothed by one of us [72], and deﬁnitely not ana-
lyzed with the care of our recent run (1987.0 to 1998.5).
In particular, the ﬁrst two Pioneer 11 points, included
in the early memos [72], were after Pioneer 11 encoun-
tered Jupiter and then was going back across the central
solar system to encounter Saturn.
[118] T. K. Keenan, R. A. Kent, and R. N. R. Milford, Data
Sheets for PMC Radioisotopic Fuel , Los Alamos Report
LA-4976-MS (1972), available from NTIS. We thank
Gary Reinhart for ﬁnding this data for us.
[119] Diagrams showing the receptacle and the bayonet cou-
pling connector were made by the Deutsch Company of
Banning, CA. (The O-ring was originally planned to be
silicon.) Diagrams of the receptacle as mounted on the
RTGs were made by Teledyne Isotopes (now Teledyne
Brown Engineering). Once again we gratefully acknowl-
edge Ted Christenbury for obtaining these documents
for us.
[120] In principle, many things could be the origin of some
spin down: structural deformations due to adjustments
or aging, thermal radiation, leakage of the helium from
the RTGs, etc. But in the case of Pioneer spacecraft
none of these provide an explanation for the spin his-
tory exhibited by the Pioneer 10, especially the large
unexpected changes among the Intervals I, II, and III.
[121] S. Herrick, Astodynamics (Van Nostrand Reinhold Co.,
London, New York, 1971-72). Vols. 1-2,
[122] We thank William Folkner of JPL for his assistance in
producing several test ﬁles and invaluable advice.
[123] D. Brouwer and G. M. Clemence, Methods of Celestial
Mechanics (Academic Press, New York, 1961).
[124] W.G. Melbourne, Scientiﬁc American 234, No. 6, 58
(1976).
[125] We thank E. Myles Standish of JPL, who encouraged
us to address in greater detail the nature of the an-
nual/diurnal terms seen in the Pioneer Doppler residu-
als. (This work is currently under way.) He also kindly
provided us with the accuracies from his internal JPL
solar system ephemeris, which is continually under de-
velopment.
new, soon to be published, solar system ephemeris.
[126] D. F. Crawford, eprint astro-ph/9904150.
[127] N. Didon, J. Perchoux, and E. Courtens, Universit´ e de
Montpellier preprint (1999).
[128] D. A. Gurnett, J. A. Ansher, W. S. Kurth, and L.
J. Granroth, Geophys. Res. Lett. 24, 3125 (1997); M.
Landgraf, K. Augustsson, E. Gr¨ un, and A. S. Gustafson,
Science 286, 239 (1999).
[129] Pioneer 10 data yielded another fundamental physics
result, a limit on the rest mass of the photon. See L.
Davis, Jr., A. S. Goldhaber, and M. M. Nieto, Phys.
Rev. Lett. 35, 1402 (1975).
[130] G. J. Stephenson, Jr., T. Goldman, and B. H. J. McKel-
lar, Int. J. Mod. Phys. A 13, 2765 (1998), hep-
ph/9603392.
[131] M. M. Nieto and T. Goldman, Phys. Rep. 205, 221
(1991); 216, 343 (1992), and references therein.
[132] J. Bekenstein and M. Milgrom, Astrophys. J. 286, 7
(1984); M. Milgrom and J. Bekenstein, in: Dark Matter
in the Universe , eds. J. Kormendy and G. R. Knapp
(Kluwer Academic, Dordrecht, Boston, 1987), p. 319;
M. Milgrom, La Recherche 19, 182 (1988).
[133] P. D. Mannheim, Astrophys. J. 419, 150 (1993). Also
see K. S. Wood and R. J. Nemiroﬀ, Astrophys. J. 369,
54 (1991).
[134] K. G. Begeman, A. H. Broeils, and R. H. Sanders, Mon.
Not. R. Astron. Soc. 249, 523 (1991); T. G. Breimer and
R. H. Sanders, Astron. Astrophys. 274, 96 (1993).
[135] M. Milgrom, Ann. Phys. (NY) 229, 384 (1994). Also see

## Page 54

54
astro-ph/0112069.
[136] S. Capozziello, S. De Martino, S. De Siena, and F. Il-
luminati, Mod. Phys. Lett. A 16, 693 (2001). Eprint
gr-qc/0104052. Also see eprint gr-qc/9901042.
[137] R. D. Reasenberg, I. I. Shapiro, P. E. MacNeil, R. B.
Goldstein, J. C. Breidenthal, J. P. Brenkle, D. L. Cain,
T. M. Kaufman, T. A. Komarek, and A. I. Zygielbaum,
Astrophys. J. 234, L219 (1979).
[138] J. D. Anderson, J. K. Campbell, R. F. Jurgens, E. L.
Lau, X X Newhall, M. A. Slade III, and E. M. Stan-
dish, Jr., in: Proceedings of the Sixth Marcel Grossmann
Meeting on General Relativity , Part A, ed. H. Sato and
T. Nakamura, (World Scientiﬁc, Singapore, 1992), p.
353.
[139] R. H. Sanders, private communication to M. Milgrom
(1998).
[140] The Principle of Equivalence ﬁgure of merit is aP /a N .
This is worse than for laboratory experiments (compar-
ing small objects) or for the Nordtvedt Eﬀect (large ob-
jects of planetary size) [51]. It again emphasizes that
the Earth and Mars do not change positions due to aP .
[141] F. Munyaneza and R. D. Viollier, eprint astro-
ph/9910566.
[142] J. L. Rosales and J. L. S´ anchez-Gomez, eprint gr-
qc/9810085.
[143] V. Guruprasad, eprints astro-ph/9907363, gr-
qc/0005014, gr-qc/0005090.
[144] D. Østvang, eprint gr-qc/9910054.
[145] W. B. Belayev, eprint gr-qc/9903016.
[146] G. Modanese, Nucl. Phys. B 556, 397 (1999). Eprint
gr-qc/9903085.
[147] R. Mansouri, F. Nasseri and M. Khorrami, Phys. Lett.
A 259,194 (1999). Eprint gr-qc/9905052.
[148] B. G. Sidharth, Nuovo Cim. B115, 151 (2000). Eprint
astro-ph/9904088.
[149] M. A. Ivanov, Gen. Rel. and Grav. 33, 479 (2001). eprint
astro-ph/0005084. Also see eprint gr-qc/0009043, a con-
tribution to the SIGRA V/2000 Congress.
[150] R. Foot and R. R. Volkas, Phys. Lett. B 517, 13 (2001).
Eprint gr-qc/0108051.
[151] J. P. Mbelek and M. Lachi` eze-Rey, eprint gr-
qc/9910105.
[152] S. Calchi Novati, S. Capozziello, and G. Lambiase,
Grav. Cosmol. 6, 173 (2000). Eprint astro-ph/0005104.
[153] R. A. Hulse and J. H. Taylor, Astrophys. J. 195, L51
(1975); J. H. Taylor and J. M. Weisberg, Astrophys. J.
253, 908 (1982).
[154] M. Consoli and F. Siringo, eprint hep-ph/9910372.
[155] M. Consoli, eprint hep-ph/0002098.
[156] S. Capozziello and G. Lambiase, Mod. Phys. Lett. A
14, 2193 (1999). Eprint gr-qc/9910026.
[157] P. D. Mannheim and D. Kazanas, Astrophys. J. 342,
635 (1989); P. D. Mannheim, Gen. Rel. Grav. 25, 697
(1993); P. D. Mannheim, Astrophys. J. 479, 659 (1997).
[158] J. Wood and W. Moreau, eprint gr-qc/0102056.
[159] O. Bertolami and F. M. Nunes, Phys. Lett. B 452, 108
(1999). Eprint hep-ph/9902439.
[160] L. Iess, G Giampieri, J. D. Anderson, and B. Bertotti,
Class. Quant. Grav. 16, 1487 (1999).
[161] R. Danner and S. Unwin, eds., SIM Interferom-
etry Mission: Taking the Measure of the Uni-
verse, NASA document JPL 400-811 (1999). Also see
http://sim.jpl.nasa.gov/
[162] The situation may be analogous to what happened
in the 1980’s to geophysical exploration. Mine and
tower gravity experiments seemed to indicate anoma-
lous forces with ranges on the order of km [163]. But
later analyses showed that the experiments had been so
precise that small inhomogeneities in the ﬁeld surveys
had introduced anomalies in the results at this newly
precise level [164]. But the very important positive out-
come was that geophysicists realized the point had been
reached where more precise studies of systematics were
necessary.
[163] F. D. Stacey, G. J. Tuck, G. J. Moore, S. C. Holding,
B. D. Goodwin, and R. Zhou, Rev. Mod. Phys. 59, 157
(1987); D. H. Eckhardt, C. Jekeli, A. R. Lazarewicz, A.
J. Romaides, and R. W. Sands, Phys. Rev. Lett. 60,
2567 (1988).
[164] Measurements were more often taken at easily accessi-
ble sites, such as roads, rather than at more inaccessi-
ble cites at diﬀerent heights, such as mountain sides or
marshes. See D. F. Bartlett and W. L. Tew, Phys. Rev.
D 40, 673 (1989); . ibid. , J. Geophys. Res. [Solid Earth
Planet] 95, 17363 (1990); C. Jekeli, D. H. Eckhardt, and
A. J. Romaides, Phys. Rev. Lett. 64, 1204 (1990). For
a review, see Section 4 of Ref. [131].

## Page 55

arXiv:gr-qc/0104064v5  10 Mar 2005
Study of the anomalous acceleration of Pioneer 10 and 11: Err ata
John D. Anderson, a Philip A. Laing, b Eunice L. Lau, a Anthony S. Liu, Michael Martin Nieto, d and Slava G. Turysheva
aJet Propulsion Laboratory, California Institute of Techno logy, Pasadena, CA 91109
bThe Aerospace Corporation, 2350 E. El Segundo Blvd., El Segu ndo, CA 90245-4691
cAstrodynamic Sciences, 2393 Silver Ridge Ave., Los Angeles , CA 90039
dTheoretical Division (MS-B285), Los Alamos National Labor atory,
University of California, Los Alamos, NM 87545
Electronic addresses: john.d.anderson@jpl.nasa.gov, Ph ilip.A.Laing@aero.org,
Eunice.L.Lau@jpl.nasa.gov, mmn@lanl.gov, turyshev@jpl .nasa.gov
(Dated: December 2, 2024)
We give the errata for this paper in both the arXiv [gr-qc/010 4064, version 4] and published
[Phys. Rev. D 65, 082004 (2002)] formats.
PACS numbers: 04.80.-y, 95.10.Eg, 95.55.Pe
Sec. I-C, p. (4), para. 4, line 6 (published version
only):
Delete “load sharing.”
Sec. IV-F, 3rd para. from end, p. (16), lines 3-4
(published version only)
Delete “the” in front of “JPL’s” and one of the two
successive “from”s.
Sec. VII-B, p. 28 (26), 4 lines below Eq. (25):
1.73 should be 1.37.
Sec. VII-B, p. 29 (27):
Line 2: Change f⊙ to f⊙ /c and v3 to v2.
Eq. (29): Change v3/c to v2.
Eq. (29): Change 1 .24 × 10− 13 to 4 .4 × 10− 11.
3 lines down: Change 10 − 5 to 10 − 3.
Table II, p. 43 (40), item 1. (b):
10− 5 should be 10 − 3.
Sec. XI-C, p. 44 (41), 4 lines below Eq. (57):
10− 3 should be 10 − 2.
Sec. XI-C, p. 45 (42), para. 7, line 1:
“Inavov” should be “Ivanov.”
Ref. [20], p. 49 (45):
“Mashoon” should be “Mashhoon.”
