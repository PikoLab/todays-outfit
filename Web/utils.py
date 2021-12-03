from datetime import date

Y = 2020 # dummy leap year to allow input X-02-29 (leap day)
seasons = [('winter', (date(Y,  1,  1),  date(Y,  2, 29))), 
           ('spring', (date(Y,  3, 1),  date(Y,  5, 31))),
           ('summer', (date(Y,  6, 1),  date(Y,  8, 31))),
           ('autumn', (date(Y,  9, 1),  date(Y, 11, 30))),
           ('winter', (date(Y, 12, 1),  date(Y, 12, 31)))]

def get_season(posted_at):
    now = posted_at.replace(year=Y)
    return next(season for season, (start, end) in seasons if start <= now <= end)