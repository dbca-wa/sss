var env = {
    appType: (window.location.protocol == "file:")?"cordova":"webapp",

    cswService:"https://csw-local.dbca.wa.gov.au/catalogue/api/records/",
    catalogueAdminService:"https://csw-local.dbca.wa.gov.au",

    kmiService:"https://kmi-local.dbca.wa.gov.au/geoserver",
    legendSrc:"https://kmi-local.dbca.wa.gov.au/geoserver/gwc/service/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&legend_options=fontName:Times%20New%20Roman;fontAntiAliasing:true;fontSize:14;bgColor:0xFFFFEE;dpi:120;labelMargin:10&LAYER=",

	hotspotService:"https://hotspots.dbca.wa.gov.au/geoserver/hotspots/ows",

    gokartService:"https://sss-local.dbca.wa.gov.au",
    resourceTrackingService:"https://resourcetracking-uat.dbca.wa.gov.au",
    bfrsService:"https://bfrs-dev.dbca.wa.gov.au",
    staticService:"https://static.dbca.wa.gov.au",
    weatherForecastUrl:"https://incidentweatherforecast.service.bom.gov.au",

    s3Service:"http://gokart.dpaw.io/",

    appMapping:{
        sss:"sss_local",
    },
    layerMapping:{
        "dpaw:bushfirelist_latest"                  : "dpaw:bushfirelist_latest_dev",
        "dpaw:bushfire_latest"                      : "dpaw:bushfire_latest_dev",
        "dpaw:bushfire_final_fireboundary_latest"   : "dpaw:bushfire_final_fireboundary_latest_dev",
        "dpaw:bushfire_fireboundary_latest"         : "dpaw:bushfire_fireboundary_latest_dev",
        "dpaw:bushfire"                             : "dpaw:bushfire_dev",
        "dpaw:bushfire_fireboundary"                : "dpaw:bushfire_fireboundary_dev",
        "dpaw:resource_tracking_live"               : "dpaw:resource_tracking_live_uat",
        "dpaw:resource_tracking_history"            : "dpaw:resource_tracking_history_uat"
    },
    detailLayerMapping:{
        "dpaw:bushfirelist_latest"                  : "dpaw:bushfire_latest_dev",
    },
    overviewLayer:"cddp:dpaw_districts"

};

document.body.onload = function() {
    var setStyle = function (){
        var leftPanel = document.getElementById("offCanvasLeft");
        if (leftPanel) {
            leftPanel.style = "background-image:url('dist/static/images/local.svg');background-size:cover;background-repeat:no-repeat;background-position:center center;"
        } else {
            setTimeout(setStyle,500)
        }
    }
    setTimeout(setStyle,500)
}
