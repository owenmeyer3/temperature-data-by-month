import math
# Temp conversion C to F
def CtoF(temp_C):
    temp_F=temp_C*9/5+32
    return temp_F

# Wet bulb function (dryBulb [F], DP [F], Psta [psia])
def wetBulbFunc(dryBulb, dpTemp, Psta):
    e=6.112*math.e**(17.67/(1+438/(dpTemp-32.001)))
    WB = 0
    increse = 1
    previoussign = 1
    Ed = 1
    while math.fabs(Ed) > 0.003:
        Ewg = 6.112 * math.e**((9.81667 * (WB-32) / (0.5556*(WB-32) + 243.5)))
        eg = Ewg - Psta*(dryBulb-WB)*(0.02458+0.000021769*dryBulb)
        Ed = e - eg
        if Ed ==0:
            break
        else:
            if Ed <0:
                cursign = -1
                if cursign != previoussign:
                    previoussign = cursign
                    increse = increse/10
                else:
                    increse = increse
            else:
                cursign = 1
                if cursign != previoussign:
                    previoussign = cursign
                    increse = increse/10
                else:
                    increse = increse
        WB = WB + increse * previoussign
    return WB