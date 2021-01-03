# Temperature Data by Month

# Overview

This project focuses on obtaining reliable weather values separated by month. Local temperature and mean-coincedent values are important for mechanical equipment design. By finding the likelihoods of extreme temperatures, and the mean-coincedent temperatures, designers can select suitable equipment to work in the project location. By separating this analysis by month, designers can consider energy savings by shutting down equipment or running systems at part load in shoulder seasons.

## Parameters
The following temperatures will be found in this analysis:
* Dry Bulb Temperature (DB)
* Wet Bulb Temperature (WB)
* Dew Point Temperature (DP)
One of the temperatures is user input of the primary temperature. The other temperatures will be found as mean-coincedent values to the primary temperature.

## Monthly Extreme Values
The monthly extreme primary temperatures are defined as a set percentage of the month that will be warmer than that temperature. Designers can base thier analysis off of a given extreme based on heating vs. cooling, and conservitivism of design. The following extremes will be found in this analysis:
* T, 99.6% = This temperature will be exceeded 99.6% of hours in a month
* T, 99.0% = This temperature will be exceeded 99.0% of hours in a month
* T, 2.0% = This temperature will be exceeded 2.0% of hours in a month
* T, 1.0% = This temperature will be exceeded 1.0% of hours in a month
* T, 0.4% = This temperature will be exceeded 0.4% of hours in a month

## User inputs
* location - user can choose 1 or 2 weather station IDs to represent a project location. If weather station changed codes during the analysis, the second statin code will be used if the first cannot be found.
* start_year - first year of analysis (inclusive)
* end_year - last year of analysis (inclusive)
* Psta - average atmospheric pressure of the location (psi). Needed for calculting wet bulb temperature from dry bulb temperature and dew point.
* primaryTemp - the month percentiles of the primary temperture will be found. The other 2 temperatures (DB, WB or DP) will be calculated as the mean-coincedent temperatures to the primary temperature.

## Final Report
The final report(final.csv) shows all 5 primary and mean-coincedent temperature extreme values for each month of the year (unless valid data was not available). 

## Calculations
Guidelenes and parameters from ASHRAE Fundementals 2017 were use to deem data valid or not. The floowingrules were followed:
* If data is not available for a given hour of the year, the closest recorded data will be recorded if it is within 0.5 hrs
* Gaps in data less than 6 hours can be filled by linearly interpolating between the closest hours
* 85% of the hours in a month must be recorded for a month to be included in the analysis
* The difference between daytime and nighttime recorded hours must be less than 60 for a month to be included in the analysis
* At least 8 instances of a month must be valid over the range of years for the month to be included in the final data

## Recording Periods
While the user can set any range of years (must be more than 7) to run an analysis, ASHRAE generally uses one of two periods:
* 1986 to 2010
* 1990 to 2014
<a/>
Use the proper years to fit your study
