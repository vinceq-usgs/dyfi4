# -*- coding: utf-8 -*-
"""

    A collection of IPEs for plotting and filtering. 

"""

import math

C = (0,0.309,1.864,-1.672,-0.00219,1.77,-0.383)

def aww2014wna(mag,r,inverse=False,fine=False):
    """

    :synopsis: Estimate intensity given magnitude and distance
    :param float mag: Magnitude
    :param float r: Epicentral distance
    :param bool inverse: Compute the inverse function
    :param bool fine: If false, intensities below 2 become 1
    :returns: Intensity


    Implementation of Atkinson, Worden, Wald (2014) for the Western North America region. See https://doi.org/10.1785/0120140178

    If `inverse` is true, then the first parameter is treated as intensity, and this returns the magnitude.

    """

    R=math.sqrt(r**2 + 14**2)
    B=max(0,math.log(R/50,10))

    logr = math.log(R,10) if R > 1 else 0

    if inverse:
        # For inverse problem, input is intensity, output is mag
        ii = mag
        mag = (ii - C[1] - C[3]*logr - C[4]*R - C[5]*B) / (C[2] + C[6]*logr)
        return mag

    mlogr = mag * logr
    ii = C[1] + C[2]*mag + C[3]*logr + C[4]*R + C[5]*B + C[6]*mlogr
    if not fine:
        if ii > 1.0 and ii < 2.0:
            ii = 2.0

    if ii < 1.0:
         ii = 1.0
    return ii


# Atkinson, Worden, and Wald 2014.
# See https://doi.org/10.1785/0120140178
def aww2014ena(mag,r,inverse=False,fine=False):
    """

    :synopsis: Estimate intensity given magnitude and distance
    :param float mag: Magnitude
    :param float r: Epicentral distance
    :param bool inverse: Compute the inverse function
    :param bool fine: If false, intensities below 2 become 1
    :returns: Intensity


    Implementation of Atkinson, Worden, Wald (2014) for the Eastern North America region. See https://doi.org/10.1785/0120140178

    If `inverse` is true, then the first parameter is treated as intensity, and this returns the magnitude.

    """

    R=math.sqrt(r**2 + 14**2)
    B=math.log(R/50,10)
    if B<0:
        B=0

    logr = math.log(R,10) if R > 1 else 0
    ecorr = 0.7 + 0.001*r + max(0,0.8*math.log(min(r,150)/50))

    if inverse:
        # For inverse problem, input is intensity, output is mag
        ii = mag
        mag = (ii - C[1] - ecorr - C[3]*logr - C[4]*R - C[5]*B) \
            / (C[2] + C[6]*logr)
        return mag

    mlogr = mag * logr
    ii = C[1] + C[2]*mag + C[3]*logr + C[4]*R + C[5]*B + C[6]*mlogr
    ii += ecorr

    if not fine:
        if ii>1.0 and ii<2.0:
            ii=2.0

    if ii < 1.0:
        ii=1.0
    return ii

aww2014wna.name = 'Atkinson, Worden, Wald 2014 (WNA)'
aww2014ena.name = 'Atkinson, Worden, Wald 2014 (ENA)'

