var dojoConfig = {
    baseUrl: ".",
    tlmSiblingOfDojo: false,
    packages: [
        { name: "dojo", location: "dojo" },
        { name: "dijit", location: "dijit" },
        { name: "dojox", location: "dojox" },
        { name: "modules", location: "modules", main: "" }
    ]
};

require([
  "dojo/dom",
  "dojo/ready",
  "dojo/dom-construct",
  "dojo/on",
  "dojo/dom-class",
  "dojo/_base/xhr",
  "dojo/domReady!",
  "dojox/widget/Toaster"
], function(dom, ready, domConstruct, on, domClass, xhr) {
  
var activatedModules = {}, moduleList = {};

var notify = new dojox.widget.Toaster({
  messageTopic: '/app/notify',
  positionDirection: 'tr-down',
  duration: 5000
});

function gameSelectionChange(element) {
  var clickedElementId = element.target.id;
  if (activatedModules.clickedElementId === true) {
    activatedModules.clickedElementId = false;
    domClass.remove(clickedElementId, "gameSelected");
    
    //TODO: Stop Module
  } else {
    activatedModules.clickedElementId = true;
    domClass.add(clickedElementId, "gameSelected");

    //TODO: Start Module
  }
}

ready(function() {
  var mainContent = dom.byId("mainContent");
  var gameList = dom.byId("gameList");
  
  var loadingDiv = domConstruct.create("div", {innerHTML: "<img src=\"static/loading.gif\"></img>", style:"text-align:center"});
  domConstruct.place(loadingDiv, mainContent)
  
  xhr.get({
    url: "JSON/modules.json",
    handleAs: "json",
    load: function(data){
      availableGameList = data["moduleList"];
      
      domConstruct.empty(mainContent);
      for (var i=0; i<availableGameList.length; i+=1 ) {
        module = availableGameList[i];
        moduleList[module["moduleName"]] = module;

        var classList = "gameListElement";
        
        if (module["defaultEnabled"] === true) {
          classList += " gameSelected";
          activatedModules[module["moduleName"]] = true;
          
          //TODO: Start Module
        }
        
        var gameListElement = domConstruct.create("div", {id: module["moduleName"] , innerHTML: module["moduleTitle"], class: classList});
        
        domConstruct.place(gameListElement, gameList);
        on(dom.byId(module["moduleName"]), "click", gameSelectionChange);
      }
      
    },
    error: function(error){
      dojo.publish('/app/notify', ["Couldn't retrive a list of availables modules"]);
    }
  });
});

});
