#! /usr/local/bin/python3

"""
    Contains DYFI mail functionality.

"""
FROM='vinceq@usgs.gov'
DEFAULT_RECIPIENT='vinceq@usgs.gov'


def dyfimail(p):
    """

    :synopsis: Simple interface to send mail
    :params dict p: A dict of mail parameters
    :returns: None

    The `p` parameter uses the following keys:

        - subject
        - to
        - text

    Usage::

        from mail import dyfimail
        dyfimail({'subject':'x','to':'recipient','text':'body'})

    """

    msgsubj='DYFI Alert'
    msgfrom=FROM
    msgto=DEFAULT_RECIPIENT

    if 'subject' in p:
        msgsubj=p['subject']
    if 'to' in p:
        msgto=p['to']

    """
    msg=MIMEText(p['text'])
    msg['Subject']=msgsubj
    msg['From']=msgfrom
    msg['To']=msgto
    print('Sending:')
    print(msg)

    s=smtplib.SMTP('smtp.usgs.gov')
    s.set_debuglevel(1)
    s.send_message(msg)
    print(s)
    s.quit()
    """

    from subprocess import Popen,PIPE
    mailer=Popen(
        ['/bin/mail','-s',msgsubj,msgto],
        stdin=PIPE,universal_newlines=True
    )

    # Pending setup of mail in Travis, disable check for this.
    mailer.communicate(p['text']) # pragma: no cover

