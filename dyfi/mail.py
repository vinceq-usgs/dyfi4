#! /usr/local/bin/python3

#import smtplib
#from email.mime.text import MIMEText

FROM='vinceq@usgs.gov'
DEFAULT_RECIPIENT='vinceq@usgs.gov'


def dyfimail(p):
    """
Simple interface to send mail. Subject, to, and from have default
values which may be overridden.

Usage:
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


def main(args=None):
    import argparse

    parser=argparse.ArgumentParser(
        description='Access the DYFI main function.'
    )
    parser.add_argument('--subject',type=str,
                        help="Subject line")
    parser.add_argument(
        '--to',type=str,
        help="Recipient (default is DEFAULT_RECIPIENT)"
    )
    parser.add_argument('--text',type=str,
                        help="Body of message")

    args=parser.parse_args(args)

    p={}
    if args.subject:
        p['subject']=args.subject
    if args.to:
        p['to']=args.to
    p['text']=args.text
    dyfimail(p)


if __name__=='__main__':
    main(sys.argv[1:])  # pragma: no cover



