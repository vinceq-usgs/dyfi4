# -*- coding: utf-8 -*-
"""

Cdi
---

:synopsis: Utilities to compute and manipulate intensity. Input is an entry or a list of entries inside an aggregated area, such as a UTM box, or ZIP code. For details, see: https://earthquake.usgs.gov/data/dyfi/background.php#app1

.. data:: cdiWeights

    A dict of the CDI calculation indices and their relative weights.

.. data:: cdiDamageValues

    An OrderedDict of damage values and which d_text strings correspond to those values.

"""

import math
from collections import OrderedDict

cdiWeights={'felt':5,'motion':1,'reaction':1,'stand':2,
            'shelf':5,'picture':2,'furniture':3,'damage':5}

cdiDamageValues=OrderedDict([
    (0,['_none']),
    (0.5,['_crackmin','_crackwindows']),
    (0.75,['_crackwallfew']),
    (1,['_crackwallmany','_crackwall','_crackfloor','_crackchim','_tilesfell']),
    (2,['_wall','_pipe','_win','_brokenwindows','_majoroldchim','_masonryfell']),
    (3,['_move','_chim','_found','_collapse','_porch','_majormodernchim','_tiltedwall'])
    ])

def calculate(pts):
    """

    :synopsis: Calculate the intensity for one entry, or list of entries.
    :param list pts: Single :py:obj:`entry` or list of entries in an aggregated area
    :returns: float

    If given a single entry instead of list, calculate the decimal intensity for that
    entry. Note that intensity is defined over an area, not a point. "Point" intensities
    should be used as estimates or debugging only.

    A computed value less than or equal to zero is considered intensity I (unfelt).
    A computed value greater than zero is considered at least intensity II (felt).
    Intensity is rounded off to the nearest 0.1 unit.

    """

    # Make a list, if not already one
    if not isinstance(pts,list):
        pts=[pts]

    totalByIndex={}
    for index in cdiWeights:
        indexTotal=0
        indexCount=0

        for entry in pts:

            if index=='damage' and 'd_text' in entry.__dict__:
                val=getDamageFromText(entry.d_text)

            elif index not in entry.__dict__:
                val=None

            else:
                val=entry.__dict__[index]

            # Indices with no value are not counted at all. They DO NOT have zero value!
            if val is None:
                 continue
            try:
                val=float(val)
            except ValueError:
                # Values might have additional text. Ignore it.
                if ' ' in val:
                    val=val.split(' ')[0]
                val=float(val)
            except TypeError:
                continue

            indexTotal+=val
            indexCount+=1


        if indexCount:
            totalByIndex[index]=indexTotal/indexCount

    cws=0
    for index in totalByIndex:
        cws += totalByIndex[index] * cdiWeights[index]


    if cws <= 0:
        return 1

    cdi=math.log(cws) * 3.3996 - 4.3781
    if cdi < 2:
        return 2

    return round(cdi,1)

def getDamageFromText(d_text):
    """

    :synopsis: Calculate the damage value given a damage string.
    :param list pts: A damage string, see :py:obj:`cdiDamageValues` for allowed values
    :returns: float

    """

    if d_text is None:
        return None

    damageTokens=d_text.split()
    damage=None
    for dval,dstrings in cdiDamageValues.items():
        for dstring in dstrings:
            if dstring in damageTokens:
                damage=dval
                continue

    return damage

