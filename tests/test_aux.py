# Tests of obsolete or not-yet-used functionality
# To run this test, you must be at the package root directory and run:
# pytest tests/test_aux.py

# This is necessary only when using "pytest.raises" tests
# import pytest

testid='ci37511872'
configfile='tests/testconfig.yml'

def test_aggregate():
    from dyfi import aggregate

    assert aggregate.myCeil(17,10)==20


def test_ipe():
    from dyfi import ipes

    func=ipes.aww2014wna # Test this ipe

    assert 8.3<func(7,0.1)<8.4
    assert func(3.5,50,fine=False)==2
    assert 6.3<func(7,10,inverse=True)<6.4

    func=ipes.aww2014ena # Test this ipe

    assert 9.0<func(7,0.1)<9.1
    assert func(2.5,100,fine=False)==2
    assert 5.8<func(7,10,inverse=True)<5.9


#def test_mail():
#    from dyfi import mail
#
#    sample=['--subject','test subject','--to','nobody','--text','test body']
#
#    # This looks for /bin/mail and should fail under Travis
#    with pytest.raises(FileNotFoundError) as exception:
#        mail.main(sample)
#    assert 'No such file or directory' in str(exception.value)


