
import pytz
import jdatetime
import datetime

local_tz = pytz.timezone('Asia/Tehran')


def utc_to_local(utc_dt):
    local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)
    return local_tz.normalize(local_dt)


def persian_conventer(date_time):
    date_time = utc_to_local(date_time)
    return jdatetime.datetime.fromgregorian(datetime=date_time)


def gregorian_converter(date_time):
    return jdatetime.datetime.togregorian(date_time)


def _date_time():
    return jdatetime.datetime.now(local_tz)
    # return datetime.datetime.now(local_tz)


def time():
    return jdatetime.datetime.now(local_tz).time()

# input persian datetime
def day(date_time=_date_time()) -> str:
    persianDays = ["شنبه", "يکشنبه", "دوشنبه",
                   "سه‏ شنبه", "چهارشنبه", "پنجشنبه", "جمعه"]

    print(date_time.weekday())

    return persianDays[date_time.weekday()]


def timedelta_subs(days, date_time=None):
    if date_time == None:
        date_time = datetime.datetime.utcnow()

    return date_time + datetime.timedelta(days)


def convert(**kwargs):
    return jdatetime.datetime(**kwargs).togregorian()


def convert_timedelta(duration):
    days, seconds = duration.days, duration.seconds
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = (seconds % 60)
    return {"days": days, "hours": hours, "minutes": minutes, "seconds": seconds}


def diff_datetimes(first_datetime, second_datetime):

    return first_datetime-second_datetime


# print(day())

# date = _date_time().now().strftime('%Y-%m-%d %H:%M')
# need_date = datetime.strptime(date, '%Y-%m-%d')
#

# print(_date_time())
# print(datetime.datetime.utcnow())
