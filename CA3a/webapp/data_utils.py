import statistics

import DBcm

from records import records


config = {
    "user": "swimuser",
    "password": "swimpasswd",
    "host": "localhost",
    "database": "swimdataDB",
}


def get_world_records(event):
    lcmen = records["LCMen"][event]
    lcwomen = records["LCWomen"][event]
    scmen = records["SCMen"][event]
    scwomen = records["SCWomen"][event]
    return lcmen, lcwomen, scmen, scwomen


# def get_swimmers_list():
#     SQL = "select name from swimmers"
#     with DBcm.UseDatabase(config) as db:
#         db.execute(SQL)
#         results = db.fetchall()  # a list of tuples.
#     names = [t[0] for t in results]  # a list of names.
#     return names


def get_swimmer_data(name, the_session):
    SQL = """  
        select distinct strokes.distance, strokes.stroke, swimmers.age
        from swimmers, strokes, times
        where times.swimmer_id = swimmers.id and
        times.stroke_id = strokes.id and
        swimmers.name = %s and
        date_format(times.ts, "%Y-%m-%d") = %s
    """
    with DBcm.UseDatabase(config) as db:
        db.execute(
            SQL,
            (
                name,
                the_session,
            ),
        )
        results = db.fetchall()  # a list of tuples.
    ## events = [t[0] + "-" + t[1] for t in results]  # a list of swimming events.
    return results


def get_chart_data(name, age, event, the_session):
    distance, stroke = event.split("-")
    SQL = """
        select swimmers.name, swimmers.age, times.time, strokes.distance, strokes.stroke, times.ts
        from swimmers, strokes, times
        where (swimmers.name = %s and swimmers.age = %s) and
        (strokes.distance = %s and strokes.stroke = %s) and 
        swimmers.id = times.swimmer_id and
        strokes.id = times.stroke_id and
        date_format(times.ts, "%Y-%m-%d") = %s
    """
    with DBcm.UseDatabase(config) as db:
        db.execute(
            SQL,
            (
                name,
                age,
                distance,
                stroke,
                the_session,
            ),
        )
        results = db.fetchall()
    times = [item[2] for item in results]
    converts = []  # This is an empty list.
    for t in times:
        if ":" in t:
            mins, the_rest = t.split(":")
            secs, hundredths = the_rest.split(".")  # Darius.
        else:
            mins = 0
            secs, hundredths = t.split(".")  # Dave.
        converts.append((int(mins) * 60 * 100) + (int(secs) * 100) + int(hundredths))
    average = statistics.mean(converts)
    mins = int((average // 60) // 100)
    remainder = average - (mins * 60 * 100)
    secs = int((remainder // 100))
    hundredths = int(round(remainder - (secs * 100), 0))
    average_str = f"{mins}:{secs}.{hundredths}"
    return average_str, times, converts


def get_list_of_sessions():
    SQL = "select distinct ts from times"
    with DBcm.UseDatabase(config) as db:
        db.execute(SQL)
        results = db.fetchall()
    return results


def get_swimmers_list_by_session(the_session):
    SQL = """
        select distinct swimmers.name   
        from times, swimmers 
        where date_format(times.ts, "%Y-%m-%d") = %s and     
        times.swimmer_id = swimmers.id 
        order by name ;
    """
    with DBcm.UseDatabase(config) as db:
        db.execute(SQL, (the_session,))
        results = db.fetchall()
        return [row[0] for row in results]
