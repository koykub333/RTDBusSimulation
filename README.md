RTDBusSimulation
by Koy Kubasta
for CSCI 4203 - Simulations

A python simulation that takes the 9 most commonly boarded bus routes in Denver, and simulates a new 
regular interval schedule for these routes. This simulation uses a parameter sweep to simulate different
time intervals between busses and daily ridership levels.

The simulation uses RTD public records from 2022 to find the range of daily ridership averages, and uses
records acquired from RTD through a CORA request in order to find the proportions of riders that board at
different times of day and on different routes. 

Results are printed to "busstats.csv" and "riderstats.csv"
