var modules = {};

$(document).ready(function () {
    "use strict";
    var mainContent, loadingDiv, gameList, fileRef, head, i;
    mainContent = $("#mainContent");
    gameList = $("#gameList");
    loadingDiv = $(document.createElement("div")).append("<img src=\"../images/loading.gif\" />").css("text-align", "center");
    mainContent.append(loadingDiv);

    fileRef = document.createElement("link");
    fileRef.setAttribute("rel", "stylesheet");
    fileRef.setAttribute("type", "text/css");
    fileRef.setAttribute("href", "static/css/themes/blackGold.css");

    head = document.getElementsByTagName('head')[0];
    head.appendChild(fileRef);

    $.ajax({
        url: "JSON/modules.json",
        data: "json",
        success: function (data) {
            mainContent.empty();

            for (i = 0; i < data.moduleList.length; i += 1) {
                var module = data.moduleList[i];
                modules[module.moduleName] = module;
                gameList.append($(document.createElement("div")).attr("id", module.moduleName).append(module.moduleTitle).addClass("gameListElement"));
                $.getScript("static/js/modules/" + module.moduleName + ".js");
            }
        }
    });
});
