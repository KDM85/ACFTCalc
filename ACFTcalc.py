import os
import sqlite3

import PySimpleGUI as sg

# ----------------------------------------------------------------
#
# Custom Fuctions
#
# ----------------------------------------------------------------


def GetAgeGroup(intAge, strGender):
    # Find the age group by gender for the entry
    if intAge < 22:
        strAgeGroup = "17-21"
    elif intAge < 27:
        strAgeGroup = "22-26"
    elif intAge < 32:
        strAgeGroup = "27-31"
    elif intAge < 37:
        strAgeGroup = "32-36"
    elif intAge < 42:
        strAgeGroup = "37-41"
    elif intAge < 47:
        strAgeGroup = "42-46"
    elif intAge < 52:
        strAgeGroup = "47-51"
    elif intAge < 57:
        strAgeGroup = "52-61"
    else:
        strAgeGroup = "62+"
    return strAgeGroup + strGender


def strTimeToSeconds(strTime):
    strSplit = strTime.split(":")
    intMin = int(strSplit[0])
    intSec = int(strSplit[1])
    intTime = intMin * 60 + intSec
    return intTime


def GetScore(strEvent, varInput, strAgeGroup):
    # Connect to the database
    strPath = os.getcwd() + "/ACFT Calculator/ACFTcalc.db"
    dbConn = sqlite3.connect(strPath)
    dbConn.row_factory = sqlite3.Row
    c = dbConn.cursor()

    if strEvent in ("SDC", "PLK", "TMR", "TMW", "OKS", "FKR", "TKB"):
        if varInput[2] != ":":
            varInput = "0" + varInput

        if strEvent == "TMW":
            strAE = "Walk"
        elif strEvent == "OKS":
            strAE = "Swim"
        elif strEvent == "FKR":
            strAE = "Row"
        elif strEvent == "TKB":
            strAE = "Bike"

    # Get Go/No-Go for alternate events
    if strEvent in ("TMW", "OKS", "FKR", "TKB"):
        strSQL = "SELECT [" + strAgeGroup + "] FROM tblAE"
        strSQL += " WHERE Event = '" + strAE + "'"
        results = c.execute(strSQL).fetchone()
        strOutput = results[0]
        c.close()
        if strTimeToSeconds(strOutput) >= strTimeToSeconds(varInput):
            intOutput = 60
        else:
            intOutput = 0
    else:
        # Build the query
        strSQL = "SELECT Points FROM tbl" + strEvent
        strSQL += " WHERE ([" + strAgeGroup + "] "
        # Set correct stack order
        if strEvent == "SDC" or strEvent == "TMR":
            strSQL += ">= ?"
        else:
            strSQL += "<= ?"
        strSQL += " AND NOT [" + strAgeGroup + "] = '')"
        # Execute query
        results = c.execute(strSQL, (varInput,)).fetchone()
        intOutput = int(results[0])
        c.close()
    return intOutput


def CalcACFT(
    intAge, strGender, intMDL, dblSPT, intHRP, strSDC, strPLK, cardio, strCardio
):
    # Calculate ACFT score
    # Find the age group and gender
    strAgeGroup = GetAgeGroup(intAge, strGender)
    # Get event scores
    intMDLScore = GetScore("MDL", intMDL, strAgeGroup)
    intSPTScore = GetScore("SPT", dblSPT, strAgeGroup)
    intHRPScore = GetScore("HRP", intHRP, strAgeGroup)
    intSDCScore = GetScore("SDC", strSDC, strAgeGroup)
    intPLKScore = GetScore("PLK", strPLK, strAgeGroup)
    if strCardio == "TMR":
        intCardioScore = GetScore("TMR", cardio, strAgeGroup)
    elif strCardio == "TMW":
        intCardioScore = GetScore("TMW", cardio, strAgeGroup)
    elif strCardio == "OKS":
        intCardioScore = GetScore("OKS", cardio, strAgeGroup)
    elif strCardio == "FKR":
        intCardioScore = GetScore("FKR", cardio, strAgeGroup)
    elif strCardio == "TKB":
        intCardioScore = GetScore("TKB", cardio, strAgeGroup)

    # Store scores in list
    strScores = [
        intMDLScore,
        intSPTScore,
        intHRPScore,
        intSDCScore,
        intPLKScore,
        intCardioScore,
    ]
    # Calculate the total score
    intTotal = (
        intMDLScore
        + intSPTScore
        + intHRPScore
        + intSDCScore
        + intPLKScore
        + intCardioScore
    )

    # Determine if all events are passed
    strPF = "Pass"
    for i in range(0, len(strScores)):
        if strScores[i] < 60:
            strPF = "Fail"
            break
    # Return results
    strScores.append(intTotal)
    strScores.append(strPF)
    return strScores


def GetMinScore(strEvent, varInput, strAgeGroup):
    # Get the minimum score for a given age
    strPath = os.getcwd() + "/ACFT Calculator/ACFTcalc.db"
    dbConn = sqlite3.connect(strPath)
    dbConn.row_factory = sqlite3.Row
    c = dbConn.cursor()
    strOutput = ""
    i = 0
    while strOutput == "":
        varInput = int(varInput) + i
        if strEvent not in ("TMW", "OKS", "FKR", "TKB"):
            strSQL = "SELECT [" + strAgeGroup + "] FROM tbl" + strEvent
            strSQL += " WHERE Points = " + str(varInput)
        else:
            # Alternate events
            if strEvent == "TMW":
                strAE = "Walk"
            elif strEvent == "OKS":
                strAE = "Swim"
            elif strEvent == "FKR":
                strAE = "Row"
            elif strEvent == "TKB":
                strAE = "Bike"
            strSQL = "SELECT [" + strAgeGroup + "] FROM tblAE"
            strSQL += " WHERE Event = '" + strAE + "'"
        results = c.execute(strSQL).fetchone()
        if results is None:
            strOutput = ""
        else:
            strOutput = results[0]
        i += 1
    c.close()
    return strOutput


# ----------------------------------------------------------------
#
# Input Validation
#
# ----------------------------------------------------------------


def ACFTvalidate(values):
    isValid = True
    strInvalidValues = []

    checkInt = ["Age", "MDL", "HRP"]
    for item in checkInt:
        try:
            int(values[item])
        except:
            strInvalidValues.append(item)
            isValid = False
    try:
        float(values["SPT"])
    except:
        strInvalidValues.append("SPT")
        isValid = False
    checkTime = ["SDC", "PLK", "Cardio"]
    for item in checkTime:
        try:
            strTimeToSeconds(values[item])
        except:
            strInvalidValues.append(item)
            isValid = False

    result = [isValid, strInvalidValues]

    return result


def MINvalidate(values):
    isValid = True
    strInvalidValues = []
    for item in ("Age", "EventScore"):
        try:
            int(values[item])
        except:
            strInvalidValues.append(item)
            isValid = False

    result = [isValid, strInvalidValues]

    return result


def GetErrorMessage(strInvalidValues):
    strMessage = ""
    for value in strInvalidValues:
        strMessage += "\nInvalid " + value
    return strMessage


# ----------------------------------------------------------------
#
# GUI
#
# ----------------------------------------------------------------

# Set theme for GUI
sg.theme("DarkGrey15")


def MainWindow():
    # Design the Score Lookup Layout
    layout = [
        [sg.Text("Age:"), sg.InputText("22", key="Age", size=(2, 1))],
        [
            sg.Text("Gender:"),
            sg.Radio("Male", "Gender", key="Gender", default=True),
            sg.Radio("Female", "Gender"),
        ],
        [
            sg.Text("MDL:"),
            sg.InputText("140", key="MDL", size=(5, 1)),
            sg.Text(key="MDLout"),
        ],
        [
            sg.Text("SPT:"),
            sg.InputText("6.3", key="SPT", size=(5, 1)),
            sg.Text(key="SPTout"),
        ],
        [
            sg.Text("HRP:"),
            sg.InputText("10", key="HRP", size=(5, 1)),
            sg.Text(key="HRPout"),
        ],
        [
            sg.Text("SDC:"),
            sg.InputText("2:31", key="SDC", size=(5, 1)),
            sg.Text(key="SDCout"),
        ],
        [
            sg.Text("PLK:"),
            sg.InputText("1:25", key="PLK", size=(5, 1)),
            sg.Text(key="PLKout"),
        ],
        [
            sg.Text("Cardio:"),
            sg.InputText("22:00", key="Cardio", size=(5, 1)),
            sg.Text(key="CardioOut"),
        ],
        [
            sg.Radio("2-mi Run", "Cardio", key="TMR", default=True),
            sg.Radio("2.5-mi Walk", "Cardio", key="TMW"),
            sg.Radio("1km Swim", "Cardio", key="OKS"),
            sg.Radio("5km Row", "Cardio", key="FKR"),
            sg.Radio("12km Bike", "Cardio", key="TKB"),
        ],
        [sg.Text("")],
        [
            sg.Text("", key="PF", size=(4, 1)),
        ],
        [
            sg.Text("", key="TotalScore", size=(16, 1)),
        ],
        [
            sg.Submit("Calculate", button_color=("black", "#229954")),
            sg.Button(
                "Find Minimums", key="FindReq", button_color=("black", "#D4AC0D")
            ),
            sg.Button("Quit", button_color=("black", "#A93226")),
        ],
    ]

    # Show the window
    window = sg.Window("ACFT Calculator", layout, element_justification="c")

    while True:
        event, values = window.read()

        if event in (sg.WIN_CLOSED, "Quit"):
            break
        elif event == "FindReq":
            window.close()
            FindMinimumsWindow()

        # Validate values
        validationResult = ACFTvalidate(values)
        if not validationResult[0]:
            strErrorMessage = GetErrorMessage(validationResult[1])
            sg.popup(strErrorMessage)
        else:
            # Prepare the query
            age = int(values["Age"])
            if values["Gender"]:
                gender = "M"
            else:
                gender = "F"
            mdl = int(values["MDL"])
            spt = float(values["SPT"])
            hrp = int(values["HRP"])
            sdc = values["SDC"]
            plk = values["PLK"]
            cardio = values["Cardio"]
            if values["TMR"]:
                cardioEvent = "TMR"
            elif values["TMW"]:
                cardioEvent = "TMW"
            elif values["OKS"]:
                cardioEvent = "OKS"
            elif values["FKR"]:
                cardioEvent = "FKR"
            elif values["TKB"]:
                cardioEvent = "TKB"

            # Execute the query
            results = CalcACFT(
                age, gender, mdl, spt, hrp, sdc, plk, cardio, cardioEvent
            )

            # Show results on the window
            window["MDLout"].update(value=str(results[0]) + " Points")
            window["SPTout"].update(value=str(results[1]) + " Points")
            window["HRPout"].update(value=str(results[2]) + " Points")
            window["SDCout"].update(value=str(results[3]) + " Points")
            window["PLKout"].update(value=str(results[4]) + " Points")
            window["CardioOut"].update(value=str(results[5]) + " Points")
            window["PF"].update(value=str(results[7]))
            window["TotalScore"].update(value="Total Score: " + str(results[6]))

    window.close()


def FindMinimumsWindow():
    # Design the Find Minimums Layout
    layout = [
        [sg.Text("Age:"), sg.InputText("22", key="Age", size=(10, 1))],
        [
            sg.Text("Gender:"),
            sg.Radio("Male", "Gender", key="Gender", default=True),
            sg.Radio("Female", "Gender"),
        ],
        [sg.Text("Event Score: "), sg.InputText("60", key="EventScore", size=(10, 1))],
        [
            sg.Radio("2-mi Run", "Cardio", key="TMR", default=True),
            sg.Radio("2.5-mi Walk", "Cardio", key="TMW"),
            sg.Radio("1km Swim", "Cardio", key="OKS"),
            sg.Radio("5km Row", "Cardio", key="FKR"),
            sg.Radio("12km Bike", "Cardio", key="TKB"),
        ],
        [sg.Text("")],
        [sg.Text("", key="MDL")],
        [sg.Text("", key="SPT")],
        [sg.Text("", key="HRP")],
        [sg.Text("", key="SDC")],
        [sg.Text("", key="PLK")],
        [sg.Text("", key="CardioOut")],
        [sg.Text("")],
        [
            sg.Submit("Show Minimums", button_color=("black", "#229954")),
            sg.Button(
                "Score Calculator", key="ScoreCalc", button_color=("black", "#D4AC0D")
            ),
            sg.Button("Quit", button_color=("black", "#A93226")),
        ],
    ]

    # Show the window
    window = sg.Window("Show Event Minimums", layout, element_justification="c")

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Quit"):
            break
        elif event == "ScoreCalc":
            window.close()
            MainWindow()

        # Validate values
        validationResult = MINvalidate(values)
        if not validationResult[0]:
            strErrorMessage = GetErrorMessage(validationResult[1])
            sg.popup(strErrorMessage)
        else:
            # Prepare the query
            if values["Gender"]:
                gender = "M"
            else:
                gender = "F"
            AgeGroup = GetAgeGroup(int(values["Age"]), gender)
            # Update the window
            window["MDL"].update(
                value="MDL: " + str(GetMinScore("MDL", values["EventScore"], AgeGroup))
            )
            window["SPT"].update(
                value="SPT: " + str(GetMinScore("SPT", values["EventScore"], AgeGroup))
            )
            window["HRP"].update(
                value="HRP: " + str(GetMinScore("HRP", values["EventScore"], AgeGroup))
            )
            window["SDC"].update(
                value="SDC: " + str(GetMinScore("SDC", values["EventScore"], AgeGroup))
            )
            window["PLK"].update(
                value="PLK: " + str(GetMinScore("PLK", values["EventScore"], AgeGroup))
            )
            if values["TMR"]:
                window["CardioOut"].update(
                    value="TMR: "
                    + str(GetMinScore("TMR", values["EventScore"], AgeGroup))
                )
            elif values["TMW"]:
                window["CardioOut"].update(
                    value="TMW: "
                    + str(GetMinScore("TMW", values["EventScore"], AgeGroup))
                )
            elif values["OKS"]:
                window["CardioOut"].update(
                    value="OKS: "
                    + str(GetMinScore("OKS", values["EventScore"], AgeGroup))
                )
            elif values["FKR"]:
                window["CardioOut"].update(
                    value="FKR: "
                    + str(GetMinScore("FKR", values["EventScore"], AgeGroup))
                )
            elif values["TKB"]:
                window["CardioOut"].update(
                    value="TKB: "
                    + str(GetMinScore("TKB", values["EventScore"], AgeGroup))
                )

    window.close()


if __name__ == "__main__":
    MainWindow()
