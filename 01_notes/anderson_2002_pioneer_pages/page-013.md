# Page 13

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
