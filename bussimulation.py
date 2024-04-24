#RTD Bus Simulation
#CSCI 4203
#Created by: Koy Kubasta

import json
import random
from queue import PriorityQueue

def main():
    printBusArt()
    #parameter sweep from 80,000 to 120,000 riders per day by increments of 10k
    #   and time between buses from 10 minutes to 30 minutes by increments of 5m
    riders = 80000
    while (riders <= 120000):
        minutes = 10
        while (minutes <= 30):
            simulateDay(riders, minutes)
            minutes += 5
        riders += 10000


###########################################################
#Generates a list of riders for a day of bus ridership    #
#PARAMS:                                                  #
#   -n: Number of riders to generate                      #
#   -routes: A dictionary of route information, including #
#           the share of ridership each route makes up in #
#           in a given day.                               #
#RETURNS:                                                 #
#   -A list of riders, sorted by time each rider arrives  #
#      at the station.                                    #
###########################################################
def generateRiders(n, routes):
    riderList = []
    for i in range(n):
        riderList.append(generateRider(routes,i))

    riderList.sort()
    
    return riderList


###########################################################
#Generates a single rider                                 #
#PARAMS:                                                  #
#   -routes: A dictionary of route information, including #
#           the share of ridership each route makes up in #
#           in a given day.                               #
#   -riderNumber: int passed to give resulting tuple a    #
#           unique number to prevent collisions in the    #
#           priority queue                                #
#RETURNS:                                                 #
#   -A single Rider, containing start station,            #
#       end station, route, and time arrived at station   #
###########################################################
def generateRider(routes,riderNumber):
    rider = {}
    rider['id'] = riderNumber
    #pick a random route for the rider to be on
    proportions = [0.10865,0.09516,0.05263,0.34524,0.05543,0.11492,0.05391,0.11401,0.06005]
    ridersRoute = random.choices(list(routes.keys()),proportions,k=1)[0]
    rider['route'] = ridersRoute

    #pick a random stop on route for riders startingLocation
    riderStart = random.choice(list(routes[ridersRoute]['stops']))
    rider['startingLocation'] = riderStart

    #pick a random stop for rider to end trip
    stops = routes[ridersRoute]['stops']
    riderEnd = random.choice(list(stops))
    #while loop to prevent rider starting and stopping at same location
    while(riderStart == riderEnd):
        riderEnd = random.choice(list(stops))
    rider['endLocation'] = riderEnd

    #calculate direction rider needs to go
    direction = stops.index(riderEnd) - stops.index(riderStart)
    direction = direction / abs(direction) #direction == 1 if route goes north/east, and -1 if route goes south/west
    rider['direction'] = direction

    #generate time rider arrives at start location
    #generate hour of arrival first
    hours = [4,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23]
    proportions = [0.004484111171, 0.0248666529, 0.04376089221, 0.05979855107, 0.05600818086, 0.05675233207, 0.05805339645, 0.06215102909, 0.06620785344, 0.06902602609, 0.07588421967, 0.08429072788, 0.08084602791, 0.0686707539, 0.0515816814, 0.03805733325, 0.02893788018, 0.02866662506, 0.02458819632, 0.01736752908]

    hour = random.choices(hours, proportions, k=1)[0]
    minute = random.choice(range(60))

    #times will be stored in minutes, starting with t=1 at 12:01 AM day of business
    t = 60*hour + minute
    rider['timeArrived'] = t

    #return a tuple with t for time arrived, riderNumber to prevent issues sorting, and rider being the main data
    return (t,riderNumber,rider)
    


###########################################################
#Generates a bus schedule for the business day            #
#PARAMS:                                                  #
#   -timeBetweenBusses: Time (in minutes) between busses  #
#       on a given route                                  #
#   -routes: A dictionary of route information, including #
#           stops on a route, and time between stops on   #
#           the route.                                    #
#RETURNS:                                                 #
#   -A priority queue of bus stop schedule, sorted by     #
#       time each bus arrives at a given stop.            #
###########################################################
def generateSchedule(timeBetweenBusses, routes):
    schedule = PriorityQueue()

    busNumber = 0
    for route in routes:
        #generate all busses for each direction for entire day
        t = 240  #4AM busses start
        while(t <= 1440): #last busses leave right at midnight
            #schedule southbound and westbound busses
            schedule.put((t,busNumber,generateBus(routes,route,-1,t,busNumber)))
            busNumber += 1
            #schedule northbound and eastbound busses
            schedule.put((t,busNumber,generateBus(routes,route,1,t,busNumber)))
            busNumber += 1

            t += timeBetweenBusses

    return schedule

###########################################################
#Generates a single bus                                   #
#PARAMS:                                                  #
#   -routes: A dictionary of route information, including #
#           the share of ridership each route makes up in #
#           in a given day.                               #
#RETURNS:                                                 #
#   -A single bus, containing start station,              #
#       route, and time to arrive at station              #
###########################################################
def generateBus(routes,route,direction,time,busNumber):
    bus = {
        'id': busNumber,
        'route' : route,
        'direction' : direction,
        'nextStopTime' : time,
        'currentRiders' : [],
        'mostSimultaneousRiders' : 0,
        'timeEmpty': 0,
        'timeRunning': 0,
        'totalRiders': 0
    }

    stops = routes[route]['stops']
    if direction == -1: #south or west bound busses
        bus['nextStopLocation'] = stops[len(stops)-1]
    else:
        bus['nextStopLocation'] = stops[0]

    return bus

###########################################################
#Processes bus stopping with Riders who's end stop is     #
#   the current stop disboarding, then having the riders  #
#   at the current stop going the same direction board    #
#   the bus.                                              #
#PARAMS:                                                  #
#   -bus: dictionary of bus being processed at current    #
#       stop. Contains stop in bus['nextStopLocation']    #
#   -ridersWaiting: list of riders waiting for a bus      #
#RETURNS:                                                 #
#   -updated bus to replace bus passed in as a param,     #
#       returns None in this position if bus completes    #
#       route.                                            #
#   -updated ridersWaiting list with riders boarding      #
#       removed from the list                             #
###########################################################
def processStop(bus,ridersWaiting, busStats, riderStats,routeData):
    #get relevant data from bus
    route = bus['route']
    stop = bus['nextStopLocation']
    direction = bus['direction']
    t = bus['nextStopTime']

    #have necessary riders disboard
    i = 0
    while (i < len(bus['currentRiders'])) :
        rider = bus['currentRiders'][i]
        if (rider['endLocation'] == stop):
            bus['currentRiders'].remove(rider)
            rider['timeTripEnded'] = t
            riderStats = trackRiderStats(riderStats,rider)
            i -= 1
        i += 1

    #check if bus is at final stop

    if(isFinalStop(direction, routeData[route]['stops'], stop)):
        busStats = trackBusStats(busStats,bus)
        return None, ridersWaiting, busStats, riderStats

    #have riders waiting at stop board bus
    i = 0
    while(i < len(ridersWaiting) and ridersWaiting[i][2]['timeArrived'] <= t):
        rider = ridersWaiting[i][2]
        if (rider['startingLocation'] == stop and rider['direction'] == direction and rider['route'] == route):
            ridersWaiting.remove(ridersWaiting[i])
            rider['timeBoarded'] = t
            bus['currentRiders'].append(rider)
            bus['totalRiders'] += 1
            i -= 1
        i += 1

    #update bus for next stop
    bus['nextStopLocation'] = getNextStop(direction, routeData[route]['stops'], stop)

    #calculate time to next stop
    timeToNextStop = getTimeToNextStop(routeData[route],stop,direction)
    if ( not bus['currentRiders'] ):
        bus['timeEmpty'] += timeToNextStop
    
    if ( len(bus['currentRiders']) > bus['mostSimultaneousRiders'] ):
        bus['mostSimultaneousRiders'] = len(bus['currentRiders'])

    bus['nextStopTime'] = t + timeToNextStop
    bus['timeRunning'] += timeToNextStop

    return bus, ridersWaiting, busStats, riderStats


###########################################################
#Calculates the time between stops                        #
#PARAMS:                                                  #
#   -routeData: dictionary containing route stops and     #
#       time to reach each stop from the first stop       #
#   -currentStop: string containing name of current stop  #
#   -direction: direction bus is heading                  #
#RETURNS:                                                 #
#   -int representing minutes until next stop             #
###########################################################
def getTimeToNextStop(routeData,currentStop,direction):
    nextStop = getNextStop(direction,routeData['stops'],currentStop)
    indexOfNextStop = routeData['stops'].index(nextStop)
    indexOfCurrentStop = routeData['stops'].index(currentStop)
    t = (routeData['timeFromFirstStop'][indexOfNextStop] - routeData['timeFromFirstStop'][indexOfCurrentStop]) * direction
    return t

###########################################################
#Gets the name of the next stop location                  #
#PARAMS:                                                  #
#   -direction: direction bus is heading                  #
#   -routeStops: list containing route stops              #
#   -currentStop: string containing name of current stop  #
#RETURNS:                                                 #
#   -string with name of next stop on route               #
###########################################################
def getNextStop(direction,routeStops,currentStop):
    return routeStops[routeStops.index(currentStop)+direction]

###########################################################
#Checks if current stop on route is the final stop        #
#PARAMS:                                                  #
#   -direction: direction bus is heading                  #
#   -routeStops: list containing route stops              #
#   -stop: string containing name of current stop         #
#RETURNS:                                                 #
#   -boolean, true if current stop is final stop, false   #
#       if current stop is not the final stop             #
###########################################################
def isFinalStop(direction,routeStops,stop):
    return (direction == -1 and routeStops.index(stop) == 0) or (direction == 1 and routeStops.index(stop) == len(routeStops)-1)

###########################################################
#Simulates ridership for a full day based on given        #
#   parameters.                                           #
#PARAMS:                                                  #
#   -numberOfRiders: total number of riders to board      #
#       busses throughout the day                         #
#   -timeBetweenBus: time (in minutes) between busses of  #
#       the same route (for example 15 would mean 15      #
#       any route will have a bus come every 15 minutes)  #
#RETURNS:                                                 #
#   -Nothing, but prints statistics of simulation to the  #
#       console, and writes detailed breakdowns of each   #
#       individual bus and rider to a file for more       #
#       in depth analysis                                 #
###########################################################
def simulateDay(numberOfRiders,timeBetweenBus):
    print("Simulating ", numberOfRiders, " riders on a day with busses every ", timeBetweenBus, " minutes...")
    routeData = loadRouteData("routes.json")
    ridersWaiting = generateRiders(numberOfRiders, routeData)
    busSchedule = generateSchedule(timeBetweenBus, routeData)

    busStats = generateEmptyBusStats(routeData)
    riderStats = generateEmptyRiderStats()

    while(not busSchedule.empty()):
        nextBus = busSchedule.get()
        bus = nextBus[2]
        bus, ridersWaiting, busStats, riderStats = processStop(bus, ridersWaiting, busStats, riderStats,routeData)
        
        if(bus):
            nextBus = (bus['nextStopTime'], bus['id'], bus)
            busSchedule.put(nextBus)
    
    print(printBusStats(busStats))
    print(printRiderStats(riderStats))
    writeRiderStats(numberOfRiders,timeBetweenBus,riderStats)
    writeBusStats(numberOfRiders,timeBetweenBus,busStats)

###########################################################
#Loads route data from json file                          #
#PARAMS:                                                  #
#   -pathToRouteData: string representing path to json    #
#       file containing necessary data                    #
#RETURNS:                                                 #
#   -Dictionary of route data                             #
###########################################################
def loadRouteData(pathToRouteData):
    f = open(pathToRouteData)
    routeData = json.load(f)
    f.close()
    return routeData

def generateEmptyBusStats(routeData):
    busStats = {}

    for key in routeData.keys():
        busStats[key] = {
            'totalBusses': 0,
            'totalRiders':0, 
            'timeEmpty':0,
            'timeRunning':0,
            'mostRiders':0
        }

    return busStats

def generateEmptyRiderStats():
    riderStats = {
        'totalRiders': 0,
        'timeWaitingForBus': 0,
        'timeOnBus': 0,
        'totalTime': 0
    }
    return riderStats

###########################################################
#Updates total rider statistics after a rider has         #
#   completed their trip.                                 #
#PARAMS:                                                  #
#   -stats: Dictionary of tracked rider statistics        #
#   -rider: rider that just completed trip                #
#RETURNS:                                                 #
#   -updated stats dictionary                             #
###########################################################
def trackRiderStats(stats, rider):
    stats['totalRiders'] += 1
    stats['timeWaitingForBus'] += rider['timeBoarded'] - rider['timeArrived']
    stats['timeOnBus'] += rider['timeTripEnded'] - rider['timeBoarded']
    stats['totalTime'] += rider['timeTripEnded'] - rider['timeArrived']
    return stats

###########################################################
#Updates total bus statistics after a bus has             #
#   completed its route.                                  #
#PARAMS:                                                  #
#   -stats: Dictionary of tracked bus statistics          #
#   -bus: bus that just completed its route               #
#RETURNS:                                                 #
#   -updated stats dictionary                             #
###########################################################
def trackBusStats(stats, bus):
    route = bus['route']
    stats[route]['totalBusses'] += 1
    stats[route]['totalRiders'] += bus['totalRiders']
    stats[route]['timeEmpty'] += bus['timeEmpty']
    stats[route]['timeRunning'] += bus['timeRunning']
    if stats[route]['mostRiders'] < bus['mostSimultaneousRiders']:
        stats[route]['mostRiders'] = bus['mostSimultaneousRiders']

    return stats

###########################################################
#Makes total rider statistics into a string after         #
#   simulation has completed. This is for printing or     #
#   writing to file                                       #
#PARAMS:                                                  #
#   -stats: Dictionary of tracked rider statistics        #
#RETURNS:                                                 #
#   -String of statistics in readable format              #
###########################################################
def printRiderStats(stats):
    totalRiders = stats['totalRiders']
    timeWaiting = stats['timeWaitingForBus']
    timeOnBus = stats['timeOnBus']
    totalTime = stats['totalTime']

    riderLog = "Rider Statisics:\n"
    riderLog += "\tTotal Riders = " + str(totalRiders) + " riders\n"
    riderLog += "\tAverage Wait Time = " + str(timeWaiting/totalRiders) + " minutes\n"
    riderLog += "\tAverage Time On Bus = " + str(timeOnBus/totalRiders) + " minutes\n"
    riderLog += "\tAverage Trip Length = " + str(totalTime/totalRiders) + " minutes\n"

    return riderLog

###########################################################
#Makes total bus statistics into a string after           #
#   simulation has completed. This is for printing or     #
#   writing to file                                       #
#PARAMS:                                                  #
#   -stats: Dictionary of tracked bus statistics          #
#RETURNS:                                                 #
#   -String of statistics in readable format              #
###########################################################
def printBusStats(stats):
    busLog = "Bus Route Statistics:\n"
    for i in stats:
        totalBusses = stats[i]['totalBusses']
        totalRiders = stats[i]['totalRiders']
        timeEmpty = stats[i]['timeEmpty']
        timeRunning = stats[i]['timeRunning']
        mostRiders = stats[i]['mostRiders']

        busLog += "\tRoute " + i + ":\n"
        busLog += "\t\tTotal Busses = " + str(totalBusses) + " busses\n"
        busLog += "\t\tTotal Riders = " + str(totalRiders) + " riders\n"
        busLog += "\t\tTime Empty = " + str(timeEmpty) + " minutes\n"
        busLog += "\t\tTime Running = " + str(timeRunning) + " minutes\n"
        busLog += "\t\tUtilization Rate = " + str((timeRunning-timeEmpty)/timeRunning) + "\n"
        busLog += "\t\tMost Riders At One Time= " + str(mostRiders) + " riders\n"
        busLog += "\t\tAverage number of riders per bus = " + str(totalRiders/totalBusses) + " riders per bus\n"

    return busLog

def writeRiderStats(numberOfRiders,timeBetweenBusses,riderStats):
    f = open("riderstats.csv", "a")
    line = str(numberOfRiders)+","+str(timeBetweenBusses)+","
    line += str(riderStats['timeWaitingForBus'])+","+str(riderStats['timeOnBus'])+","
    line += str(riderStats['totalTime'])+"\n"
    f.write(line)
    f.close()

def writeBusStats(numberOfRiders,timeBetweenBusses,busStats):
    f = open("busstats.csv","a")
    for i in busStats.keys():
        line = str(numberOfRiders)+","+str(timeBetweenBusses)+","+i+","
        line += str(busStats[i]['totalBusses']) + ","
        line += str(busStats[i]['totalRiders']) + ","
        line += str(busStats[i]['timeEmpty']) + ","
        line += str(busStats[i]['timeRunning']) + ","
        line += str(busStats[i]['mostRiders']) + "\n"
        f.write(line)
    f.close()
    

def printBusArt():
    print(" .-------------------------------------------------------------.")
    print("'------..-------------..----------..----------..----------..--.|")
    print("|       \\\\            ||          ||          ||          ||  ||")
    print("|        \\\\           ||          ||          ||          ||  ||")
    print("|    ..   ||  _    _  ||    _   _ || _    _   ||    _    _||  ||")
    print("|    ||   || //   //  ||   //  // ||//   //   ||   //   //|| /||")
    print("|_.------\"''----------''----------''----------''----------''--'|")
    print(" |)|      |       |       |       |    |      mga|      ||==|  |")
    print(" | |      |  _-_  |       |       |    |  .-.    |      ||==| C|")
    print(" | |  __  |.'.-.' |   _   |   _   |    |.'.-.'.  |  __  | \"__=='")
    print(" '---------'|( )|'----------------------'|( )|'----------\"\" ")
    print("             '-'                          '-' ")
    print("   Art by:      Martin Atkins    mart.atkins@bigfoot.com")

if __name__ == "__main__":
    main()