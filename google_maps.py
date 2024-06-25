import os
import googlemaps
from googlemaps.distance_matrix import distance_matrix

gmaps = googlemaps.Client(key=os.getenv('GMAPS_API_KEY'))


class Stop:
    def __init__(self, activity, hours, index):
        self.activity = activity
        self.gmaps_address = ""
        self.hours = hours
        self.time_str = ""
        self.set_time_str()
        self.index = index
        self.located = True

    def set_time_str(self):
        self.time_str = str(int(self.hours // 1)) + "hrs"
        mins = str(int((60 * (self.hours % 1)) // 1))
        if mins != "0":
            self.time_str += " " + mins + "min"


def get_stops(activities):
    stops = []
    i = 0
    for thing in activities:
        if thing.time_to_spend == "Less than 1 hour":
            hours = 1
        elif thing.time_to_spend == "1 to 2 hours":
            hours = 2
        elif thing.time_to_spend == "2 hours to Half Day":
            hours = 4
        elif thing.time_to_spend == "Half Day to Full Day":
            hours = 6
        elif thing.time_to_spend == "Full Day":
            hours = 8
        elif thing.time_to_spend == "More than Full Day":
            hours = 8
        else:
            hours = 0
        stop = Stop(thing, hours, i)
        if stop.activity.address[0].isnumeric():
            stop.gmaps_address = stop.activity.address.replace(" ", "+")
        else:
            stop.gmaps_address = stop.activity.name.replace(" ", "+")
        stops.append(stop)
        i += 1
    return stops


def get_distance_matrix(stops, city, mode):
    destinations = []
    for stop in stops:
        if stop.activity.address[0].isnumeric():
            destinations.append(stop.activity.address + city)
        else:
            destinations.append(stop.activity.name + ", " + city)
    matrix = []
    for origin in destinations:
        durations = []
        for dest in destinations:
            result = distance_matrix(gmaps, origins=[origin], destinations=[dest], mode=mode)
            try:
                durations.append(result['rows'][0]['elements'][0]['duration']['value'] / 3600)
            except KeyError:
                durations.append(1000)
        matrix.append(durations)
    return matrix


class Route:
    def __init__(self, stops, city, mode, create_matrix):
        self.stops = stops
        self.city = city
        self.all_located = True
        if create_matrix:
            self.matrix = get_distance_matrix(stops, city, mode)
            for i in range(len(self.matrix)):
                located = False
                for dist in self.matrix[i]:
                    if dist != 1000:
                        located = True
                self.stops[i].located = located
                if not located:
                    self.all_located = False
            for stop in self.stops:
                stop.gmaps_address += "," + self.city
        else:
            self.matrix = []
        self.trip_times = []

    def set_matrix(self, matrix):
        self.matrix = matrix

    def optimize(self):
        path = []
        trip = self.__get_shortest_trip()
        path.append(trip[0])
        path.append(trip[1])
        for i in range(1, len(self.stops)-1):
            option = self.__get_shortest_option(path, i)
            if option[0] == path[i]:
                path.append(option[1])
            else:
                path.insert(0, option[0])
        self.__resort(path)
        self.__set_trip_times()
        sum1 = 0
        for trip in self.trip_times:
            sum1 += trip
        path.reverse()
        self.__resort(path)
        self.__set_trip_times()
        sum2 = 0
        for trip in self.trip_times:
            sum2 += trip
        if sum1 < sum2:
            path.reverse()
            self.__resort(path)
            self.__set_trip_times()

    def reoptimize(self):
        path = []
        for i in range(len(self.stops) + 1):
            path.append(i)
        self.__resort(path)
        removed_index = -1
        for i in range(len(self.stops)):
            if removed_index == -1:
                if i != self.stops[i].index:
                    removed_index = i
                    self.stops[i].index = i
            else:
                self.stops[i].index = i
        self.matrix.pop(removed_index)
        for dists in self.matrix:
            dists.pop(removed_index)
        self.optimize()

    def __get_shortest_option(self, path, index):
        begin = path[0]
        finish = path[index]
        trip = [0, 0]
        val = 1000
        for start in range(len(self.matrix)):
            if start not in path:
                if self.matrix[start][begin] < val:
                    val = self.matrix[start][begin]
                    trip[0] = start
                    trip[1] = begin
        for end in range(len(self.matrix[finish])):
            if end not in path:
                if self.matrix[finish][end] < val:
                    val = self.matrix[finish][end]
                    trip[0] = finish
                    trip[1] = end
        return trip

    def __get_shortest_trip(self):
        length = len(self.matrix)
        trip = [0, 1]
        for start in range(length):
            for end in range(length):
                if start != end:
                    if self.matrix[start][end] < self.matrix[trip[0]][trip[1]]:
                        trip[0] = start
                        trip[1] = end
        return trip

    def __resort(self, path):
        new_stops = []
        for i in path:
            for stop in self.stops:
                if stop.index == i:
                    new_stops.append(stop)
        self.stops = new_stops

    def __set_trip_times(self):
        self.trip_times = [0]
        for i in range(1, len(self.stops)):
            start = self.stops[i-1].index
            end = self.stops[i].index
            self.trip_times.append(self.matrix[start][end])

    def get_route_time(self):
        total_hours = 0
        for stop in self.stops:
            total_hours += stop.hours
        for trip in self.trip_times:
            total_hours += trip
        return total_hours


class Day:
    def __init__(self, start, hours):
        self.start = start
        self.hours = hours
        self.busy_hours = ""
        self.time_str = ""
        self.start_str = ""

    def set_details(self, busy_hours):
        hrs = str(int(busy_hours // 1))
        mins = str(round(60 * (busy_hours % 1)))
        self.busy_hours = hrs + "hrs"
        if mins != "0":
            self.busy_hours += " " + mins + "min"
        start_str = str(int((self.start // 1) % 12)) + ":" + str(round(60 * (self.start % 1)))
        if self.start // 1 == 12:
            start_str = "12" + start_str[1:]
        if self.start < 10:
            self.start_str = "0" + start_str
            self.time_str = start_str + "am"
        else:
            self.start_str = start_str
            if self.start < 12:
                self.time_str = start_str + "am"
            else:
                self.time_str = start_str + "pm"
        if len(self.start_str) < 5:
            self.start_str = self.start_str[:-1] + "0" + self.start_str[-1]
            self.time_str = self.time_str[:-3] + "0" + self.time_str[-3:]
        self.time_str += " - "
        end_str = str(int(((self.start + self.hours) // 1) % 12)) + ":" + str(round(60 * ((self.start + self.hours) % 1)))
        if (self.start + self.hours) // 1 == 12:
            end_str = "12" + end_str[1:]
        self.time_str += end_str
        if self.time_str[-2] == ":":
            self.time_str = self.time_str[:-1] + "0" + self.time_str[-1]
        if self.start + self.hours < 12:
            self.time_str += "am"
        else:
            self.time_str += "pm"


class Schedule:
    def __init__(self, num_days, hours, start):
        self.num_days = num_days
        self.days = []
        for i in range(num_days):
            self.days.append(Day(start, hours))

    def set_days(self, days):
        self.days = days
        self.num_days = len(self.days)


class Vacation:
    def __init__(self, route):
        self.route = route
        self.schedule = None
        self.daily_routes = []
        self.daily_routes_trip_times = []
        self.unvisited_stops = []
        self.unlocated_stops = []
        self.description = ""
        self.key = gmaps.key
        self.map_links = []
        self.__plan()

    def __plan(self):
        if not self.route.all_located:
            self.__separate_located()
        self.__plan_without_schedule()
        self.__set_description(True)
        self.__optimize_time()
        self.__optimize_daily_routes()
        self.__set_schedule_details()

    def __replan(self, schedule):
        self.schedule = schedule
        self.daily_routes = []
        self.daily_routes_trip_times = []
        self.map_links = []
        self.unvisited_stops = []
        self.__plan_with_schedule()
        self.__set_description(False)
        self.__optimize_time()
        self.__optimize_daily_routes()
        self.__set_schedule_details()

    def remove_stop(self, name):
        for i in range(len(self.route.stops)):
            if name == self.route.stops[i].activity.name:
                self.route.stops.pop(i)
                break
        self.route.reoptimize()
        self.__replan(self.schedule)

    def remove_unlocated_stop(self, name):
        for i in range(len(self.unlocated_stops)):
            if name == self.unlocated_stops[i].activity.name:
                self.unlocated_stops.pop(i)
                break

    def adjust_stop(self, name, hours):
        for i in range(len(self.route.stops)):
            if self.route.stops[i].activity.name == name:
                self.route.stops[i].hours = hours
                self.route.stops[i].set_time_str()
        self.__replan(self.schedule)

    def adjust_unlocated_stop(self, name, hours):
        for i in range(len(self.unlocated_stops)):
            if self.unlocated_stops[i].activity.name == name:
                self.unlocated_stops[i].hours = hours
                self.unlocated_stops[i].set_time_str()

    def adjust_day(self, day, start_str, hours):
        start = float(start_str[0:2])
        if float(start_str[3:]) != 0:
            start += (float(start_str[3:]) / 60)
        self.schedule.days[day].start = start
        self.schedule.days[day].hours = hours
        self.__replan(self.schedule)

    def remove_day(self, day):
        days = []
        for i in range(self.schedule.num_days):
            if i != day:
                days.append(self.schedule.days[i])
        self.schedule.set_days(days)
        self.__replan(self.schedule)

    def add_day(self):
        self.schedule.days.append(Day(10, 9))
        self.schedule.set_days(self.schedule.days)
        self.__replan(self.schedule)

    def __separate_located(self):
        unlocated_index = []
        for stop in self.route.stops:
            if not stop.located:
                unlocated_index.append(stop.index)
        for index in unlocated_index:
            for i in range(len(self.route.stops)):
                if index == self.route.stops[i].index:
                    self.unlocated_stops.append(self.route.stops.pop(i))
                    self.route.reoptimize()
                    break

    def __plan_without_schedule(self):
        hours = 9
        stops = []
        stop_index = 0
        while stop_index < len(self.route.stops):
            if len(stops) == 0:
                time_for_stop = self.route.stops[stop_index].hours
            else:
                time_for_stop = self.route.trip_times[stop_index] + self.route.stops[stop_index].hours
            if time_for_stop <= hours:
                hours -= time_for_stop
                stops.append(self.route.stops[stop_index])
                stop_index += 1
            else:
                self.daily_routes.append(stops)
                stops = []
                hours = 9
        if len(stops) > 0:
            self.daily_routes.append(stops)
        schedule = Schedule(len(self.daily_routes), 9, 10)
        self.schedule = schedule

    def __plan_with_schedule(self):
        num_stops = len(self.route.stops)
        stop_index = 0
        for day in self.schedule.days:
            stops = []
            hours = day.hours
            if stop_index < num_stops:
                for i in range(stop_index, num_stops):
                    if len(stops) == 0:
                        time_for_stop = self.route.stops[i].hours
                    else:
                        time_for_stop = self.route.trip_times[i] + self.route.stops[i].hours
                    if time_for_stop <= hours:
                        hours -= time_for_stop
                        stops.append(self.route.stops[i])
                        stop_index += 1
                    else:
                        break
                self.daily_routes.append(stops)
            else:
                break
        if stop_index < num_stops:
            for i in range(stop_index, len(self.route.stops)):
                self.unvisited_stops.append(self.route.stops[i])
        else:
            for i in range(self.schedule.num_days - len(self.daily_routes)):
                self.daily_routes.append([])

    def __optimize_time(self):
        unused_time = []
        daily_index = 0
        for day in self.schedule.days:
            hours = day.hours
            for i in range(len(self.daily_routes[daily_index])):
                if i == 0:
                    hours -= self.daily_routes[daily_index][i].hours
                else:
                    hours -= self.route.matrix[self.daily_routes[daily_index][i-1].index][self.daily_routes[daily_index][i].index] + self.daily_routes[daily_index][i].hours
            daily_index += 1
            unused_time.append(hours)
        for stop in self.unvisited_stops:
            for i in range(self.schedule.num_days):
                time_for_stop = stop.hours
                if len(self.daily_routes[i]) > 0:
                    time_for_stop += self.route.matrix[self.daily_routes[i][-1].index][stop.index]
                if unused_time[i] >= time_for_stop:
                    unused_time[i] -= time_for_stop
                    self.daily_routes[i].append(stop)
                    self.unvisited_stops.remove(stop)
        broke = False
        for i in range(self.schedule.num_days - 1):
            for j in range(i + 1, self.schedule.num_days):
                if len(self.daily_routes[j]) > 0:
                    time_to_combine = self.schedule.days[j].hours - unused_time[j]
                    if len(self.daily_routes[i]) > 0:
                        time_to_combine += self.route.matrix[self.daily_routes[i][-1].index][self.daily_routes[j][0].index]
                    if unused_time[i] >= time_to_combine:
                        for stop in self.daily_routes[j]:
                            self.daily_routes[i].append(stop)
                        self.daily_routes[j] = []
                        if j != self.schedule.num_days - 1:
                            self.__optimize_time()
                            broke = True
                            break
            if broke:
                break

    def __optimize_daily_routes(self):
        for i in range(len(self.daily_routes)):
            stops = []
            matrix = []
            index = 0
            for stop in self.daily_routes[i]:
                dists = []
                for next_stop in self.daily_routes[i]:
                    dists.append(self.route.matrix[stop.index][next_stop.index])
                matrix.append(dists)
                new_stop = Stop(stop.activity, stop.hours, index)
                new_stop.gmaps_address = stop.gmaps_address
                stops.append(new_stop)
                index += 1
            daily_route = Route(stops, self.route.city, "driving", False)
            daily_route.set_matrix(matrix)
            daily_route.optimize()
            for j in range(len(daily_route.stops)):
                for orig_stop in self.daily_routes[i]:
                    if daily_route.stops[j].gmaps_address == orig_stop.gmaps_address:
                        daily_route.stops[j].index = orig_stop.index
            self.daily_routes[i] = daily_route.stops

    def __set_schedule_details(self):
        for i in range(self.schedule.num_days):
            hours = 0
            daily_trip_times = []
            num_stops = len(self.daily_routes[i])
            if num_stops == 1:
                map_link = "https://www.google.com/maps/embed/v1/place?key=" + self.key
            elif num_stops > 1:
                map_link = "https://www.google.com/maps/embed/v1/directions?key=" + self.key + "&mode=driving"
            else:
                map_link = "none"
            for j in range(num_stops):
                hours += self.daily_routes[i][j].hours
                if j != 0:
                    trip_time = self.route.matrix[self.daily_routes[i][j - 1].index][self.daily_routes[i][j].index]
                    hours += trip_time
                    daily_trip_times.append(round(60 * trip_time))
                else:
                    daily_trip_times.append(0)
                if num_stops == 1:
                    map_link += "&q=" + self.daily_routes[i][j].gmaps_address
                else:
                    if j == 0:
                        map_link += "&origin=" + self.daily_routes[i][j].gmaps_address
                    elif j == num_stops - 1:
                        map_link += "&destination=" + self.daily_routes[i][j].gmaps_address
                    elif j == 1:
                        map_link += "&waypoints=" + self.daily_routes[i][j].gmaps_address
                    else:
                        map_link += "|" + self.daily_routes[i][j].gmaps_address
            self.map_links.append(map_link)
            self.schedule.days[i].set_details(hours)
            self.daily_routes_trip_times.append(daily_trip_times)

    def __set_description(self, initialize):
        if initialize:
            self.description = "With the " + str(len(self.route.stops)) + " activities you chose to do in " + self.route.city
            self.description += ", we advise a " + str(self.schedule.num_days) + " day trip."
        else:
            self.description = "Your adjusted schedule results in a " + str(self.schedule.num_days) + "day trip visiting " + str(len(self.route.stops) - len(self.unvisited_stops)) + " activities."
            if len(self.unvisited_stops) > 0:
                self.description += "\n" + str(len(self.unvisited_stops)) + " stop(s) could not fit in your adjusted schedule."