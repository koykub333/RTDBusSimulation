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
    simulateDay(100000,10)

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
    riders = PriorityQueue()
    for i in range(n):
        riders.put(generateRider(routes,i))

    riderList = []
    while riders.empty() == False:
        riderList.append(riders.get())
    
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
    #pick a random route for the rider to be on
    ridersRoute = random.choice(list(routes.keys()))
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

    #return a tuple with t for the priority queue, riderNumber to prevent priority collisions, and rider being the main data
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
        while(t < 1440): #last busses leave right before midnight
            #schedule southbound and westbound busses
            schedule.put((t,busNumber,generateBus(routes,route,-1,t)))
            busNumber += 1
            #schedule northbound and eastbound busses
            schedule.put((t,busNumber,generateBus(routes,route,1,t)))
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
def generateBus(routes,route,direction,time):
    bus = {
        'route' : route,
        'direction' : direction,
        'nextStopTime' : time,
        'currentRiders' : [],
        'mostSimultaneousRiders' : 0,
        'timeEmpty': 0,
        'totalRiders': 0
    }

    stops = routes[route]['stops']
    if direction == -1: #south or west bound busses
        bus['nextStopLocation'] = stops[len(stops)-1]
    else:
        bus['nextStopLocation'] = stops[0]

    return bus

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
    routeData = loadRouteData("routes.json")
    ridersWaiting = generateRiders(numberOfRiders, routeData)
    busSchedule = generateSchedule(timeBetweenBus, routeData)

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
    pass

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
    pass

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
    pass

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
    pass

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