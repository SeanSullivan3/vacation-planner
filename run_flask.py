from flask import Flask, render_template, request

from google_maps import Route, get_stops, Vacation
from web_scraper import ThingToDo, find_things_to_do, get_list_of_cities

app = Flask(__name__)

city_list = get_list_of_cities()
chosen_city = ""
things_to_do = []
chosen_things_to_do = []
vacation = None


@app.route("/", methods=["GET", "POST"])
def display_city_selector():
    global chosen_city
    global things_to_do
    global chosen_things_to_do
    global vacation
    chosen_city = ""
    things_to_do = []
    chosen_things_to_do = []
    vacation = None
    return render_template("city_selector.html", city_list=city_list, error=False)


@app.route("/select_things_to_do", methods=["POST"])
def display_things_to_do():
    global chosen_city
    global things_to_do
    global chosen_things_to_do
    city = request.form.get("city")
    if chosen_city == "":
        things_to_do = find_things_to_do(city)
        if things_to_do[0].name != "not a listed city":
            chosen_city = city
        else:
            return render_template("city_selector.html", city_list=city_list, error=True, city=city)
    else:
        add_thing = request.form.get("add_thing")
        rm_thing = request.form.get("rm_thing")
        if add_thing is not None:
            chosen_thing = ThingToDo
            for thing in things_to_do:
                if thing.name == add_thing:
                    chosen_thing = thing
                    break
            things_to_do.remove(chosen_thing)
            chosen_things_to_do.insert(0, chosen_thing)
        elif rm_thing is not None:
            chosen_thing = ThingToDo
            for thing in chosen_things_to_do:
                if thing.name == rm_thing:
                    chosen_thing = thing
                    break
            chosen_things_to_do.remove(chosen_thing)
            things_to_do.insert(0, chosen_thing)
    return render_template("things_selector.html", city=chosen_city, things_to_do=things_to_do,
                           chosen_things_to_do=chosen_things_to_do, error=False)


@app.route("/route_details", methods=["POST"])
def display_route_details():
    global chosen_things_to_do
    global chosen_city
    global vacation
    if len(chosen_things_to_do) == 0:
        return render_template("things_selector.html", city=chosen_city, things_to_do=things_to_do,
                               chosen_things_to_do=chosen_things_to_do, error=True)
    error = False
    err_msg = ""
    if vacation is None:
        stops = get_stops(chosen_things_to_do)
        route = Route(stops, chosen_city, "driving", True)
        route.optimize()
        vacation = Vacation(route)
    else:
        rm_stop = request.form.get("rm_stop")
        rm_ul_stop = request.form.get("rm_ul_stop")
        adj_stop = request.form.get("adj_stop")
        adj_ul_stop = request.form.get("adj_ul_stop")
        adj_day = request.form.get("adj_day")
        rm_day = request.form.get("rm_day")
        add_day = request.form.get("add_day")
        if rm_stop is not None:
            if len(vacation.route.stops) != 1:
                check = request.form.get("rm_stop_check")
                if len(vacation.route.stops) == int(check):
                    vacation.remove_stop(rm_stop)
            else:
                error = True
                err_msg = "You can not remove your last activity. If you wish to reselect activities click \"Home\" in the navigation menu to restart."
        elif rm_ul_stop is not None:
            check = request.form.get("rm_stop_check")
            if len(vacation.unlocated_stops) == int(check):
                vacation.remove_unlocated_stop(rm_stop)
        elif adj_stop is not None:
            hours = float(request.form.get("stop-hours"))
            vacation.adjust_stop(adj_stop, hours)
        elif adj_ul_stop is not None:
            hours = float(request.form.get("stop-hours"))
            vacation.adjust_unlocated_stop(adj_stop, hours)
        elif adj_day is not None:
            start_str = request.form.get("day-start")
            hours = float(request.form.get("day-hours"))
            adj_day = int(adj_day)
            vacation.adjust_day(adj_day, start_str, hours)
        elif rm_day is not None:
            if vacation.schedule.num_days != 1:
                check = request.form.get("rm_day_check")
                if vacation.schedule.num_days == int(check):
                    vacation.remove_day(int(rm_day))
            else:
                error = True
                err_msg = "You can not remove the only day from your schedule. If you wish to reselect activities click \"Home\" in the navigation menu to restart."
        elif add_day is not None:
            check = request.form.get("add_day_check")
            if vacation.schedule.num_days == int(check):
                vacation.add_day()
    if len(vacation.unlocated_stops) > 0:
        error = True
        err_msg = "Unfortunately google maps could not retrieve the location data for some of your stops. These stops are displayed in \"Unlocated Activities\""
    return render_template("route_details.html", vacation=vacation, error=error, error_message=err_msg)


if __name__ == "__main__":
    app.run(debug=True)
