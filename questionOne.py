import numpy as np
from matplotlib import pyplot as plt

timeStep = 1

class qOut:
    def __init__(self):
        self.time = 0

        self.windVelocity = 3    # m/s

        self.poolTopSurface = 10 * 20    # m^2
        self.poolSidesSurface = 1.5 * (10 + 10 + 20 + 20)    # m^2

        self.waterTemperature = 37 + 273    # Kelvin
        self.waterifg = 2414 * 1000    # J/kg @ 37°C
        self.waterh = 1    # TROUVER LE H DE L'EAU DANS LE BASSIN

        self.airTemperature = self.getAirTemperature()
        self.airCp = 1.007 * 1000    # J/kgK @ 25°C
        self.airRho = 1.1614    # kg/m^3 @ 25°C

        self.airViscosity = self.getAirViscosity(self.airTemperature)
        self.airReynold = self.getAirReynold()
        self.airPrandtl = self.getAirPrandtl(self.airTemperature)
        self.airNu = self.getAirNu()
        self.airK = self.getAirK(self.airTemperature)
        self.airToph = self.getAirH()
        self.airThermicDiffusivity = 15.9 * 10**-6 + 6.6 * 10**-6 * (self.airTemperature - 250) / 50
        self.Dab = 0.26 * 10**-4
        self.airhm = self.airToph / (self.airRho * self.airCp * (self.airThermicDiffusivity / self.Dab)**(2/3))    # m/s
        self.mDot = self.getMDotEvap()

        # self.airSidesh = 1 # DUNNO COMMENT TROUVER CA HEHE
        self.airSidesh = self.airToph

        self.coldWaterTemprature = 7 + 273    # Kelvin
        self.coldWaterCp = 4.198 * 1000    # J/kgK @ 7°C

        self.glassk = 1.4    # W/mK pyrex
        self.glassThickness = 0.015  # m
        self.insulatingk = 0.05    # W/mK
        self.insulatingThickness = 0    # m

        self.qEvap = self.getqEvap()
        self.qColdWater = self.getqColdWater()
        self.qSurfaces = self.getqSurfaces()
        self.qTot = self.getqTotal()



    ## METHODS CALLED TO MODIFY CLASS VARIABLES

    def updateProperties(self):
        self.airTemperature = self.getAirTemperature()

        self.airViscosity = self.getAirViscosity(self.airTemperature)
        self.airReynold = self.getAirReynold()
        self.airPrandtl = self.getAirPrandtl(self.airTemperature)
        self.airNu = self.getAirNu()
        self.airK = self.getAirK(self.airTemperature)
        self.airToph = self.getAirH()
        self.airhm = self.airToph / (self.airRho * self.airCp * 20 * np.exp(2 / 3))
        self.mDot = self.getMDotEvap()

        self.qEvap = self.getqEvap()
        self.qColdWater = self.getqColdWater()
        self.qSurfaces = self.getqSurfaces()
        self.qTot = self.getqTotal()

    def updateTime(self, time):
        self.time = time
        self.updateProperties()

    def updateThickness(self, thickness):
        if thickness != 0:
            self.insulatingThickness = thickness
            self.updateProperties()

    def getAirViscosity(self, temperature):
        return (0.089 * temperature - 10.81) * 10**-6

    def getAirReynold(self):
        return self.windVelocity * 20 / self.airViscosity

    def getAirPrandtl(self, temperature):
        return -2.6 * 10**-4 * temperature + 0.785

    def getAirNu(self):
        return (0.037 * self.airReynold**(4/5) - 871) * self.airPrandtl**(1/3)

    def getAirK(self, temperature):
        return (0.08 * temperature + 2.3) * 10**-3

    def getAirH(self):
        return self.airNu * self.airK / 20

    def getAirTemperature(self):    # t is time in days
        return 6.4 + 29.5 * np.sin(1.5 * np.pi + 2 * np.pi / 365 * self.time) + 273

    def getMDotEvap(self):
        Wf = 1.9747e-5 * self.waterTemperature**2 + 1.3257e-4 * self.waterTemperature + 3.9866e-3
        Wair = 0.5 * Wf
        return self.airhm * (Wf - Wair) * self.poolTopSurface


    ## ENERGY Q

    def getqTotal(self):
        return self.getqSurfaces() + self.getqEvap() + self.getqColdWater()

    def getqEvap(self):
        return self.mDot * self.waterifg

    def getqColdWater(self):
        return self.mDot * self.coldWaterCp * (self.waterTemperature - self.coldWaterTemprature)

    def getqSurfaces(self):
        equivalentR = ( (self.getTopRConvectionWithAir())**-1
                        + (self.getSidesRConvectionWithWater()
                           + self.getSidesRConductionInGlass()
                           + self.getSidesRConductionInInsulating()
                           + self.getSidesRConvectionWithAir() )**-1 )**-1
        return (self.waterTemperature - self.airTemperature)/equivalentR


    ## RESISTANCES R

    def getTopRConvectionWithAir(self):
        return 1 / (self.airToph * self.poolTopSurface)

    def getSidesRConvectionWithWater(self):
        return 0 * 1 / (self.waterh * self.poolSidesSurface)

    def getSidesRConductionInGlass(self):
        return self.glassThickness / (self.glassk * self.poolSidesSurface)

    def getSidesRConductionInInsulating(self):
        return self.insulatingThickness / (self.insulatingk * self.poolSidesSurface)

    def getSidesRConvectionWithAir(self):
        return 1 / (self.airSidesh * self.poolSidesSurface)


# a = qOut()
# print(a.qColdWater)
# print(a.__dict__)
# values = []
# print(a.insulatingThickness)
# for i in range(5):
#     a.updateTime(timeStep * (i + 1))
#     print(a.qColdWater, a.qEvap, a.qSurfaces)
#     values.append(a.qTot)
# print(values)
#
a = qOut()
a.updateThickness(0.005)
print(a.insulatingThickness)
values =  []
for i in range(5):
    a.updateTime(timeStep * (i + 1))
    values.append(a.qTot)
print(values)



class simulationInTime:
    def __init__(self):
        self.timeStep = timeStep
        self.numberOfDays = 365

        # self.insulatingThicknessValues = self.generateInsulatingThicknessValues()
        self.insulatingThicknessValues = [0.005]
        self.timeValues = self.generateTimeValues()
        self.sets = self.generateQValuesForAllSets()

    def generateInsulatingThicknessValues(self):
        numberOfValues = 5
        step = 0.010   # m
        return [round(value * step, 6) for value in range(numberOfValues)]

    def generateTimeValues(self):
        return ([(step + 1) * self.timeStep for step in range(int(self.numberOfDays / self.timeStep))])

    def generateQValues(self, thickness = 0):
        q = qOut()
        q.updateThickness(thickness)
        qValues = list()
        for time in self.timeValues:
            q.updateTime(time)
            print(q.__dict__)
            qValues.append(q.qTot)
        return qValues

    def generate3Values(self, thickness = 0):
        q = qOut()
        q.updateThickness(thickness)
        qSurfaces, qEvap, qColdWater = list(), list(), list()
        for time in self.timeValues:
            q.updateTime(time)
            print(q.__dict__)
            qSurfaces.append(q.qSurfaces)
            qEvap.append(q.qEvap)
            qColdWater.append(q.qColdWater)
        return [qSurfaces, qEvap, qColdWater]

    def generateQValuesForAllSets(self):
        sets = []
        for thickness in self.insulatingThicknessValues:
            # sets.append(self.generateQValues(thickness=thickness))
            sets.append(self.generate3Values(thickness=thickness))
        return sets

    def plot(self):
        for i in range(len(self.insulatingThicknessValues)):
            # thickness = self.insulatingThicknessValues[i]
            # set = self.sets[i]
            # plt.plot(self.timeValues,set,label='%s' % str(thickness))

            set = self.sets[i][0]
            plt.plot(self.timeValues,set,label='qSurfaces')
            set = self.sets[i][1]
            plt.plot(self.timeValues,set,label='qEvap')
            set = self.sets[i][2]
            plt.plot(self.timeValues,set,label='qColdWater')
        # plt.legend(title="Épaisseur d'isolant (m)")
        plt.legend(title="Isolant de 5 mm d'épaisseur")

        plt.xlabel('Temps (jours)')
        plt.ylabel('Énergie perdue (W)')
        plt.title('Un beau titre')
        # plt.show()
        plt.savefig('Q1-qOutOverTime', bbox_inches='tight')

# print("\\")
a = simulationInTime()
a.plot()
