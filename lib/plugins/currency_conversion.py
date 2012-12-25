# -*- coding: utf-8
""" currency conversion:

      provides an input preprocess that allows for currency conversions.
      query must match a regex that recognizes stuff like this:

        "10 lkr to usd"
        "100 eur to usd"
"""
import re
import urllib
import demjson

import IPython
import IPython.ipapi

from smashlib.util import report, do_it_later
from smashlib.smash_plugin import SmashPlugin

CODES = {"AED":"United Arab Emirates Dirham (AED)","ANG":"Netherlands Antillean Guilder (ANG)","ARS":"Argentine Peso (ARS)","AUD":"Australian Dollar (AUD)","BDT":"Bangladeshi Taka (BDT)","BGN":"Bulgarian Lev (BGN)","BHD":"Bahraini Dinar (BHD)","BND":"Brunei Dollar (BND)","BOB":"Bolivian Boliviano (BOB)","BRL":"Brazilian Real (BRL)","BWP":"Botswanan Pula (BWP)","CAD":"Canadian Dollar (CAD)","CHF":"Swiss Franc (CHF)","CLP":"Chilean Peso (CLP)","CNY":"Chinese Yuan (CNY)","COP":"Colombian Peso (COP)","CRC":"Costa Rican Colón (CRC)","CZK":"Czech Republic Koruna (CZK)","DKK":"Danish Krone (DKK)","DOP":"Dominican Peso (DOP)","DZD":"Algerian Dinar (DZD)","EEK":"Estonian Kroon (EEK)","EGP":"Egyptian Pound (EGP)","EUR":"Euro (EUR)","FJD":"Fijian Dollar (FJD)","GBP":"British Pound Sterling (GBP)","HKD":"Hong Kong Dollar (HKD)","HNL":"Honduran Lempira (HNL)","HRK":"Croatian Kuna (HRK)","HUF":"Hungarian Forint (HUF)","IDR":"Indonesian Rupiah (IDR)","ILS":"Israeli New Sheqel (ILS)","INR":"Indian Rupee (INR)","JMD":"Jamaican Dollar (JMD)","JOD":"Jordanian Dinar (JOD)","JPY":"Japanese Yen (JPY)","KES":"Kenyan Shilling (KES)","KRW":"South Korean Won (KRW)","KWD":"Kuwaiti Dinar (KWD)","KYD":"Cayman Islands Dollar (KYD)","KZT":"Kazakhstani Tenge (KZT)","LBP":"Lebanese Pound (LBP)","LKR":"Sri Lankan Rupee (LKR)","LTL":"Lithuanian Litas (LTL)","LVL":"Latvian Lats (LVL)","MAD":"Moroccan Dirham (MAD)","MDL":"Moldovan Leu (MDL)","MKD":"Macedonian Denar (MKD)","MUR":"Mauritian Rupee (MUR)","MVR":"Maldivian Rufiyaa (MVR)","MXN":"Mexican Peso (MXN)","MYR":"Malaysian Ringgit (MYR)","NAD":"Namibian Dollar (NAD)","NGN":"Nigerian Naira (NGN)","NIO":"Nicaraguan Córdoba (NIO)","NOK":"Norwegian Krone (NOK)","NPR":"Nepalese Rupee (NPR)","NZD":"New Zealand Dollar (NZD)","OMR":"Omani Rial (OMR)","PEN":"Peruvian Nuevo Sol (PEN)","PGK":"Papua New Guinean Kina (PGK)","PHP":"Philippine Peso (PHP)","PKR":"Pakistani Rupee (PKR)","PLN":"Polish Zloty (PLN)","PYG":"Paraguayan Guarani (PYG)","QAR":"Qatari Rial (QAR)","RON":"Romanian Leu (RON)","RSD":"Serbian Dinar (RSD)","RUB":"Russian Ruble (RUB)","SAR":"Saudi Riyal (SAR)","SCR":"Seychellois Rupee (SCR)","SEK":"Swedish Krona (SEK)","SGD":"Singapore Dollar (SGD)","SKK":"Slovak Koruna (SKK)","SLL":"Sierra Leonean Leone (SLL)","SVC":"Salvadoran Colón (SVC)","THB":"Thai Baht (THB)","TND":"Tunisian Dinar (TND)","TRY":"Turkish Lira (TRY)","TTD":"Trinidad and Tobago Dollar (TTD)","TWD":"New Taiwan Dollar (TWD)","TZS":"Tanzanian Shilling (TZS)","UAH":"Ukrainian Hryvnia (UAH)","UGX":"Ugandan Shilling (UGX)","USD":"US Dollar (USD)","UYU":"Uruguayan Peso (UYU)","UZS":"Uzbekistan Som (UZS)","VEF":"Venezuelan Bolívar (VEF)","VND":"Vietnamese Dong (VND)","XOF":"CFA Franc BCEAO (XOF)", "YER":"Yemeni Rial (YER)","ZAR":"South African Rand (ZAR)","ZMK":"Zambian Kwacha (ZMK)",}

CACHE = {}
ip = IPython.ipapi.get()
# matcher for stuff like 100 usd to eur, etc
PATTERN = re.compile('\d* \w\w\w to \w\w\w')
url_t = 'http://rate-exchange.appspot.com/currency?from={0}&to={1}'

def base_rate(c1, c2):
    """ returns base exchange rate between currency codes c1 and c2
        no point invalidating the cache; the shell isn't likely to
        be open that long.
    """
    c1, c2 = c1.lower(), c2.lower()
    if (c1,c2) not in CACHE:
        url = url_t.format(c1,c2)
        contents = urllib.urlopen(url).read()
        obj = demjson.decode(contents)
        try:             rate = obj['rate']
        except KeyError: raise Exception,obj
        else:            CACHE[(c1, c2)] = rate

    return CACHE[(c1,c2)]

def handler(line, mo):
    val,c1,_,c2 = filter(None, line.split())
    c11,c22 = CODES[c1.upper()],CODES[c2.upper()]
    report('running currency conversion from: {0} {1} to {2}'.format(val, c11, c22))
    rate = base_rate(c1, c2)
    result = float(val) * float(rate)
    report('retrieved base-rate: {0}'.format(rate))
    return 'smashlib.util.report("{0} {1}")'.format(result, c2.upper())



class Plugin(SmashPlugin):
    def install(self):
        meta = ip.meta
        def add_prefilter():
            try:
                meta.re_prefilters.append([PATTERN, handler])
            except AttributeError:
                report.ERROR("could not install currency-converter plugin.. "
                       "re_prefilter still not set")

        do_it_later(add_prefilter)
