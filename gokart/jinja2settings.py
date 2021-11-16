import pytz
from datetime import timedelta

def addDate(dt,days=0,hours=0,minutes=0,seconds=0):
    return dt + timedelta(days=days,hours=hours,minutes=minutes,seconds=seconds)

def formatDate(value,pattern=None,non_data="",timezone=None):
    if not value:
       return non_data or ""
    elif pattern:
        return value.astimezone(pytz.timezone(timezone)).strftime(pattern) if timezone else value.strftime(pattern)
    else:
        return "{}".format(value)


def format(value,pattern=None,non_data=""):
    if not value:
       return non_data or ""
    elif pattern:
        return pattern.format(value)
    else:
        return "{}".format(value)

def formatText(text,**context):
    if context:
        return text.format(**context)
    else:
        return text

filters={
    "addDate":addDate,
    "formatDate":formatDate,
    "format":format,
    "formatText":formatText,
}

def initValue(data=None):
    return [data]

def setValue(var,data=None):
    var[0] = data
    return ""

def getValue(var):
    return var[0]

globals={
    "initValue":initValue,
    "setValue":setValue,
    "getValue":getValue,
    
}

settings = {
    "filters":filters,
    "globals":globals
}

