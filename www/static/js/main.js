var modules = {};

$(document).ready(function () {
    var mainContent = $("#mainContent"), gameList = $("#gameList");
    var loadingDiv = $(document.createElement("div")).append("<img src=\"static/images/loading.gif\"></img>").css("text-align","center");
    mainContent.append(loadingDiv);

    $.ajax({
        url: "JSON/modules.json",
        data: "json",
        success: function (data) {
            mainContent.empty();

            for (var i=0; i<data.moduleList.length; i+=1 ) {
                var module = data.moduleList[i];
                modules[module.moduleName] = module;
                gameList.append($(document.createElement("div")).attr("id", module.moduleName).append(module.moduleTitle).addClass("gameListElement"));
                $.getScript("static/js/modules/" + module.moduleName + ".js");
            }
        }
    });
});
