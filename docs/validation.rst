Validation
==========

.. testsetup::

     from dyfi import cdi
     from entries import Entry

Here we show a series of validation tests to show results consistent with
the algorithm as shown in:

      Utilization of the Internet for Rapid Community Intensity Maps
      David J. Wald  Vincent Quitoriano  Lori A. Dengler  James W. Dewey
      Seismological Research Letters (1999) 70 (6): 680-697
      DOI: https://doi.org/10.1785/gssrl.70.6.680

To calculate a DYFI intensity, we first assign numerical values to individual answers to each question in the questionnaire. For each "community" (i.e., geocoded block), the numerical values assigned to each questionnaire are averaged. A weighted sum of the community values for each question, the "Community Weighted Sum", is then computed based on the following equation::

      CWS = 5 x "felt" (0-1)
          + 1 x "motion" (0-5)
          + 1 x "reaction" (0-5)
          + 2 x "stand" (0-1)
          + 5 x "shelf" (0-3)
          + 2 x "picture" (0-1)
          + 5 x "damage" (0-3)

      (Numbers in parentheses are the range of possible values)

The intensity is then computed as::

      Intensity = |ln|(cws) * 3.3996 - 4.3781

.. |ln| replace:: log\ :sub:`e`

Test 1. An entry composed of a single 'I felt it' response, which results in a CWS of 5. 

      >>> entry=Entry({'felt':1})
      >>> cdi.calculate(entry,cwsOnly=True)
      5.0

For any 'felt' response, the minimum intensity is 2 (which corresponds to 'felt' on the MMI intensity scale).

      >>> cdi.calculate(entry)
      2

Test 2. For two entries 

