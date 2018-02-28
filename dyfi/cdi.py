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

def calculate(entries,cwsOnly=False):
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

    # Make a list, if not already one
    if not isinstance(entries,list):
        entries=[entries]

    totalByIndex={}
    for index in cdiWeights:
        indexTotal=0
        indexCount=0

        for entry in entries:

            #----------------------------------------------
            # Special rules  for 'damage' and 'other_felt'
            #----------------------------------------------
            if index=='damage':
                val=getDamageFromText(entry)

            elif index=='felt':
                val=getFeltFromOther(entry)

            elif index not in entry.__dict__:
                val=None

            else:
                val=entry.__dict__[index]

            # Indices with no value are not counted.
            # They DO NOT have zero value!
            if val is None:
                 continue

            # Values might have additional text. Ignore it.
            if isinstance(val,str) and ' ' in val:
                    val=val.split(' ')[0]

            try:
                val=float(val)
            except ValueError:
                continue

            indexTotal+=val
            indexCount+=1

        if indexCount:
            totalByIndex[index]=indexTotal/indexCount

    cws=0
    for index in totalByIndex:
        cws += totalByIndex[index] * cdiWeights[index]

    if cwsOnly:
        return cws

    if cws <= 0:
        return 1

    cdi=math.log(cws) * 3.3996 - 4.3781
    if cdi < 2:
        return 2

    return round(cdi,1)


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
    elif 'd_text' not in entry.__dict__:
        return None
    elif entry.d_text==None or entry.d_text=='':
        return None
    else:
        d_text=entry.d_text

    damageTokens=d_text.split()
    damage=None
    for val,dstrings in cdiDamageValues.items():
        for dstring in dstrings:
            if dstring in damageTokens:
                damage=val
                continue

    return damage


def getFeltFromOther(entry):
    """

    :synopsis: Return felt index value modified by other_felt
    :param entry: An `Entry` object
    :returns: float

    Modifies the 'felt' index for this entry when a value for 'other_felt' is entered.

    """

    # Need to store felt index (in case it doesn't exist)
    if 'felt' not in entry.__dict__:
        myFelt=None
    else:
        myFelt=entry.felt

    if 'other_felt' not in entry.__dict__ or not entry.other_felt:
        return myFelt

    other_felt=entry.other_felt
    if other_felt==2 and not myFelt:
        return 0
    if other_felt==2:
        return 0.36
    if other_felt==3:
        return 0.72

    return 1

