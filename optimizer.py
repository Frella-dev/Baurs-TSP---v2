import math


def haversine(lat1, lon1, lat2, lon2):

    R = 6371

    lat1 = math.radians(float(lat1))
    lon1 = math.radians(float(lon1))
    lat2 = math.radians(float(lat2))
    lon2 = math.radians(float(lon2))

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        math.sin(dlat / 2) ** 2
        +
        math.cos(lat1)
        *
        math.cos(lat2)
        *
        math.sin(dlon / 2) ** 2
    )

    c = 2 * math.atan2(
        math.sqrt(a),
        math.sqrt(1 - a)
    )

    return R * c


def optimize_route(df, office_lat, office_lon):

    remaining = df.to_dict("records")

    route = []

    current_lat = office_lat
    current_lon = office_lon

    while remaining:

        nearest = min(
            remaining,
            key=lambda x: haversine(
                current_lat,
                current_lon,
                x["Latitude"],
                x["Longitude"]
            )
        )

        route.append(nearest)

        current_lat = nearest["Latitude"]
        current_lon = nearest["Longitude"]

        remaining.remove(nearest)

    return route


def split_daily(route, daily_km=160):

    days = []

    current_day = []

    current_distance = 0

    previous = None

    for stop in route:

        if previous is None:

            distance = 0

        else:

            distance = haversine(
                previous["Latitude"],
                previous["Longitude"],
                stop["Latitude"],
                stop["Longitude"]
            )

        if (
            current_distance + distance > daily_km
            and
            len(current_day) > 0
        ):

            days.append(current_day)

            current_day = []

            current_distance = 0

        current_day.append(stop)

        current_distance += distance

        previous = stop

    if current_day:

        days.append(current_day)

    return days


def cluster_then_split(df):

    OFFICE_LAT = 6.8275814230546725
    OFFICE_LON = 79.95698659415302

    route = optimize_route(
        df,
        OFFICE_LAT,
        OFFICE_LON
    )

    return split_daily(
        route,
        160
    )
