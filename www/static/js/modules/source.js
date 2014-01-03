function formatSecondsAsTime(totalSeconds) {
    "use strict";
    var hours, minutes, seconds, finalStr;
    hours  = Math.floor(totalSeconds / 3600);
    minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
    seconds = Math.floor(totalSeconds - (hours * 3600) -  (minutes * 60));

/*    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (seconds < 10) {
        seconds  = "0" + seconds;
    }
*/
    if (isNaN(hours) || isNaN(minutes) || isNaN(seconds)) {
        return "--:--";
    }

    if (hours > 0) {
        finalStr = hours + " hrs, " + minutes + ' mins, ' + seconds + " secs";
    } else if (minutes > 0) {
        finalStr = minutes + ' mins, ' + seconds + " secs";
    } else {
        finalStr = seconds + " secs";
    }

    return finalStr;
}

function CSServerDisplay() {
    "use strict";
    var playSound, serverList, audioElement, moduleDiv, fillTable, refreshTable, toggleSound, removeDiv, createDiv, moduleToggle;
    playSound = false;
    serverList = {};
    audioElement = $(document.createElement("audio")).attr("src", "static/ding.wav").attr("preload", "true");
    moduleDiv = $("#" + modules.cs.moduleName);

    fillTable = function () {
        $.ajax({
            url: "JSON/cs.json",
            data: "json",
            cache: false,
            success: function (jsonObj) {
                var tableElem, trElem, tdElem, tableElem2, tBodyElem, count, divElem, newServer = false,
                    serverDict, key, sortFunc, playerList, i;

                sortFunc = function (a, b) { return parseFloat(b.kills) - parseFloat(a.kills); };

                tableElem = $("#CSContentTable");
                tableElem.empty();

                tBodyElem = $(document.createElement("tbody"));

                trElem = $(document.createElement("tr")).addClass("csTopRow");
                tdElem = $(document.createElement("td")).addClass("csServerName").append("Server Name");
                trElem.append(tdElem);
                tdElem = $(document.createElement("td")).addClass("csServerMapName").append("Map");
                trElem.append(tdElem);
                tdElem = $(document.createElement("td")).addClass("csServerIP").append("IP");
                trElem.append(tdElem);
                tdElem = $(document.createElement("td")).addClass("csServerLatency").append("Latency");
                trElem.append(tdElem);
                tdElem = $(document.createElement("td")).addClass("csServerPlayer").append("Players");
                trElem.append(tdElem);
                tdElem = $(document.createElement("td")).addClass("csServerPassword").append("Password");
                trElem.append(tdElem);
                tdElem = $(document.createElement("td")).addClass("csServerVersion").append("Version");
                trElem.append(tdElem);
                tBodyElem.append(trElem);

                count = 0;
                if (jsonObj !== "undefined") {
                    for (key in jsonObj) {
                        if (jsonObj.hasOwnProperty(key)) {
                            if (!serverList.hasOwnProperty(key)) {
                                newServer = true;
                            }
                            serverDict = jsonObj[key];
                            serverList[key] = true;
                            trElem = $(document.createElement("tr")).addClass("csRows");
                            tdElem = $(document.createElement("td")).addClass("csServerName").append(serverDict.serverName);
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csServerMapName").append(serverDict.map);
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csServerIP").append(key);
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csServerLatency").append(serverDict.latency + " ms");
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csServerPlayer").append(serverDict.numPlayers + "/" + serverDict.maxPlayers);
                            trElem.append(tdElem);
                            if (serverDict.passworded === 1) {
                                tdElem = $(document.createElement("td")).addClass("csServerPassword").append("Yes");
                            } else {
                                tdElem = $(document.createElement("td")).addClass("csServerPassword").append("No");
                            }
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csServerVersion").append(serverDict.version);
                            trElem.append(tdElem);
                            tBodyElem.append(trElem);

                            playerList = serverDict.players;
                            if (playerList.length > 0) {
                                playerList.sort(sortFunc);

                                trElem = $(document.createElement("tr")).addClass("csPlayersRow");
                                tdElem = $(document.createElement("td")).addClass("csPlayersCol").attr("colspan", "7");
                                tableElem2 = $(document.createElement("table")).addClass("csPlayersTable");
                                divElem = $(document.createElement("div")).addClass("csPlayersDiv");
                                divElem.append(tableElem2);
                                tdElem.append(divElem);
                                trElem.append(tdElem);
                                tBodyElem.append(trElem);

                                for (i = 0; i < playerList.length; i += 1) {
                                    trElem = $(document.createElement("tr")).addClass("csPlayerRow");
                                    tdElem = $(document.createElement("td")).addClass("csPlayerCol").append(playerList[i].name);
                                    trElem.append(tdElem);
                                    tdElem = $(document.createElement("td")).addClass("csPlayerCol").append(playerList[i].kills + " Kills");
                                    trElem.append(tdElem);
                                    tdElem = $(document.createElement("td")).addClass("csPlayerCol").append(formatSecondsAsTime(playerList[i].time));
                                    trElem.append(tdElem);
                                    tableElem2.append(trElem);
                                }

                            }
                            count += 1;
                        }
                    }
                }

                if (newServer && playSound) {
                    audioElement[0].play();
                }

                if (count === 0) {
                    trElem = $(document.createElement("tr")).addClass("csRows noServerRow");
                    tdElem = $(document.createElement("td")).attr("colspan", "7").append("No Server Running");
                    trElem.append(tdElem);
                    tBodyElem.append(trElem);
                }
                tableElem.append(tBodyElem);
            }
        });
    };

    refreshTable = function () {
        if (modules.cs.enabled === false) { return null; }
        fillTable();
        setTimeout(function () { refreshTable(); }, parseInt(modules.cs.refreshTime, 10) * 1000);
    };

    createDiv = function () {
        var div, table, tBody;
        div = $(document.createElement("div")).attr("id", "CSContent");
        div.append($(document.createElement("h2")).append("Counter - Strike").addClass("gameTitle csTitle").append($(document.createElement("label")).append($(document.createElement("input")).attr("type", "checkbox").attr("id", "csPingCheckBox")).append("Ping for new server")));
        table = $(document.createElement("table")).attr("id", "CSContentTable").addClass("serverList");
        tBody = $(document.createElement("tbody"));
        table.append(tBody);
        div.append(table);
        $("#body").append(div);
        $("#csPingCheckBox").click(toggleSound);
    };

    toggleSound = function () {
        playSound = $("#csPingCheckBox")[0].checked;
    };

    removeDiv = function () {
        $("#CSContent").remove();
    };

    moduleToggle = function () {

        moduleDiv.toggleClass("gameSelected");
        if (moduleDiv.hasClass("gameSelected")) {
            modules.cs.enabled = true;
            createDiv();
            refreshTable();
        } else {
            modules.cs.enabled = false;
            removeDiv();
        }
    };

    moduleDiv.click(moduleToggle);

    if (modules.cs.defaultEnabled) {
        moduleDiv.addClass("gameSelected");
        modules.cs.enabled = true;
        createDiv();
        refreshTable();
    }
}

$(document).ready(CSServerDisplay);
