import math
import sqlite3

from PyQt5.QtCore import QUrl, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QWidget, QFileDialog, QMessageBox, QGridLayout, QPushButton, QLabel, QComboBox, QGroupBox, \
    QVBoxLayout, QLineEdit, QHBoxLayout, QRadioButton, QApplication


class Weapon:
    crew: int = None
    size: int = None
    cost: int = None
    capacitor: int = None
    power: int = None
    rechargeRate: int = None
    htk: int = None
    damage: int = None
    shots: int = None
    rangeMod: int = None
    duranium: int = None
    neutronium: int = None
    corbomite: int = None
    tritanium: int = None
    boronide: int = None
    mercassium: int = None
    vendarite: int = None
    sorium: int = None
    uridium: int = None
    corundium: int = None
    gallicite: int = None
    materials: list = None
    componentValue: int = None

    def __init__(self, data):
        self.crew = data[0]
        self.size = data[1]
        self.cost = data[2]
        self.capacitor = data[5]
        self.componentValue = data[3]
        self.power = data[4]
        self.rechargeRate = data[5]
        self.htk = data[6]
        self.damage = data[7]
        self.shots = data[8]
        self.rangeMod = data[9]
        self.duranium = data[10]
        self.neutronium = data[11]
        self.corbomite = data[12]
        self.tritanium = data[13]
        self.boronide = data[14]
        self.mercassium = data[15]
        self.vendarite = data[16]
        self.sorium = data[17]
        self.uridium = data[18]
        self.corundium = data[19]
        self.gallicite = data[20]
        self.materials = [self.duranium, self.neutronium, self.corbomite, self.tritanium, self.boronide,
                          self.mercassium,
                          self.vendarite, self.sorium, self.uridium, self.corundium, self.gallicite]


# noinspection PyAttributeOutsideInit
def calcRoF(weapon: Weapon):
    rof = (25 * weapon.power) / (5 * weapon.capacitor)
    if rof % 5 > 0:
        rof = rof + 5 - (rof % 5)
    return rof


def calcArmorSize(hullSize, armorLevel, turretArmorLevel):
    armorSize = turretArmorLevel * (
            math.pow(math.pow(hullSize * 0.75 / math.pi, 1.0 / 3.0), 2.0) * 4 * math.pi / 4.0) / armorLevel
    return armorSize


def calcArmorCost(hullSize, turretArmorLevel):
    armorSize = turretArmorLevel * (
            math.pow(math.pow(hullSize * 0.75 / math.pi, 1.0 / 3.0), 2.0) * 4 * math.pi / 4.0) / 10
    armorCost = armorSize * 10
    return armorCost


def calcCost(weapon: Weapon):
    cost = 0
    for material in weapon.materials:
        cost += material
    return cost


class Window(QWidget):
    # noinspection SpellCheckingInspection
    conn: sqlite3.Connection = None
    c: sqlite3.Cursor = None
    gameID: int = None
    gameID: dict = None
    raceID: int = None
    raceIDs: dict = None
    weaponID: int = None
    weapon: Weapon = None
    weaponType: dict = None
    weaponIDs: dict = None
    armorBase: int = None
    trackingTech: int = None
    armor: dict = None
    spaceMaster: bool = False
    techType: dict = None
    turretWeapon: Weapon = None
    insert: bool = False
    turretTrackingSpeed: int = None

    def __init__(self):
        super().__init__()
        self.initUI()
        self.conn = None
        self.c = None
        self.gameID = 0
        self.gameIDs = {}
        self.raceID = 0
        self.raceIDs = {}
        self.weaponID = 0
        self.weapon = {}
        self.weaponType = {"Laser": 15, "Particle Beam": 30, "Railgun": 35, "Gauss Cannon": 45}
        self.weaponIDs = {}
        self.armorBase = 3136
        self.trackingTech = 0
        self.techType = {}

    def showFileChooser(self):
        self.gameID = 0
        self.gameIDs = {}
        self.raceID = 0
        self.raceIDs = {}
        self.weaponID = 0
        if self.conn is not None:
            self.conn.close()
            self.conn = None
        self.gameBox.clear()
        file = QFileDialog.getOpenFileUrl(self, "Open file", filter="DB files (*.db)")
        if file[0] != QUrl(""):
            url = file[0].toLocalFile()
            self.conn = sqlite3.connect(url)
            self.dbLabel.setText("Connected to: " + file[0].fileName())
            self.c = self.conn.cursor()
            self.c.execute("SELECT GameID, GameName FROM FCT_Game")
            results = self.c.fetchall()
            for result in results:
                id = result[0]
                name = result[1]
                self.gameIDs[name] = id
                self.gameBox.addItem(name)
            self.gameBox.setDisabled(False)

    def changeRace(self):
        self.weaponID = 0
        self.raceBox.clear()
        if self.gameBox.currentText() in self.gameIDs.keys():
            self.gameID = self.gameIDs[self.gameBox.currentText()]
        else:
            self.gameID = 0
        if self.conn is not None and self.gameID != 0:
            try:
                self.c.execute("SELECT RaceID, NPR, RaceTitle, GameID FROM FCT_Race")
            except Exception as err:
                print(err)
            results = self.c.fetchall()

            for result in results:
                raceid = result[0]
                npr = result[1]
                name = result[2]
                gameid = result[3]
                if self.gameID == gameid and not npr:
                    self.raceIDs[name] = raceid
                    self.raceBox.addItem(name)
                    self.raceBox.setDisabled(False)
        else:
            self.raceBox.setDisabled(True)

        if self.raceBox.currentText():
            self.weaponTypeBox.setDisabled(False)
        else:
            self.weaponTypeBox.setDisabled(True)

    def changeWeapons(self):
        self.weaponBox.clear()
        if self.raceBox.currentText() in self.raceIDs.keys():
            self.raceID = self.raceIDs[self.raceBox.currentText()]
        if self.conn is not None and self.gameID != 0 and self.raceID != 0:
            try:
                self.c.execute("SELECT SDComponentID, GameID, BeamWeapon, Name, ComponentTypeID, TurretWeaponID FROM "
                               "FCT_ShipDesignComponents")
            except Exception as err:
                print(err)
            results = self.c.fetchall()
            for result in results:
                weaponid = result[0]
                gameid = result[1]
                beamweapon = result[2]
                name = result[3]
                weapontype = result[4]
                turretid = result[5]
                if gameid == self.gameID and beamweapon and turretid == 0 and weapontype == self.weaponType[
                    self.weaponTypeBox.currentText()]:
                    try:
                        self.c.execute(
                            f"SELECT Obsolete, RaceID FROM FCT_RaceTech WHERE TechID = {weaponid} AND GameID = {self.gameID}")
                    except Exception as err:
                        print(err)
                    techresult = self.c.fetchone()
                    if techresult is not None and not techresult[0] and techresult[1] == self.raceID:
                        self.weaponIDs[name] = weaponid
                        self.weaponBox.addItem(name)
            self.weaponBox.setDisabled(False)
        else:
            self.weaponBox.setDisabled(True)

        if self.weaponBox.currentText():
            self.trackingSpeedLine.setDisabled(False)
            self.armorAmountLine.setDisabled(False)
        else:
            self.trackingSpeedLine.setDisabled(True)
            self.armorAmountLine.setDisabled(True)

    def getCustomArmorUp(self, prerequisite):
        if self.conn is not None and self.gameID != 0 and self.raceID != 0:
            try:
                self.c.execute(
                    f"SELECT Name, Prerequisite1, AdditionalInfo, TechSystemID FROM FCT_TechSystem WHERE Prerequisite1 = {prerequisite}")
            except Exception as err:
                print(err)
            result = self.c.fetchone()
            if result is not None:
                self.armor[result[0]] = result[2]
                self.armorBox.clear()
                self.armorBox.addItems(self.armor.keys())
                try:
                    self.c.execute(
                        f"SELECT TechID FROM FCT_RaceTech WHERE GameID = {self.gameID} AND RaceID = {self.raceID} AND "
                        f"TechID = {result[3]}")
                except Exception as err:
                    print(err)
                techResult = self.c.fetchone()
                if techResult is not None:
                    self.armorBox.setCurrentText(result[0])
                self.getCustomArmorUp(result[3])

    def getArmorTech(self):
        if self.conn is not None and self.gameID != 0 and self.raceID != 0:
            try:
                self.c.execute(
                    f"SELECT TechID FROM FCT_RaceTech WHERE GameID = {self.gameID} AND RaceID = {self.raceID} AND ("
                    f"TechID BETWEEN 3136 AND 3147 OR TechID = 27459 OR TechID = 65899 OR TechID = 65900)")
            except Exception as err:
                print(err)
            results = self.c.fetchall()
            minTech = 3136
            techLevel = 0
            for result in results:
                if result[0] == 27459 and techLevel < 3:
                    techLevel = 0
                elif result[0] == 65899 and techLevel < 3:
                    techLevel = 1
                elif result[0] == 65900 and techLevel < 3:
                    techLevel = 2
                elif minTech <= result[0] <= 3147:
                    minTech = result[0]
                    techLevel = minTech - self.armorBase + 3
            self.armorBox.setCurrentIndex(techLevel)
            self.getCustomArmorUp(3147)

    def getCustomSpeedTechs(self, prerequisite):
        if self.conn is not None and self.gameID != 0 and self.raceID != 0:
            try:
                self.c.execute(
                    f"SELECT Name, Prerequisite1, AdditionalInfo, TechSystemID FROM FCT_TechSystem WHERE Prerequisite1 = {prerequisite}")
            except Exception as err:
                print(err)
            result = self.c.fetchone()
            if result is not None:
                try:
                    self.c.execute(
                        f"SELECT TechID FROM FCT_RaceTech WHERE GameID = {self.gameID} AND RaceID = {self.raceID} AND "
                        f"TechID = {result[3]}")
                except Exception as err:
                    print(err)
                techResult = self.c.fetchone()
                if techResult is not None:
                    self.trackingSpeedTechLabel.setText(result[0])
                    self.trackingTech = result[2]
                self.getCustomSpeedTechs(result[3])

    def getCustomFCTechs(self, prerequisite):
        if self.conn is not None and self.gameID != 0 and self.raceID != 0:
            try:
                self.c.execute(
                    f"SELECT Name, Prerequisite1, AdditionalInfo, TechSystemID FROM FCT_TechSystem WHERE Prerequisite1 = {prerequisite}")
            except Exception as err:
                print(err)
            result = self.c.fetchone()
            if result is not None:
                try:
                    self.c.execute(
                        f"SELECT TechID FROM FCT_RaceTech WHERE GameID = {self.gameID} AND RaceID = {self.raceID} AND "
                        f"TechID = {result[3]}")
                except Exception as err:
                    print(err)
                techResult = self.c.fetchone()
                if techResult is not None:
                    self.fireControlSpeedLabel.setText(result[0])
                self.getCustomFCTechs(result[3])

    def getSpeedTechs(self):
        if self.conn is not None and self.gameID != 0 and self.raceID != 0:
            try:
                self.c.execute(
                    f"SELECT TechID FROM FCT_RaceTech WHERE GameID = {self.gameID} AND RaceID = {self.raceID} AND "
                    f"TechID BETWEEN 25608 AND 25619")
            except Exception as err:
                print(err)
            results = self.c.fetchall()
            if results is not None:
                minTech = 25608
                for result in results:
                    if result[0] > minTech:
                        minTech = result[0]
                try:
                    self.c.execute(f"SELECT Name, AdditionalInfo FROM FCT_TechSystem WHERE TechSystemID = {minTech}")
                except Exception as err:
                    print(err)
                result = self.c.fetchone()
                self.trackingSpeedTechLabel.setText(result[0])
                self.trackingTech = result[1]

            try:
                self.c.execute(
                    f"SELECT TechID FROM FCT_RaceTech WHERE GameID = {self.gameID} AND RaceID = {self.raceID} AND "
                    f"TechID BETWEEN 3653 AND 3664")
            except Exception as err:
                print(err)
            results = self.c.fetchall()
            if results is not None:
                minTech = 3653
                for result in results:
                    if result[0] > minTech:
                        minTech = result[0]
                try:
                    self.c.execute(f"SELECT Name FROM FCT_TechSystem WHERE TechSystemID = {minTech}")
                except Exception as err:
                    print(err)
                result = self.c.fetchone()
                self.fireControlSpeedLabel.setText(result[0])
            self.getCustomSpeedTechs(25619)
            self.getCustomFCTechs(3664)

    def updateTurretInfo(self):
        try:
            self.weaponID = self.weaponIDs[self.weaponBox.currentText()]
        except KeyError:
            self.weaponID = 0
        if self.conn is not None and self.weaponID != 0:
            try:
                self.c.execute(
                    f"SELECT Crew, Size, Cost, ComponentValue, PowerRequirement, RechargeRate, HTK, DamageOutput, "
                    f"NumberOfShots, RangeModifier, Duranium, Neutronium, Corbomite, Tritanium, Boronide, Mercassium, "
                    f"Vendarite, Sorium, Uridium, Corundium, Gallicite FROM FCT_ShipDesignComponents WHERE GameID = "
                    f"{self.gameID} AND SDComponentID = {self.weaponID}")
            except Exception as err:
                print(err)
            results = self.c.fetchone()
            self.weapon = Weapon(results)
            # self.getSpeedTechs
            trackingTech = self.trackingTech
            try:
                gearPercent = int(self.trackingSpeedLine.text().replace(",", "")) / int(trackingTech) * 10
                gearSize = self.weapon.size * gearPercent / 100
            except ValueError:
                gearPercent = 0
                gearSize = 0
            turretCrew = self.weapon.crew
            if self.turretSingleButton.isChecked():
                turretOption = 1
            elif self.turretDoubleButton.isChecked():
                turretOption = 2
                gearSize *= 0.9
                turretCrew *= 1.8
            elif self.turretTripleButton.isChecked():
                turretOption = 3
                gearSize *= 0.85
                turretCrew *= 2.55
            else:
                turretOption = 4
                gearSize *= 0.8
                turretCrew *= 3.2
            try:
                armorCost = calcArmorCost(self.weapon.size * turretOption,
                                          int(self.armorAmountLine.text().replace(",", "")))
                armorSize = calcArmorSize(self.weapon.size * turretOption, self.armor[self.armorBox.currentText()],
                                          int(self.armorAmountLine.text().replace(",", "")))
            except ValueError:
                armorCost = 0
                armorSize = 0

            gearPercent = "%.2f" % gearPercent
            gearSize = "%.2f" % gearSize
            armorCost = "%.2f" % armorCost
            armorSize = "%.2f" % armorSize
            totalWeaponCost = "%.1f" % float(float(calcCost(self.weapon)) * turretOption)

            infoLeft1 = f"Individual Weapon Size:\n" \
                        f"Individual Weapon Cost:\n" \
                        f"Total Weapon Size:\n" \
                        f"Total Weapon Cost:\n" \
                        f"Rotation Gear(%):\n" \
                        f"Gear Size:\n" \
                        f"Armor Cost:\n" \
                        f"Armor Size:"

            infoLeft2 = f"{self.weapon.size}\n" \
                        f"{calcCost(self.weapon)}\n" \
                        f"{self.weapon.size * turretOption}\n" \
                        f"{totalWeaponCost}\n" \
                        f"{gearPercent}\n" \
                        f"{gearSize}\n" \
                        f"{armorCost}\n" \
                        f"{armorSize}"

            self.turretInfoLabelLeft1.setText(infoLeft1)
            self.turretInfoLabelLeft2.setText(infoLeft2)

            if self.weaponTypeBox.currentText() == "Gauss Cannon" or self.weaponTypeBox.currentText() == "Microwave" or self.weaponTypeBox.currentText() == "Particle Beam":
                maxRange = self.weapon.rangeMod
            else:
                maxRange = self.weapon.rangeMod * self.weapon.power
            turretSize = self.weapon.size * turretOption + float(gearSize) + float(armorSize)
            turretCost = (self.weapon.cost + float(gearSize) * 5 + float(armorCost)) * turretOption
            if self.weaponTypeBox.currentText() == "Gauss Cannon":
                rof = f"{self.weapon.componentValue}/5"
            else:
                rof = calcRoF(self.weapon)

            try:
                htk = (self.weapon.htk + int(self.armorAmountLine.text().replace(',', ''))) * turretOption
            except ValueError:
                htk = self.weapon.htk * turretOption

            infoRight1 = f"Damage Output:\n" \
                         f"Rate of Fire:\n" \
                         f"Range Modifier:\n" \
                         f"Maximum Range:\n" \
                         f"Turret Size:\n" \
                         f"HTK:\n" \
                         f"Power Requirement:\n" \
                         f"Recharge Rate:\n" \
                         f"Cost:\n" \
                         f"Crew:\n" \
                         f"Development Cost:\n\n" \
                         f"Materials Required:\n" \
                         f"Duranium:\n"

            infoRight2 = f"{self.weapon.damage}x{self.weapon.shots * turretOption}\n" \
                         f"{rof} sec\n" \
                         f"{self.weapon.rangeMod}\n" \
                         f"{maxRange} km\n" \
                         f"{'%.2f' % turretSize} HS ({round(turretSize * 50)} tons)\n" \
                         f"{htk}\n" \
                         f"{self.weapon.power * turretOption}\n" \
                         f"{int(self.weapon.rechargeRate * turretOption)}\n" \
                         f"{'%.1f' % turretCost}\n" \
                         f"{round(turretCrew)}\n" \
                         f"{round(turretCost * 10)} RP\n\n\n" \
                         f"{'%.1f' % (self.weapon.duranium * turretOption + float(gearSize) * 5)}\n"
            if float(armorCost) > 0:
                infoRight1 = infoRight1 + "Neutronium:\n"
                infoRight2 = infoRight2 + f"{armorCost}\n"
            if float(self.weapon.corbomite) > 0:
                infoRight1 = infoRight1 + "Corbomite:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.corbomite * turretOption)}\n"
            if float(self.weapon.tritanium) > 0:
                infoRight1 = infoRight1 + "Tritanium:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.tritanium * turretOption)}\n"
            if float(self.weapon.boronide) > 0:
                infoRight1 = infoRight1 + "Boronide:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.boronide * turretOption)}\n"
            if float(self.weapon.mercassium) > 0:
                infoRight1 = infoRight1 + "Mercassium:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.mercassium * turretOption)}\n"
            if float(self.weapon.vendarite) > 0:
                infoRight1 = infoRight1 + "Vendarite:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.vendarite * turretOption)}\n"
            if float(self.weapon.sorium) > 0:
                infoRight1 = infoRight1 + "Sorium:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.sorium * turretOption)}\n"
            if float(self.weapon.uridium) > 0:
                infoRight1 = infoRight1 + "Uridium:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.uridium * turretOption)}\n"
            if float(self.weapon.corundium) > 0:
                infoRight1 = infoRight1 + "Corundium:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.corundium * turretOption)}\n"
            if float(self.weapon.gallicite) > 0:
                infoRight1 = infoRight1 + "Gallicite:\n"
                infoRight2 = infoRight2 + f"{'%.1f' % (self.weapon.gallicite * turretOption)}\n"

            self.turretWeapon = Weapon([turretCrew, turretSize, turretCost, self.weapon.componentValue,
                                        self.weapon.power * turretOption,
                                        self.weapon.rechargeRate * turretOption, htk, self.weapon.damage,
                                        self.weapon.shots * turretOption, self.weapon.rangeMod,
                                        self.weapon.duranium * turretOption + float(gearSize) * 5, armorCost,
                                        self.weapon.corbomite * turretOption, self.weapon.tritanium * turretOption,
                                        self.weapon.boronide + turretOption, self.weapon.mercassium * turretOption,
                                        self.weapon.vendarite * turretOption, self.weapon.sorium * turretOption,
                                        self.weapon.uridium * turretOption, self.weapon.corundium * turretOption,
                                        self.weapon.gallicite * turretOption])
            self.turretTrackingSpeed = self.trackingSpeedLine.text()

            self.insert = True

            self.turretInfoLabelRight1.setText(infoRight1)
            self.turretInfoLabelRight2.setText(infoRight2)
        else:
            self.turretInfoLabelLeft1.setText("")
            self.turretInfoLabelLeft2.setText("")
            self.turretInfoLabelRight1.setText("")
            self.turretInfoLabelRight2.setText("")
            self.insert = False

    def spaceMasterMode(self):
        if self.spaceMaster:
            self.spaceMaster = False
            self.instantButton.setDisabled(True)
            self.armorBox.setDisabled(True)

        else:
            self.spaceMaster = True
            self.instantButton.setDisabled(False)
            self.armorBox.setDisabled(False)

    def dbInsert(self, instant):
        if self.conn is not None:
            error = False
            errorMsg = None
            try:
                self.c.execute(
                    f"SELECT MAX(TechSystemID) FROM FCT_TechSystem")
            except Exception as err:
                print(err)
            result = self.c.fetchone()
            techSystemID = result[0] + 1
            name = self.nameLine.text()
            componentName = "none"
            categoryID = self.weaponType[self.weaponTypeBox.currentText()]
            raceID = self.raceID
            techTypeID = 124
            noTechScan = 0
            ruinOnly = 0
            prerequisite = 0
            startingSystem = 0
            conventionalSystem = 0
            developCost = round(self.turretWeapon.cost * 10)
            additionalInfo = 0
            techDescription = "Race-designed Turret"
            gameID = self.gameID
            automaticResearch = 0
            sql = f"INSERT INTO FCT_TechSystem (TechSystemID, Name, ComponentName, CategoryID, RaceID, TechTypeID, " \
                  f"NoTechScan, RuinOnly, Prerequisite1, Prerequisite2, StartingSystem, ConventionalSystem, DevelopCost, " \
                  f"AdditionalInfo, AdditionalInfo2, AdditionalInfo3, AdditionalInfo4, TechDescription, GameID, " \
                  f"AutomaticResearch) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) "
            values = [techSystemID, name, componentName, categoryID, raceID, techTypeID, noTechScan,
                      ruinOnly, prerequisite, prerequisite, startingSystem, conventionalSystem, developCost,
                      additionalInfo, additionalInfo, additionalInfo, additionalInfo, techDescription, gameID,
                      automaticResearch]
            try:
                self.c.execute(sql, values)
                self.conn.commit()
            except Exception as err:
                error = True
                errorMsg = err
                print(err)
            sdComponentID = techSystemID
            noScrap = 0
            militarySystem = 1
            shippingLine = 0
            beamWeapon = 1
            componentTypeID = categoryID
            componentValue = self.turretWeapon.componentValue
            electronicSystem = 0
            electronicCTD = 0
            self.turretTrackingSpeed
            # TODO special funktion = 3 für particle beam
            specialFunction = 0
            maxSensorRange = 0
            resolution = 0
            fuelUse = 0
            noMaintFailure = 0
            hangarReloadOnly = 0
            explosionChance = 0
            maxExplosionSize = 0
            if self.weaponTypeBox.currentText() == "Particle Beam":
                maxWeaponRange = self.turretWeapon.rangeMod
            else:
                maxWeaponRange = 0
            spinalWeapon = 0
            jumpDistance = 0
            jumpRating = 0
            rateOfFire = 0
            maxPercentage = 0
            fuelEfficiency = 0
            ignoreShields = 0
            ignoreArmour = 0
            electronicOnly = 0
            stealthRating = 0
            cloakRating = 0
            weapon = 1
            try:
                self.c.execute(
                    f"SELECT BGTech1, BGTech2, BGTech3, BGTech4, BGTech5, BGTech6 FROM FCT_ShipDesignComponents WHERE "
                    f"SDComponentID = {self.weaponID}")
            except Exception as err:
                error = True
                errorMsg = str(errorMsg) + "\n" + str(err)
                print(err)
            bgTech = self.c.fetchone()
            singleSystemOnly = 0
            shipyardRepairOnly = 0
            eCCM = 0
            armourRetardation = 0
            weaponToHitMod = 1.0
            prototype = 0
            try:
                self.c.execute(
                    f"INSERT INTO FCT_ShipDesignComponents (SDComponentID, GameID, Name, NoScrap, MilitarySystem, "
                    f"ShippingLineSystem, BeamWeapon, Crew, Size, Cost, ComponentTypeID, ComponentValue, PowerRequirement,"
                    f"RechargeRate, ElectronicSystem, ElectronicCTD, TrackingSpeed, SpecialFunction, MaxSensorRange, "
                    f"Resolution, HTK, FuelUse, NoMaintFailure, HangarReloadOnly, ExplosionChance, MaxExplosionSize, "
                    f"DamageOutput, NumberOfShots, RangeModifier, MaxWeaponRange, SpinalWeapon, JumpDistance, JumpRating,"
                    f"RateOfFire, MaxPercentage, FuelEfficiency, IgnoreShields, IgnoreArmour, ElectronicOnly, StealthRating,"
                    f"CloakRating, Weapon, BGTech1, BGTech2, BGTech3, BGTech4, BGTech5, BGTech6, Duranium, Neutronium,"
                    f"Corbomite, Tritanium, Boronide, Mercassium, Vendarite, Sorium, Uridium, Corundium, Gallicite,"
                    f"SingleSystemOnly, ShipyardRepairOnly, ECCM, ArmourRetardation, WeaponToHitModifier, Prototype, "
                    f"TurretWeaponID) VALUES ({sdComponentID}, {self.gameID}, '{name}', {noScrap}, {militarySystem}, "
                    f"{shippingLine}, {beamWeapon}, {self.turretWeapon.crew}, {self.turretWeapon.size},"
                    f"{self.turretWeapon.cost}, {componentTypeID}, {componentValue}, {self.turretWeapon.power}, "
                    f"{self.turretWeapon.rechargeRate}, {electronicSystem}, {electronicCTD}, {self.turretTrackingSpeed},"
                    f"{specialFunction}, {maxSensorRange}, {resolution}, {self.turretWeapon.htk}, {fuelUse}, {noMaintFailure},"
                    f"{hangarReloadOnly}, {explosionChance}, {maxExplosionSize}, {self.turretWeapon.damage}, "
                    f"{self.turretWeapon.shots}, {self.turretWeapon.rangeMod}, {maxWeaponRange}, {spinalWeapon}, {jumpDistance},"
                    f"{jumpRating}, {rateOfFire}, {maxPercentage}, {fuelEfficiency}, {ignoreShields}, {ignoreArmour},"
                    f"{electronicOnly}, {stealthRating}, {cloakRating}, {weapon}, {bgTech[0]}, {bgTech[1]}, {bgTech[2]},"
                    f"{bgTech[3]}, {bgTech[4]}, {bgTech[5]}, {self.turretWeapon.duranium}, {self.turretWeapon.neutronium},"
                    f"{self.turretWeapon.corbomite}, {self.turretWeapon.tritanium}, {self.turretWeapon.boronide}, "
                    f"{self.turretWeapon.mercassium}, {self.turretWeapon.vendarite}, {self.turretWeapon.sorium}, "
                    f"{self.turretWeapon.uridium}, {self.turretWeapon.corundium}, {self.turretWeapon.gallicite},"
                    f"{singleSystemOnly}, {shipyardRepairOnly}, {eCCM}, {armourRetardation}, {weaponToHitMod}, {prototype},"
                    f"{self.weaponID})")
                self.conn.commit()
            except Exception as err:
                error = True
                errorMsg = str(errorMsg) + "\n" + str(err)
                print(err)
            if instant:
                try:
                    self.c.execute(f"INSERT INTO FCT_RaceTech (GameID, TechID, RaceID, Obsolete) VALUES ({self.gameID}, "
                                   f"{techSystemID}, {self.raceID}, 0)")
                    self.conn.commit()
                except Exception as err:
                    print(err)
            msgBox = QMessageBox()
            msgBox.setWindowTitle("Turret Creation")
            msgBox.setWindowIcon(QIcon("turret.png"))
            if error:
                msgBox.setIcon(QMessageBox.Critical)
                msgBox.setText("Turret Creation failed")
                msgBox.setInformativeText(str(errorMsg))
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()
            else:
                msgBox.setIcon(QMessageBox.Information)
                msgBox.setText("Turret Creation complete")
                msgBox.setStandardButtons(QMessageBox.Ok)
                msgBox.exec_()

    def dbInsertInstant(self):
        self.dbInsert(True)

    def dbInsertProject(self):
        self.dbInsert(False)

    def initUI(self):
        self.mainLayout = QGridLayout(self)
        self.dbButton = QPushButton("Choose DB", self)
        self.dbLabel = QLabel("no DB selected", self)
        self.gameLabel = QLabel("Game:", self)
        self.raceLabel = QLabel("Race:", self)
        self.weaponTypeLabel = QLabel("Weapon type:", self)
        self.weaponLabel = QLabel("Weapon:", self)
        self.gameBox = QComboBox(self)
        self.raceBox = QComboBox(self)
        self.weaponTypeBox = QComboBox(self)
        self.weaponBox = QComboBox(self)
        self.armorBox = QComboBox(self)
        self.armorLabel = QLabel("Armor:", self)
        self.trackingSpeedTechLabel = QLabel("", self)
        self.fireControlSpeedLabel = QLabel("", self)
        self.speedGroupBox = QGroupBox(self)
        self.speedLayout = QVBoxLayout(self)
        self.trackingSpeedLabel = QLabel("Desired Tracking Speed", self)
        self.trackingSpeedLine = QLineEdit("1000", self)
        self.armorAmountLabel = QLabel("Turret Armor Strength", self)
        self.armorAmountLine = QLineEdit("0", self)
        self.turretButtonsLayout = QHBoxLayout(self)
        self.turretGroupBox = QGroupBox(self)
        self.turretSingleButton = QRadioButton("Single", self)
        self.turretDoubleButton = QRadioButton("Double", self)
        self.turretTripleButton = QRadioButton("Triple", self)
        self.turretQuadButton = QRadioButton("Quad", self)
        self.turretInfoLabelRight1 = QLabel("", self)
        self.turretInfoLabelLeft1 = QLabel("", self)
        self.turretInfoLabelRight2 = QLabel("", self)
        self.turretInfoLabelLeft2 = QLabel("", self)
        self.turretInfoBox = QGroupBox(self)
        self.turretInfoLayout = QHBoxLayout(self)
        self.nameLine = QLineEdit("", self)
        self.spaceMasterButton = QPushButton("SM Mode", self)
        self.addProjectButton = QPushButton("Create", self)
        self.instantButton = QPushButton("Instant", self)
        self.buttonBoxLayout = QHBoxLayout(self)
        self.buttonBox = QGroupBox(self)
        self.nameLabel = QLabel("Name:", self)

        self.mainLayout.addWidget(self.dbButton, 0, 0)
        self.mainLayout.addWidget(self.dbLabel, 0, 1)
        self.mainLayout.addWidget(self.gameLabel, 1, 0)
        self.mainLayout.addWidget(self.gameBox, 1, 1)
        self.mainLayout.addWidget(self.raceLabel, 2, 0)
        self.mainLayout.addWidget(self.raceBox, 2, 1)
        self.mainLayout.addWidget(self.weaponTypeLabel, 3, 0)
        self.mainLayout.addWidget(self.weaponTypeBox, 3, 1)
        self.mainLayout.addWidget(self.weaponLabel, 4, 0, 1, 2)
        self.mainLayout.addWidget(self.weaponBox, 5, 0, 1, 2)
        self.mainLayout.addWidget(self.armorLabel, 6, 0)
        self.mainLayout.addWidget(self.armorBox, 6, 1)
        self.mainLayout.addWidget(self.speedGroupBox, 7, 0, 1, 2)
        self.mainLayout.addWidget(self.trackingSpeedLabel, 8, 0)
        self.mainLayout.addWidget(self.trackingSpeedLine, 8, 1)
        self.mainLayout.addWidget(self.armorAmountLabel, 9, 0)
        self.mainLayout.addWidget(self.armorAmountLine, 9, 1)
        self.mainLayout.addWidget(self.turretGroupBox, 10, 0, 1, 2)
        self.mainLayout.addWidget(self.turretInfoBox, 11, 0, 1, 2)
        self.mainLayout.addWidget(self.nameLabel, 12, 0, 1, 2)
        self.mainLayout.addWidget(self.nameLine, 13, 0, 1, 2)
        self.mainLayout.addWidget(self.buttonBox, 14, 0, 1, 2)


        self.speedLayout.addWidget(self.trackingSpeedTechLabel)
        self.speedLayout.addWidget(self.fireControlSpeedLabel)
        self.speedGroupBox.setLayout(self.speedLayout)

        self.turretInfoLayout.addWidget(self.turretInfoLabelLeft1)
        self.turretInfoLayout.addWidget(self.turretInfoLabelLeft2)
        self.turretInfoLayout.addWidget(self.turretInfoLabelRight1)
        self.turretInfoLayout.addWidget(self.turretInfoLabelRight2)
        self.turretInfoBox.setLayout(self.turretInfoLayout)

        self.turretInfoLabelLeft1.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.turretInfoLabelLeft2.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.turretInfoLabelRight1.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self.turretInfoLabelRight2.setTextInteractionFlags(Qt.TextSelectableByMouse)

        self.turretButtonsLayout.addWidget(self.turretSingleButton)
        self.turretButtonsLayout.addWidget(self.turretDoubleButton)
        self.turretButtonsLayout.addWidget(self.turretTripleButton)
        self.turretButtonsLayout.addWidget(self.turretQuadButton)
        self.turretGroupBox.setLayout(self.turretButtonsLayout)

        self.buttonBoxLayout.addWidget(self.addProjectButton)
        self.buttonBoxLayout.addWidget(self.instantButton)
        self.buttonBoxLayout.addWidget(self.spaceMasterButton)
        self.buttonBox.setLayout(self.buttonBoxLayout)

        self.turretSingleButton.setChecked(True)

        self.gameBox.setDisabled(True)
        self.raceBox.setDisabled(True)
        self.weaponTypeBox.setDisabled(True)
        self.weaponBox.setDisabled(True)
        self.armorBox.setDisabled(True)
        self.trackingSpeedLine.setDisabled(True)
        self.armorAmountLine.setDisabled(True)
        self.instantButton.setDisabled(True)

        self.weaponTypeBox.addItems(["Laser", "Particle Beam", "Railgun", "Gauss Cannon"])

        self.dbButton.clicked.connect(self.showFileChooser)
        self.gameBox.currentTextChanged.connect(self.changeRace)
        self.raceBox.currentTextChanged.connect(self.changeWeapons)
        self.raceBox.currentTextChanged.connect(self.getArmorTech)
        self.raceBox.currentTextChanged.connect(self.getSpeedTechs)
        self.weaponTypeBox.currentTextChanged.connect(self.changeWeapons)
        self.weaponBox.currentTextChanged.connect(self.updateTurretInfo)

        self.turretSingleButton.clicked.connect(self.updateTurretInfo)
        self.turretDoubleButton.clicked.connect(self.updateTurretInfo)
        self.turretTripleButton.clicked.connect(self.updateTurretInfo)
        self.turretQuadButton.clicked.connect(self.updateTurretInfo)

        self.trackingSpeedLine.textChanged.connect(self.updateTurretInfo)
        self.armorAmountLine.textChanged.connect(self.updateTurretInfo)
        self.armorBox.currentTextChanged.connect(self.updateTurretInfo)

        self.spaceMasterButton.clicked.connect(self.spaceMasterMode)
        self.instantButton.clicked.connect(self.dbInsertInstant)
        self.addProjectButton.clicked.connect(self.dbInsertProject)

        self.setLayout(self.mainLayout)

        self.setWindowTitle("TurretTool")
        self.setWindowIcon(QIcon("turret.png"))
        self.show()

        self.armor = {"Conventional Steel Armor": 1,
                      "Conventional Composite Armour": 2,
                      "Conventional Advanced Composite Armour": 3,
                      "Duranium Armour": 4,
                      "High Density Duranium Armour": 6,
                      "Composite Armour": 8,
                      "Ceramic Composite Armour": 10,
                      "Laminate Composite Armour": 12,
                      "Compressed Carbon Armour": 15,
                      "Biphase Carbide Armour": 18,
                      "Crystalline Composite Armour": 21,
                      "Superdense Armour": 25,
                      "Bonded Superdense Armour": 30,
                      "Coherent Superdense Armour": 36,
                      "Collapsium Armour": 45}
        self.weaponIDs = {}

        self.armorBox.addItems(self.armor.keys())


def main():
    app = QApplication([])
    window = Window()
    app.exec_()


if __name__ == '__main__':
    try:
        main()
    except Exception as err:
        print(err)
