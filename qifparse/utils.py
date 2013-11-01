# -*- coding: utf-8 -*-
from datetime import datetime


def parseQifDateTime(qdate):
    """ convert from QIF time format to ISO date string

    QIF is like   "7/ 9/98"  "9/ 7/99"  or   "10/10/99"  or "10/10'01" for y2k
         or, it seems (citibankdownload 20002) like "01/22/2002"
         or, (Paypal 2011) like "3/2/2011".
    ISO is like   YYYY-MM-DD  I think @@check
    """
    if qdate[1] == "/":
        qdate = "0" + qdate   # Extend month to 2 digits
    if qdate[4] == "/":
        qdate = qdate[:3]+"0" + qdate[3:]   # Extend month to 2 digits
    for i in range(len(qdate)):
        if qdate[i] == " ":
            qdate = qdate[:i] + "0" + qdate[i+1:]
    if len(qdate) == 10:  # new form with YYYY date
        iso_date = qdate[6:10] + "-" + qdate[3:5] + "-" + qdate[0:2]
        return datetime.strptime(iso_date, '%Y-%m-%d')
    if qdate[5] == "'":
        C = "20"
    else:
        C = "19"
    iso_date = C + qdate[6:8] + "-" + qdate[3:5] + "-" + qdate[0:2]
    return datetime.strptime(iso_date, '%Y-%m-%d')
