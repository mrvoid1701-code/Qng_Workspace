J/A+A/534/A109   MCXC Meta-Catalogue X-ray galaxy Clusters  (Piffaretti+, 2011)
================================================================================
The MCXC: a Meta-Catalogue of X-ray detected Clusters of galaxies.
    Piffaretti R., Arnaud M., Pratt G.W., Pointecouteau E., Melin J.-B.
   <Astron. Astrophys. 534, A109 (2011)>
   =2011A&A...534A.109P
================================================================================
ADC_Keywords: Clusters, galaxy ; X-ray sources ; Positional data ; Redshifts ;
              Combined data ; Cross identifications
Keywords: X-rays: galaxies: clusters - cosmology: observations -
          large-scale structure of Universe -
          galaxies: cluster: general - catalogs

Abstract:
    We present the compilation and properties of a meta-catalogue of X-ray
    detected clusters of galaxies, the MCXC. This very large catalogue is
    based on publicly available ROSAT All Sky Survey-based (NORAS, REFLEX,
    BCS, SGP, NEP, MACS, and CIZA) and serendipitous (160SD, 400SD, SHARC,
    WARPS, and EMSS) cluster catalogues. Data have been systematically
    homogenised to an overdensity of 500, and duplicate entries from
    overlaps between the survey areas of the individual input catalogues
    are carefully handled. The MCXC comprises 1743 clusters with virtually
    no duplicate entries. For each cluster the MCXC provides three
    identifiers, a redshift, coordinates, membership in the original
    catalogue, and standardised 0.1-2.4keV band luminosity L_500_, total
    mass M_500_, and radius R_500_. The meta-catalogue additionally
    furnishes information on overlaps between the input catalogues and the
    luminosity ratios when measurements from different surveys are
    available, and gives notes on individual objects.


File Summary:
--------------------------------------------------------------------------------
 FileName   Lrecl  Records   Explanations
--------------------------------------------------------------------------------
ReadMe         80        .   This file
mcxc.dat      323     1743   MCXC catalogue (table2 of the paper)
--------------------------------------------------------------------------------

See also:
        IX/10     : ROSAT All-Sky Bright Source Catalogue (1RXS) (Voges+ 1999)
        IX/15     : Einstein EMSS Survey (Gioia+ 1990, Stocke+ 1991)
        I/221     : The Magellanic Catalogue of Stars - MACS (Tucholke+ 1996)
 J/ApJS/129/435   : NORAS galaxy cluster survey. I. (Bohringer+, 2000)
 J/ApJ/580/774    : X-ray galaxy clusters behind the Milky Way (Ebeling+, 2002)
 J/ApJS/140/239   : RASS: clusters of galaxies around SGP (Cruddace+, 2002)
 J/MNRAS/301/881  : The ROSAT brightest cluster sample - I. (Ebeling+, 1998)
 J/MNRAS/318/333  : Extended ROSAT Bright Cluster Sample (Ebeling+ 2000)
 J/ApJS/162/304   : ROSAT NEP X-ray source catalog (Henry+, 2006)
 J/ApJ/594/154    : 160 square degree ROSAT survey (Mullis+, 2003)
 J/ApJS/172/561   : The 400d cluster Survey (Burenin+, 2007)
 J/ApJS/140/265   : WARPS survey. VI. (Perlman+, 2002)
 J/ApJS/176/374   : WARPS-II Cluster catalog. VII. (Horner+, 2008)
 J/A+A/425/367    : REFLEX Galaxy Cluster Survey catalogue (Boehringer+, 2004)
 J/ApJS/126/209   : Bright SHARC survey cluster catalog (Romer+, 2000)
 J/MNRAS/341/1093 : The Southern SHARC catalogue (Burke+, 2003)
 J/ApJS/140/265   : WARPS survey. VI. (Perlman+, 2002)
 J/ApJS/176/374   : WARPS-II Cluster catalog. VII. (Horner+, 2008)

Byte-by-byte Description of file: mcxc.dat
--------------------------------------------------------------------------------
   Bytes Format Units     Label     Explanations
--------------------------------------------------------------------------------
   1- 12  A12   ---       MCXC      MCXC name (JHHMM.m+DDMM)
  14- 31  A18   ---       OName     Other name
  33- 86  A54   ---       AName     Alternative name
  88- 89  I2    h         RAh       Right ascension (J2000)
  91- 92  I2    min       RAm       Right ascension (J2000)
  94- 97  F4.1  s         RAs       Right ascension (J2000)
      99  A1    ---       DE-       Declination sign (J2000)
 100-101  I2    deg       DEd       Declination (J2000)
 103-104  I2    arcmin    DEm       Declination (J2000)
 106-107  I2    arcsec    DEs       [0/60] Declination (J2000)
 109-115  F7.3  deg       RAdeg     Right ascension (J2000)
 117-123  F7.3  deg       DEdeg     Declination (J2000)
 125-131  F7.3  deg       GLON      Galactic longitude
 133-139  F7.3  deg       GLAT      Galactic latitude
 141-146  F6.4  ---       z         Redshift
 148-159  A12   ---       Cat       Catalogue name
 161-172  A12   ---       Sub-Cat   Sub-catalogue name
 174-178  F5.3 kpc/arcsec Scale     Scale
 180-188  F9.6  10+37W    L500      X-ray luminosity in 10^44^erg/s (1)
 190-196  F7.4 10+14Msun  M500      Total mass (1)
 198-204  F7.4  Mpc       R500      Characteristic radius (1)
 206-247  A42   ---       Notes     Notes (losStr = line of sight structure)
 249-260  A12   ---       Cat1      First overlapped catalog
 262-273  A12   ---       Cat2      Second overlapped catalog
 275-286  A12   ---       Cat3      Third overlapped catalog
 288-299  A12   ---       Cat4      Fourth overlapped catalog
 301-305  F5.3  ---       L500r1    ? Luminosity ratio L_500_/L_(500,MCXC)_
                                      for first catalogue overlapped
 307-311  F5.3  ---       L500r2    ? Luminosity ratio L_500_/L_(500,MCXC)_
                                      for second catalogue overlapped
 313-317  F5.3  ---       L500r3    ? Luminosity ratio L_500_/L_(500,MCXC)_
                                      for third catalogue overlapped
 319-323  F5.3  ---       L500r4    ? Luminosity ratio L_500_/L_(500,MCXC)_
                                      for fourth catalogue overlapped
--------------------------------------------------------------------------------
Note (1): the quantities are:
  * R500 is the radius within which the mean over-density of the cluster
    is 500 times the critical density at the cluster redshift.
  * L500 = a*Ltot, where a is the ratio L500/Ltot for a luminosity profile
    model based in the average gas density profile derived from the
    representative X-ray cluster sample REXCESS (2009A&A...498..361P)
  * M500 = 4/3{pi}*(R500)^3^*500{rho}_c_(z), where {rho}_c_(z) is the
    critical density ({rho}_c_(z)=3H(z)^2^).
--------------------------------------------------------------------------------

Acknowledgements:
     Rocco Piffaretti, rocco.piffaretti(at)cea.fr

History:
  * 05-Sep-2011: Original version
  * 12-Nov-2011: Missing declination sign "DE-" was fixed in 6 clusters
    J0458.9-0029 J1013.6-0054 J1013.7-0006 J1042.4-0008 J1415.2-0030
    J1516.5-0056; the Abell numbers have been homogenized in the
    "ANames" column as "ANNNN" or "SNNNN".
    (communicated by Heinz Andernach, Univ. Guanajuato, Mexico)

================================================================================
(End)                                        Patricia Vannier [CDS]  05-Sep-2011
