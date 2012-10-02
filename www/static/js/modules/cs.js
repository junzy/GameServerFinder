function _cs_formatSecondsAsTime(totalSeconds) {
    var hours, minutes, seconds;
    hours  = Math.floor(totalSeconds / 3600);
    minutes = Math.floor((totalSeconds - (hours * 3600)) / 60);
    seconds = Math.floor(totalSeconds - (hours * 3600) -  (minutes * 60));
    if (minutes < 10) {
        minutes = "0" + minutes;
    }
    if (seconds < 10) {
        seconds  = "0" + seconds;
    }
    
    if (hours === NaN || minutes === NaN || seconds === NaN) {
        return "--:--";
    }

    if (hours > 0) {
        return (hours + ":" + minutes + ':' + seconds);
    }
    return (minutes + ':' + seconds);
}


function CSServerDisplay() {

    var _this = this;
    _this.playSound = false;
    _this.serverList = {};
    _this.audioElement = $(document.createElement("audio")).attr("src", "static/ding.wav").attr("preload", "true");
    
    _this.fillTable = function () {
        $.ajax({
          url: "JSON/cs.json",
          data: "json",
          success: function(jsonObj){
            var tableElem, trElem, tdElem,tableElem2, tbodyElem, count, divElem, newServ = false, serverList = {};
            
            tableElem = $("#CSContentTable");
            tableElem.empty();
            
            tbodyElem = $(document.createElement("tbody"));
            
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
            tbodyElem.append(trElem);
            
            count = 0;
            for (key in jsonObj) {
                if (jsonObj.hasOwnProperty(key)) {
                    if(!(key in _this.serverList)) {
                        newServ = true;
                    }
                    serverList[key] = true;
                    serverDict = jsonObj[key];
                    trElem = $(document.createElement("tr")).addClass("csRows");
                    tdElem = $(document.createElement("td")).addClass("csServerName").append(serverDict.serverName);
                    trElem.append(tdElem);
                    tdElem = $(document.createElement("td")).addClass("csServerMapName").append(serverDict.map);
                    trElem.append(tdElem);
                    tdElem = $(document.createElement("td")).addClass("csServerIP").append(serverDict.gameIP);
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
                    tbodyElem.append(trElem);
                    
                    playerList = serverDict.players;
                    if (playerList.length > 0) {
                        playerList.sort(function(a,b) { return parseFloat(b.kills) - parseFloat(a.kills) } );
                    
                        trElem = $(document.createElement("tr")).addClass("csPlayersRow");
                        tdElem = $(document.createElement("td")).addClass("csPlayersCol").attr("colspan", "7");
                        tableElem2 = $(document.createElement("table")).addClass("csPlayersTable");
                        divElem = $(document.createElement("div")).addClass("csPlayersDiv");
                        divElem.append(tableElem2)
                        tdElem.append(divElem);
                        trElem.append(tdElem);
                        tbodyElem.append(trElem);
                        
                        trElem = $(document.createElement("tr")).addClass("csPlayerRow csRows");
                        tdElem = $(document.createElement("td")).addClass("csPlayerCol").append("Player Name");
                        trElem.append(tdElem);
                        tdElem = $(document.createElement("td")).addClass("csPlayerCol").append("Player Kills");
                        trElem.append(tdElem);
                        tdElem = $(document.createElement("td")).addClass("csPlayerCol").append("Player Play Time");
                        trElem.append(tdElem);
                        tableElem2.append(trElem);

                        
                        for (var i=0; i<playerList.length; i+=1) {
                            trElem = $(document.createElement("tr")).addClass("csPlayerRow");
                            tdElem = $(document.createElement("td")).addClass("csPlayerCol").append(playerList[i].name);
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csPlayerCol").append(playerList[i].kills);
                            trElem.append(tdElem);
                            tdElem = $(document.createElement("td")).addClass("csPlayerCol").append(_cs_formatSecondsAsTime(playerList[i].time));
                            trElem.append(tdElem);
                            tableElem2.append(trElem);
                        }
                        
                    }
                    count += 1;
                }
            }
            
            if (newServ && _this.playSound) {
                _this.audioElement[0].play();
            }
            _this.serverList = serverList;
            
            if (count === 0) {
                trElem = $(document.createElement("tr")).addClass("csRows noServerRow");
                tdElem = $(document.createElement("td")).attr("colspan", "7").append("No Server Running");
                trElem.append(tdElem);
                tbodyElem.append(trElem);
            }
            tableElem.append(tbodyElem);
        }
    })};
    
    _this.refreshTable = function () {
        if (modules.cs.enabled === false) return;
        _this.fillTable();
        setTimeout(function() {_this.refreshTable();}, parseInt(modules.cs.refreshTime, 10) * 1000);
    };
    
    _this.createDiv = function () {
        var div = $(document.createElement("div")).attr("id","CSContent");
        div.append($(document.createElement("h2")).append("Counter - Strike").addClass("gameTitle csTitle").append($(document.createElement("label")).append($(document.createElement("input")).attr("type", "checkbox").attr("id","csPingCheckBox")).append("Ping for new server")));
        var table = $(document.createElement("table")).attr("id","CSContentTable").addClass("serverList");
        var tbody = $(document.createElement("tbody"));
        table.append(tbody);
        div.append(table);
        $("#mainContent").append(div);
        $("#csPingCheckBox").click(_this.toggleSound);
    };
    
    _this.toggleSound = function () {
        _this.playSound = $("#csPingCheckBox")[0].checked;
    };
    
    _this.removeDiv = function () {
        $("#CSContent").remove();
    };
    
    _this.moduleToggle = function () {
        $("#" + modules.cs.moduleName).toggleClass("gameSelected");
        if($("#" + modules.cs.moduleName).hasClass("gameSelected")) {
            modules.cs.enabled = true;
            _this.createDiv();
            _this.refreshTable();
        } else {
            modules.cs.enabled = false;
            _this.removeDiv();
        }
    };
    
    $("#" + modules.cs.moduleName).click(_this.moduleToggle);
    
    if (modules.cs.defaultEnabled) {
        $("#" + modules.cs.moduleName).addClass("gameSelected");
        modules.cs.enabled = true;
        _this.createDiv();
        _this.refreshTable();
    }
}

$(document).ready(function () {
    var worker = new CSServerDisplay();
});
