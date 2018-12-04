import numpy as np
from matplotlib import pyplot as plt

timeStep = 1

class qOut:
    
    "CONSTRUCTOR"
    def __init__(self):
        self.time = 0

        self.windVelocity = 3    # m/s

        self.poolTopSurface = 10 * 20    # m^2
        self.poolSidesSurface = 1.5 * (10 + 10 + 20 + 20)    # m^2

        self.waterTemperature = 37 + 273    # Kelvin
        self.waterifg = 2414 * 1000    # J/kg @ 37°C
        # self.waterh = 1    # TROUVER LE H DE L'EAU DANS LE BASSIN

        self.airTemperature = self.getAirTemperature()
        self.airCp = 1.007 * 1000    # J/kgK @ 25°C
        self.airRho = 1.1614    # kg/m^3 @ 25°C

        self.airTopViscosity = self.getAirViscosity((self.airTemperature + self.waterTemperature) / 2)
        self.airTopReynold = self.getAirReynold(self.airTopViscosity)
        self.airTopPrandtl = self.getAirPrandtl((self.airTemperature + self.waterTemperature) / 2)
        self.airTopNu = self.getAirNu(self.airTopReynold, self.airTopPrandtl)
        self.airTopK = self.getAirK((self.airTemperature + self.waterTemperature) / 2)
        self.airTopH = self.getAirH(self.airTopNu, self.airTopK)
        
        self.airTopThermicDiffusivity = self.getAirThermicDiffusivity((self.airTemperature + self.waterTemperature) / 2)
        self.Dab = 0.26 * 10**-4
        self.airHm = self.getAirHm(self.airTopH, self.airTopThermicDiffusivity)
        self.mDot = self.getMDotEvap()
        
        self.airSidesViscosity = self.getAirViscosity(self.airTemperature)
        self.airSidesReynold = self.getAirReynold(self.airTopViscosity)
        self.airSidesPrandtl = self.getAirPrandtl(self.airTemperature)
        self.airSidesNu = self.getAirNu(self.airTopReynold, self.airTopPrandtl)
        self.airSidesK = self.getAirK(self.airTemperature)
        self.airSidesH = self.getAirH(self.airSidesNu, self.airSidesK)

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

    ## TO DEFINE OR MODIFY CLASS VARIABLES
    
    def getAirTemperature(self):    # t is time in days
        return 6.4 + 29.5 * np.sin(1.5 * np.pi + 2 * np.pi / 365 * self.time) + 273

    def updateProperties(self):
        self.airTemperature = self.getAirTemperature()
        
        self.airTopViscosity = self.getAirViscosity((self.airTemperature + self.waterTemperature) / 2)
        self.airTopReynold = self.getAirReynold(self.airTopViscosity)
        self.airTopPrandtl = self.getAirPrandtl((self.airTemperature + self.waterTemperature) / 2)
        self.airTopNu = self.getAirNu(self.airTopReynold, self.airTopPrandtl)
        self.airTopK = self.getAirK((self.airTemperature + self.waterTemperature) / 2)
        self.airTopH = self.getAirH(self.airTopNu, self.airTopK)
        self.airTopThermicDiffusivity = self.getAirThermicDiffusivity((self.airTemperature + self.waterTemperature) / 2)
        self.airHm = self.getAirHm(self.airTopH, self.airTopThermicDiffusivity)
        
        self.mDot = self.getMDotEvap()
        
        self.airSidesViscosity = self.getAirViscosity(self.airTemperature)
        self.airSidesReynold = self.getAirReynold(self.airTopViscosity)
        self.airSidesPrandtl = self.getAirPrandtl(self.airTemperature)
        self.airSidesNu = self.getAirNu(self.airTopReynold, self.airTopPrandtl)
        self.airSidesK = self.getAirK(self.airTemperature)
        self.airSidesH = self.getAirH(self.airSidesNu, self.airSidesK)

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

    # TO FIND H OF AIR
    
    def getAirViscosity(self, temperature):
        return (0.089 * temperature - 10.81) * 10**-6

    def getAirReynold(self, viscosity):
        return self.windVelocity * 20 / viscosity

    def getAirPrandtl(self, temperature):
        return -2.6 * 10**-4 * temperature + 0.785

    def getAirNu(self, Reynold, Prandtl):
        return (0.037 * Reynold**(4/5) - 871) * Prandtl**(1/3)

    def getAirK(self, temperature):
        return (0.08 * temperature + 2.3) * 10**-3

    def getAirH(self, Nu, K):
        return Nu * K / 20

    # TO FIND M DOT OF EVAPORATION
    
    def getAirThermicDiffusivity(self, temperature):
        return 15.9 * 10**-6 + 6.6 * 10**-6 * (temperature - 250) / 50

    def getAirHm(self, h, thermicDiffusivity):
        return h / (self.airRho * self.airCp * (thermicDiffusivity / self.Dab)**(2/3))    # m/s

    def getMDotEvap(self):
        Wf = ( 1.9747 * 10**-5 * (self.waterTemperature - 273)**2
               + 1.3257 * 10**-4 * (self.waterTemperature - 273)
               + 3.9866 * 10**-3 )
        Wair = 0.5 * Wf
        return self.airHm * (Wf - Wair) * self.poolTopSurface


    ## ENERGY Q

    def getqTotal(self):
        return self.getqSurfaces() + self.getqEvap() + self.getqColdWater()

    def getqEvap(self):
        return self.mDot * self.waterifg

    def getqColdWater(self):
        return self.mDot * self.coldWaterCp * (self.waterTemperature - self.coldWaterTemprature)

    def getqSurfaces(self):
        equivalentR = ( (self.getTopRConvectionWithAir())**-1
                        + (self.getSidesRConductionInGlass()
                           + self.getSidesRConductionInInsulating()
                           + self.getSidesRConvectionWithAir() )**-1 )**-1
        return (self.waterTemperature - self.airTemperature)/equivalentR


    ## RESISTANCES R

    def getTopRConvectionWithAir(self):
        return 1 / (self.airTopH * self.poolTopSurface)

    # def getSidesRConvectionWithWater(self):
    #     return 0 * 1 / (self.waterh * self.poolSidesSurface)

    def getSidesRConductionInGlass(self):
        return self.glassThickness / (self.glassk * self.poolSidesSurface)

    def getSidesRConductionInInsulating(self):
        return self.insulatingThickness / (self.insulatingk * self.poolSidesSurface)

    def getSidesRConvectionWithAir(self):
        return 1 / (self.airSidesH * self.poolSidesSurface)


class simulationInTime:
    
    "CONSTRUCTOR"
    def __init__(self):
        self.timeStep = timeStep
        self.numberOfDays = 365

        self.insulatingThicknessValues = self.generateInsulatingThicknessValues()
        self.timeValues = self.generateTimeValues()
        self.sets = self.generateQValuesForAllSets()

    def generateInsulatingThicknessValues(self):
        numberOfValues = 5
        step = 0.01   # m
        return [round(value * step, 6) for value in range(numberOfValues)]

    def generateTimeValues(self):
        return ([(step + 1) * self.timeStep for step in range(int(self.numberOfDays / self.timeStep))])

    ## TO GRAPH Q_TOT FOR DIFFERENT INSULATING THICKNESSES
    
    def generateQValues(self, thickness = 0):
        q = qOut()
        q.updateThickness(thickness)
        qValues = list()
        for time in self.timeValues:
            q.updateTime(time)
            print(q.__dict__)
            qValues.append(q.qTot)
        return qValues

    def generateQValuesForAllSets(self):
        sets = []
        for thickness in self.insulatingThicknessValues:
            sets.append(self.generateQValues(thickness=thickness))
        return sets

    def plotQtot(self):
        plt.figure()
        for i in range(len(self.insulatingThicknessValues)):
            thickness = self.insulatingThicknessValues[i]
            set = self.sets[i]
            plt.plot(self.timeValues,set,label='%s' % str(thickness))
        plt.legend(title="Épaisseur d'isolant (m)")
        plt.xlabel('Temps (jours)')
        plt.ylabel('Énergie perdue (W)')
        plt.title('Un beau titre')
        plt.savefig('Q1-qOutOverTime', bbox_inches='tight')


    ## TO GRAPH Q_EVAP, Q_COLD WATER AND Q_SURFACES FOR A GIVEN INSULATING THICKNESS
    
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

    def plot3lines(self, thickness):
        set = self.generate3Values(thickness=thickness)

        plt.figure()
        plt.plot(self.timeValues,set[0],label='qSurfaces')
        plt.plot(self.timeValues,set[1],label='qEvap')
        plt.plot(self.timeValues,set[2],label='qColdWater')

        plt.legend(title="Isolant de %s m d'épaisseur" % thickness)
        plt.xlabel('Temps (jours)')
        plt.ylabel('Énergie perdue (W)')
        plt.title('Un beau titre')
        plt.savefig('Q1-qOutOverTime_3lines', bbox_inches='tight')
        
        
        
        
    def generateValues(self, thickness = 0):
        q = qOut()
        q.updateThickness(thickness)
        airTopK = list()
        for time in self.timeValues:
            q.updateTime(time)
            print(q.__dict__)
            airTopK.append(q.airTopK)
        return airTopK

    def plot(self, thickness):
        set = self.generateValues(thickness=thickness)

        plt.figure()
        plt.plot(self.timeValues,set,label='q_')

        plt.legend(title="Isolant de %s m d'épaisseur" % thickness)
        plt.xlabel('Temps (jours)')
        plt.ylabel('Énergie perdue (W)')
        plt.title('Un beau titre')
        plt.savefig('Q1-qOutOverTime_whatever', bbox_inches='tight')

a = simulationInTime()
a.plotQtot()
a.plot3lines(0.01)
