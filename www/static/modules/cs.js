define ([
  "dojo/dom",
  "dojo/domConstruct",
  "dojo/_base/declare",
  "dojo/query",
], function(dom, domConstruct, declare, query) {

declare("modules.cs", null, {
  jsonURL : "../../JSON/cs.json",
  divId : "csDiv",
  refreshTime : 1000,
  enabled : false,
  
  _fillCSTable : function() {
    dojo.xhrGet(
      url: this.jsonURL,
      handleAs: "json",
      load: function(jsonObj){
        var tbody = query(divId + "Table" + " tbody")[0];
        tbodyElem = dom.Byid(divId + "Table");
        domConstruct.empty(tbody);

        jsonDict = jsonObj["serverList"];
/*        trElem = tbodyElem.insertRow(tbodyElem.rows.length);
        trElem.className = "csTopRow";
        tdElem = trElem.insertCell(trElem.cells.length);
        tdElem.innerHTML = jsonDict["serverName"];
        tdElem.className = "csServerName";
        tdElem = trElem.insertCell(trElem.cells.length);
        tdElem.innerHTML = jsonDict["serverMapName"];
        tdElem.className = "csServerMapName";
        tdElem = trElem.insertCell(trElem.cells.length);
        tdElem.innerHTML = jsonDict["serverIP"];
        tdElem.className = "csServerIP";
        tdElem = trElem.insertCell(trElem.cells.length);
        tdElem.innerHTML = jsonDict["serverLatency"];
        tdElem.className = "csServerLatency";
        tdElem = trElem.insertCell(trElem.cells.length);
        tdElem.innerHTML = jsonDict["serverPlayer"];
        tdElem.className = "csServerPlayer";
        tdElem = trElem.insertCell(trElem.cells.length);
        tdElem.innerHTML = "Player List";
        tdElem.className = "csServerPlayerList";

        if (jsonObj.length === 1) {
          trElem = tbodyElem.insertRow(tbodyElem.rows.length);
          trElem.className = "csRows noServerRow";
          tdElem = trElem.insertCell(trElem.cells.length);
          tdElem.innerHTML = "No Server Running";
          tdElem.colSpan = "6";
        }
        else {
          for (var i = 1; i < jsonObj.length ; i++){
            jsonDict = jsonObj[i];
            trElem = tbodyElem.insertRow(tbodyElem.rows.length);
            trElem.className = "csRow";
            tdElem = trElem.insertCell(trElem.cells.length);
            tdElem.innerHTML = jsonDict["serverName"];
            tdElem = trElem.insertCell(trElem.cells.length);
            tdElem.innerHTML = jsonDict["serverMapName"];
            tdElem = trElem.insertCell(trElem.cells.length);
            tdElem.innerHTML = jsonDict["serverIP"];
            tdElem = trElem.insertCell(trElem.cells.length);
            tdElem.innerHTML = jsonDict["serverLatency"] + " ms";
            tdElem = trElem.insertCell(trElem.cells.length);
            tdElem.innerHTML = jsonDict["serverPlayer"] + "/" + jsonDict["serverPlayerMax"];
            tdElem = trElem.insertCell(trElem.cells.length);
            tdElem.innerHTML = "&lt;Not Yet Implemented&gt;";
          }
        }*/
     },
     error: function() {
     
     });
    },

    _refreshCSTable : function() {
        fillCSTable();
        setTimeout("refreshCSTable()", this.refreshTime);
    },
    
    _createDiv : function() {
      var div = domConstruct("div", {id: divId});
      var table = domConstruct("table", {id: divId + "Table"});
      var tbody = domConstruct("tbody");
      domConstruct.place(table, tbody);
      domConstruct.place(div, table);
      domConstruct.place(dom.byId("mainContent"), div);
    },
    
    _removeDiv : function() {
      domConstruct.destroy(divId);
    },
    
    startModule : function() {
      this.enabled = true;
      this._createDiv();
      
      this._refreshCSTable();
    },
    
    stopModule: function() {
      this.enabled = false;
      this._removeDiv();
    }
  });
});
