# -*- coding: utf-8 -*-
"""

A collection of functions to compute and manipulate intensity. For details, see the :ref:`Scientific Guide`.

.. data:: cdiWeights

    A dict of the CDI calculation indices and their relative weights.

.. data:: cdiDamageValues

    An OrderedDict of damage values and the d_text strings correspond to those values.

"""

import math
from collections import OrderedDict

#cdiWeights={'felt':5,'motion':1,'reaction':1,'stand':2,
#            'shelf':5,'picture':2,'furniture':3,'damage':5}

cdiWeights=OrderedDict([
    ('felt',5),('motion',1),('reaction',1),('stand',2),
    ('shelf',5),('picture',2),('furniture',3),('damage',5)
])

cdiDamageValues=OrderedDict([
    (0,['_none']),
    (0.5,['_crackmin','_crackwindows']),
    (0.75,['_crackwallfew']),
    (1,['_crackwallmany','_crackwall','_crackfloor','_crackchim','_tilesfell']),
    (2,['_wall','_pipe','_win','_brokenwindows','_majoroldchim','_masonryfell']),
    (3,['_move','_chim','_found','_collapse','_porch','_majormodernchim','_tiltedwall'])
    ])

def calculate(entries,cwsOnly=False,fine=False,debug=False):
    """

    :synopsis: Calculate the intensity for one entry, or list of entries
    :param list entries: Single :py:class:`Entry` object or list of entries in an aggregated area
    :returns: float

    If given a single entry instead of list, calculate the decimal intensity for that entry.

    .. note:: Intensity is defined over an area, not a point. "Point intensities" should be used as estimates or for debugging only.

    A computed value less than or equal to zero is considered intensity I (unfelt).
    A computed value greater than zero is considered at least intensity II (felt).
    Intensity is rounded off to the nearest 0.1 unit.

    """

    # Make this into a list, if not already one
    if not isinstance(entries,list):
        entries=[entries]

    totalByIndex={}

    for index in cdiWeights:
        indexTotal=0
        indexCount=0

        for entry in entries:

            #----------------------------------------------
            # Special rules for 'damage' and 'other_felt'
            #----------------------------------------------
            if index=='damage':
                val=getDamageFromText(entry)

            elif index=='felt':
                val=getFeltFromOther(entry)

            else:
                val=entry.cdiIndex(index)

            subid=entry.subid

            # Indices with no value are not counted.
            # They DO NOT have zero value!
            if val is None:
                 continue

            indexTotal+=val
            indexCount+=1

        infoText=''
        if indexCount:
            totalByIndex[index]=indexTotal/indexCount
            infoText='%s/%s' % (totalByIndex[index],indexCount)

    cws=0
    for index in totalByIndex:
        cws += totalByIndex[index] * cdiWeights[index]

    if cwsOnly:
        returnVal=cws
        return returnVal

    cdi=1
    if cws<=0:
        returnVal=1

    else:
        cdi=math.log(cws)*3.3996-4.3781
        # This step is necessary for compatibility of DYFI3 and DYFI4 values
        cdi=float('%.4f' % cdi)

        if cdi<2:
            cdi=2

    if fine:
        returnVal=cdi

    else:
        returnVal=round(cdi,1)

    return returnVal


def getDamageFromText(entry):
    """

    :synopsis: Convert a damage string to a damage value
    :param entry: An `Entry` object or `str`
    :returns: float

    This function takes either an `Entry` object or an actual d_text string.
    Multiple damage strings (separated by whitespace) are allowed.

    """

    if isinstance(entry,str):
        d_text=entry

    else:
        d_text=entry.cdiIndex('d_text')

    if not d_text:
        return None

    damageTokens=d_text.split()
    damage=None
    for val,dstrings in cdiDamageValues.items():
        for dstring in dstrings:
            if dstring in damageTokens:
                damage=val
                break

    return damage


def getFeltFromOther(entry):
    """

    :synopsis: Return felt index value modified by other_felt
    :param entry: An `Entry` object
    :returns: float

    Returns a modified 'felt' value when 'other_felt' is entered.

    """

    felt=entry.cdiIndex('felt')
    other_felt=entry.cdiIndex('other_felt')

    if not other_felt or other_felt<2:
        return felt
    if other_felt==2 and not felt:
        return 0
    if other_felt==2:
        return 0.36
    if other_felt==3:
        return 0.72

    return 1

