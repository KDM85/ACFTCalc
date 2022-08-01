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


def GetScore(strEvent, varInput, strAgeGroup):
    # Connect to the database
    strPath = os.getcwd() + "/ACFT Calculator/ACFTcalc.db"
    dbConn = sqlite3.connect(strPath)
    dbConn.row_factory = sqlite3.Row
    c = dbConn.cursor()

    if strEvent == "SDC" or strEvent == "PLK" or strEvent == "TMR":
        if varInput[2] != ":":
            varInput = "0" + varInput

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


def StrTimeToSeconds(strTime):
    # Convert mm:ss string to integer seconds
    # Handle null
    if len(strTime) == 0 or strTime is None:
        return 0
        quit()
    # Find the colon in the string
    intColonLoc = strTime.find(":")
    intMinutes = int(strTime[:intColonLoc])
    intSeconds = int(strTime[-2 : len(strTime)])
    # Return total seconds
    return intSeconds + (intMinutes * 60)


def SecondsToStrTime(intTime):
    # Convert integer seconds to mm:ss string
    intMinutes = int(intTime / 60)
    strMinutes = str(intMinutes).format("00")
    intSeconds = intTime - (intMinutes * 60)
    strSeconds = str(intSeconds).format("00")
    # Build string
    strOutput = strMinutes + ":" + strSeconds
    return strOutput


def CalcACFT(intAge, strGender, intMDL, dblSPT, intHRP, strSDC, strPLK, strTMR):
    # Calculate ACFT score
    # Find the age group and gender
    strAgeGroup = GetAgeGroup(intAge, strGender)
    strEvents = ["MDL", "SPT", "HRP", "SDC", "PLK", "TMR"]
    # Get event scores
    intMDLScore = GetScore("MDL", intMDL, strAgeGroup)
    intSPTScore = GetScore("SPT", dblSPT, strAgeGroup)
    intHRPScore = GetScore("HRP", intHRP, strAgeGroup)
    intSDCScore = GetScore("SDC", strSDC, strAgeGroup)
    intPLKScore = GetScore("PLK", strPLK, strAgeGroup)
    intTMRScore = GetScore("TMR", strTMR, strAgeGroup)
    # Store scores in list
    strScores = [
        intMDLScore,
        intSPTScore,
        intHRPScore,
        intSDCScore,
        intPLKScore,
        intTMRScore,
    ]
    # Calculate the total score
    intTotal = (
        intMDLScore
        + intSPTScore
        + intHRPScore
        + intSDCScore
        + intPLKScore
        + intTMRScore
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
    strSQL = "SELECT [" + strAgeGroup + "] FROM tbl" + strEvent
    strSQL += " WHERE Points = " + varInput
    results = c.execute(strSQL).fetchone()
    strOutput = results[0]
    c.close()
    return strOutput


# ----------------------------------------------------------------
#
# Input Validation
#
# ----------------------------------------------------------------


def validInt(varInput):
    # Check if input is an integer
    try:
        int(varInput)
        return True
    except ValueError:
        return False


def validFloat(varInput):
    # Check if input is a float
    try:
        float(varInput)
        return True
    except ValueError:
        return False


def validTime(varInput):
    # Check if input is a time
    if StrTimeToSeconds(varInput) > 0:
        return True
    else:
        return False


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
        [sg.Text("Age:"), sg.InputText("22", key="Age", size=(10, 1))],
        [
            sg.Text("Gender:"),
            sg.Radio("Male", "Gender", key="Gender", default=True),
            sg.Radio("Female", "Gender"),
        ],
        [
            sg.Text("MDL:"),
            sg.InputText("140", key="MDL", size=(10, 1)),
            sg.Text(size=(10, 1), key="MDLout"),
        ],
        [
            sg.Text("SPT:"),
            sg.InputText("7.8", key="SPT", size=(10, 1)),
            sg.Text(size=(10, 1), key="SPTout"),
        ],
        [
            sg.Text("HRP:"),
            sg.InputText("10", key="HRP", size=(10, 1)),
            sg.Text(size=(10, 1), key="HRPout"),
        ],
        [
            sg.Text("SDC:"),
            sg.InputText("2:31", key="SDC", size=(10, 1)),
            sg.Text(size=(10, 1), key="SDCout"),
        ],
        [
            sg.Text("PLK:"),
            sg.InputText("1:31", key="PLK", size=(10, 1)),
            sg.Text(size=(10, 1), key="PLKout"),
        ],
        [
            sg.Text("TMR:"),
            sg.InputText("19:31", key="TMR", size=(10, 1)),
            sg.Text(size=(10, 1), key="TMRout"),
        ],
        [sg.Text("")],
        [
            sg.Text("", key="PF", size=(10, 1)),
        ],
        [
            sg.Text("", key="TotalScore", size=(15, 1)),
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
    window = sg.Window("ACFT Calculator", layout)

    while True:
        event, values = window.read()

        # Validate values
        if event in (sg.WIN_CLOSED, "Quit"):
            break
        elif event == "FindReq":
            window.close()
            FindMinimumsWindow()
        checkInt = ["Age", "MDL", "HRP"]
        for item in checkInt:
            if not validInt(values[item]):
                window[item].update(value="")
        if not validFloat(values["SPT"]):
            window["SPT"].update(value="")
        checkTime = ["SDC", "PLK", "TMR"]
        for item in checkTime:
            if not validTime(values[item]):
                window[item].update(value="")

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
        tmr = values["TMR"]

        # Execute the query
        results = CalcACFT(age, gender, mdl, spt, hrp, sdc, plk, tmr)

        # Show results on the window
        window["MDLout"].update(value=str(results[0]) + " Points")
        window["SPTout"].update(value=str(results[1]) + " Points")
        window["HRPout"].update(value=str(results[2]) + " Points")
        window["SDCout"].update(value=str(results[3]) + " Points")
        window["PLKout"].update(value=str(results[4]) + " Points")
        window["TMRout"].update(value=str(results[5]) + " Points")
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
        [sg.Text("")],
        [sg.Text("", key="MDL", size=(10, 1))],
        [sg.Text("", key="SPT", size=(10, 1))],
        [sg.Text("", key="HRP", size=(10, 1))],
        [sg.Text("", key="SDC", size=(10, 1))],
        [sg.Text("", key="PLK", size=(10, 1))],
        [sg.Text("", key="TMR", size=(10, 1))],
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
    window = sg.Window("Show Event Minimums", layout)

    while True:
        event, values = window.read()
        if event in (sg.WIN_CLOSED, "Quit"):
            break
        elif event == "ScoreCalc":
            window.close()
            MainWindow()
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
        window["TMR"].update(
            value="TMR: " + str(GetMinScore("TMR", values["EventScore"], AgeGroup))
        )

    window.close()


if __name__ == "__main__":
    MainWindow()
