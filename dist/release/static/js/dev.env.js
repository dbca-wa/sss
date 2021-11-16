var env = {
    authUrl:'/sso/profile',
	appType: (window.location.protocol == "file:")?"cordova":"webapp",

    cswService:"https://csw-uat.dbca.wa.gov.au/catalogue/api/records/",
    catalogueAdminService:"https://csw-uat.dbca.wa.gov.au",

    kmiService:"https://kmi.dbca.wa.gov.au/geoserver",
    legendSrc:"https://kmi.dbca.wa.gov.au/geoserver/gwc/service/wms?REQUEST=GetLegendGraphic&VERSION=1.0.0&FORMAT=image/png&legend_options=fontName:Times%20New%20Roman;fontAntiAliasing:true;fontSize:14;bgColor:0xFFFFEE;dpi:120;labelMargin:10&LAYER=",

	hotspotService:"https://hotspots.dbca.wa.gov.au/geoserver/hotspot/ows",

    gokartService:"https://sss-dev.dbca.wa.gov.au",
    resourceTrackingService:"https://resourcetracking-uat.dbca.wa.gov.au",
    bfrsService:"https://bfrs-uat.dbca.wa.gov.au",
    staticService:"https://static.dbca.wa.gov.au",

    s3Service:"http://gokart.dpaw.io/",

    appMapping:{
        sss:"sss_dev",
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
    overviewLayer:"dbca:mapbox-outdoors",

};

document.body.onload = function() {
    var setStyle = function (){
        var leftPanel = document.getElementById("offCanvasLeft");
        if (leftPanel) {
            leftPanel.style = "background-image:url('dist/static/images/dev.svg');background-size:cover;background-repeat:no-repeat;background-position:center center;"
        } else {
            setTimeout(setStyle,500)
        }
    }
    setTimeout(setStyle,500)
}
