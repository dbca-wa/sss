function toInt(str) {
    try {
        var result = parseInt(str)
        return Number.isNaN(result)?0:result
    } catch(ex) {
        return 0
    }
}

function convertUnit(data,unit){
    unit = unit || "px"
    if (!data) {
        return 0
    } else if (unit === "px") {
        return data
    } else if(unit === "mm") {
        return data / dpmm
    } else {
        throw "Unit '" + unit + "' Not Support"
    }
}

function getWidth(element,unit) {
    return convertUnit(element.width() 
        + toInt(element.css("padding-left")) + toInt(element.css("padding-right")) 
        + toInt(element.css("margin-left")) + toInt(element.css("margin-right")) 
        + toInt(element.css("border-width"))
        ,unit)
}

function getHeight(element,unit) {
    return convertUnit(element.height() 
        + toInt(element.css("padding-top")) + toInt(element.css("padding-bottom")) 
        + toInt(element.css("margin-top")) + toInt(element.css("margin-bottom")) 
        + toInt(element.css("border-width"))
        ,unit)
}

var hexDigits = ["0","1","2","3","4","5","6","7","8","9","a","b","c","d","e","f"]

//Function to convert rgb color to hex format
function rgb2hex(rgbColor) {
    var rgb = rgbColor.match(/^rgb\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/);
    if (rgb) {
        return "#" + hex(rgb[1]) + hex(rgb[2]) + hex(rgb[3]);
    } else {
        var rgba = rgbColor.match(/^rgba\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/);
        if (rgba) {
            var alpha = parseInt(rgba[4])
            var result = "#"
            var index = 1
            while (index < 4) {
                try {
                    result += hex( Math.round((1 - alpha) * 255 + alpha * parseInt(rgba[index]))  )
                } catch(ex) {
                    result += "00"
                }
                index += 1
            }
            return result
        }
    }
}

function hex(x) {
    return isNaN(x) ? "00" : hexDigits[(x - x % 16) / 16] + hexDigits[x % 16];
}

function getRgbColor(element,defaultColor) {
    if (!element) {
        return defaultColor
    }
    var color = $(element).css(cssName);
    if (color == null || color == undefined) {
        return defaultColor
    } else {
        color = color.trim()
        var m = null
        try {
            if (color.match(/^#[0-9a-fA-F]+$/)) {
                color = ("000000" + color.substring(1))
                color = color.substring(result.length - 6)
                return [parseInt(color.substring(0,2),16),parseInt(color.substring(2,4),16),parseInt(color.substring(4,6),16)]
            } else if (m = color.match(/^rgb\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/)) {
                return [parseInt(m[1]),parseInt(m[2]),parseInt(m[3])]
            } else if (m = color.match(/^rgba\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*([0-9\.]+)\s*\)$/)) {
                var alpha = parseFloat(m[4])
                color = [parseInt(m[1]),parseInt(m[2]),parseInt(m[3])]
                var backgroundColor = getRgbColor(element.parentElement,[255,255,255])
                return [
                    Math.round((1 - alpha) * backgroundColor[0] + alpha * color[0]),
                    Math.round((1 - alpha) * backgroundColor[1] + alpha * color[1]),
                    Math.round((1 - alpha) * backgroundColor[2] + alpha * color[2])
                ]
            return result
            } else {
                return defaultColor
            }
        } catch(ex) {
            return defaultColor
        }
    }
}

function getHexColor(element,cssName,defaultColor){
    var result = $(element).css(cssName);
    if (result == null || result == undefined) {
        return defaultColor
    } else {
        result = result.trim()
        var m = null
        if (result.match(/^#[0-9a-fA-F]+$/)) {
            return result
        } else if (m = result.match(/^rgb\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/)) {
            return "#" + hex(m[1]) + hex(m[2]) + hex(m[3]);
        } else if (m = result.match("/^rgba\((\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*\)$/")) {
            var color = getRgbColor(element,cssName,null)
            if (color) {
                return "#" + hex(color[0]) + hex(color[1]) + hex(color[2]);
            } else {
                return defaultColor
            }
        }
    }
}

function getItalic(element) {
    return $(element).css("font-style").toLowerCase() === "italic";
}

var boldNames={
    lighter:100,
    normal:400,
    bold:700,
    bolder:800,
    thicker:900
}
function getBold(element) {
    var result = $(element).css("font-weight");
    if (result in boldNames) {
        result = boldNames[result];
    } else if (isNaN(parseInt(result))) {
        result = 400;
    } else {
        result = parseInt(result)
    }
    return result >=700 
}
var textFontSizes = [
    ["xx-small",9,9],
    ["x-small",10,10],
    ["small",13,12],
    ["medium",16,14],
    ["large",18,16],
    ["larger",19,18],
    ["x-large",24,20],
    ["xx-large",32,22],
]

var titleFontSizes = [
    ["h6",16,16],
    ["h5",20,18],
    ["h4",25,21],
    ["h3",31,25],
    ["h2",40,29],
    ["h1",48,33],
]
function getFontSize(element) {
    var fontSize = $(element).css("font-size");
    var tmpSize = parseInt(fontSize);
    if (isNaN(tmpSize)) {
        fontSize = 16;
    } else {
        fontSize = tmpSize;
    }
    var index = titleFontSizes.findIndex(function(t){return t[0] === element.nodeName.toLowerCase()})
    if (index >= 0) {
        if (index === titleFontSizes.length - 1) {
            return titleFontSizes[index][2]
        } else {
            return titleFontSizes[index][2] + (titleFontSizes[index+1][2] -  titleFontSizes[index][2]) * ((fontSize - titleFontSizes[index][1]) / (titleFontSizes[index+1][1] - titleFontSizes[index][1]));
        }
    } else {
        var index = 0
        while (index < textFontSizes.length) {
            if (fontSize < textFontSizes[index][1]) {
                if (index === 0) {
                    break
                } else {
                    return textFontSizes[index - 1][2] + (textFontSizes[index][2] -  textFontSizes[index-1][2]) * ((fontSize - textFontSizes[index-1][1]) / (textFontSizes[index][1] - textFontSizes[index-1][1]));
                }
            }
            index += 1
        }
        return textFontSizes[textFontSizes.length - 1][2]
    }
}
function convertStyleToPdfStyle(element) {
    return {
        fontSize: getFontSize(element),
        color:getHexColor(element,"color","#000000"),
        bold:getBold(element), 
        italics: getItalic(element),
    }
}

function getDataUrl(image) {
    var canvas = document.createElement("canvas"),
    canvasContext = canvas.getContext("2d");

    //Set canvas size is same as the picture
    canvas.width = image.width;
    canvas.height = image.height;

    // draw image into canvas element
    canvasContext.drawImage(image, 0, 0, image.width, image.height);

    // get canvas contents as a data URL (returns png format by default)
    return canvas.toDataURL();

}

function convertHtmlToPdfContent(element,ignoreElements,content,filter) {
    content = content || [];
    $.each(element.childNodes,function(index,node){
        if (filter && !filter(node)) {
            return
        } else if (node.nodeName === "#text") {
            if (node.data.trim() === "") {
                return
            }
            content.push({
                text:node.data.trim(),
                style:convertStyleToPdfStyle(element)
            })
        } else if (node.nodeName.toUpperCase() === "IMG") {
            content.push({
                image:getDataUrl(node),
                width:Math.floor(node.width * 2 / 3),
                height:Math.floor(node.height * 2 / 3)
            })
        } else if (node.nodeName.toUpperCase() === "SCRIPT") {
            return
        } else if (node.nodeName.toUpperCase() === "LINK") {
            return
        } else if (node.nodeName.toUpperCase() === "#COMMENT") {
            return
        } else if (ignoreElements.find(function(e) {return e === node})) {
            return
        } else if (node.nodeName.toUpperCase() === "BR") {
            content.push({text:"\r\n"})
        } else if (node.nodeName.toUpperCase() === "TABLE") {
            var table = {body:[],widths:[],context:{tag:"TABLE",section:"body",rowIndex:-1,columnIndex:-1,rowSpan:[]}}
            table = convertHtmlToPdfContent(node,ignoreElements,table)
            delete table["context"]
            content.push({table:table})
        } else if (node.nodeName.toUpperCase() === "THEAD") {
            content["context"]["section"] = "head"
            content["headerRows"] = 0
            convertHtmlToPdfContent(node,ignoreElements,content)
            content["context"]["section"] = "body"
        } else if (node.nodeName.toUpperCase() === "TBODY") {
            content["context"]["section"] = "body"
            convertHtmlToPdfContent(node,ignoreElements,content)
            content["context"]["section"] = "body"
        } else if (node.nodeName.toUpperCase() === "TFOOT") {
            content["context"]["section"] = "foot"
            convertHtmlToPdfContent(node,ignoreElements,content)
            content["context"]["section"] = "body"
        } else if (node.nodeName.toUpperCase() === "TR") {
            if (content["context"]["section"] === "head") {
               content["headerRows"] += 1
            }
            //set current row index, 0 based
            content["context"]["rowIndex"] += 1
            //reset column index
            content["context"]["columnIndex"] = -1
            content["context"]["rowColor"] = getHexColor(node,"background-color",'#FFFFFF')
            //initialize row data array
            content["body"].push([])

            //process the row spans for columns at the beginning.
            while (content["context"]["rowSpan"][content["context"]["columnIndex"] + 1] > 0) {
                content["context"]["columnIndex"] += 1
                content["context"]["rowSpan"][content["context"]["columnIndex"]] -= 1
                content["body"][content["context"]["rowIndex"]].push({})
            }
            convertHtmlToPdfContent(node,ignoreElements,content)
        } else if (node.nodeName.toUpperCase() === "TD" || node.nodeName.toUpperCase() === "TH") {
            var colSpan = parseInt($(node).attr("colSpan") || 1)
            var rowSpan = parseInt($(node).attr("rowSpan") || 1)
            var index = 0
            if (content["context"]["rowIndex"] === 0) {
                //initialize the widths array
                index = 0
                while (index < colSpan) {
                    content["widths"].push(null)
                    index += 1
                }
                //initialize the context rowSpan array
                index = 0
                while (index < colSpan) {
                    content["context"]["rowSpan"].push(0)
                    index += 1
                }
            }
            //set current columnIndex, 0 based
            content["context"]["columnIndex"] += 1
            //set the widths array value
            if (colSpan === 1 && content["widths"][content["context"]["columnIndex"]] === null) {
                //set the widths to auto.
                content["widths"][content["context"]["columnIndex"]] = 'auto'
            }
            //add cell value to pdf
            var cellBody = null
            if (node.nodeName.toUpperCase() === "TH") {
                cellBody = convertHtmlToPdfContent(node,ignoreElements,[],function(node){
                    if (node.nodeName.toUpperCase() === "BR") {
                        return false
                    } else {
                        return true
                    }
                })
            } else {
                cellBody = convertHtmlToPdfContent(node,ignoreElements,[])
            }
            content["body"][content["context"]["rowIndex"]].push({stack:cellBody,colSpan:colSpan,rowSpan:rowSpan,alignment:$(node).css('text-align'),fillColor:content["context"]["rowColor"],margin:[0,0,0,0]})

            //set the context rowSpan array value
            if (rowSpan > 1) {
                index = 0
                while (index < colSpan) {
                    content["context"]["rowSpan"][content["context"]["columnIndex"] + index] = rowSpan - 1
                    index += 1
                }
            }
            //add empty column if colspan is greater than 1
            if (colSpan > 1) {
                index = 1
                while (index < colSpan) {
                    content["body"][content["context"]["rowIndex"]].push({})
                    index += 1
                }
                //set current columnIndex to the index of the last column occupied by this cell
                content["context"]["columnIndex"] += (colSpan - 1)
            }
            //add empty column if context rowSpan is greater than 1
            while (content["context"]["rowSpan"][content["context"]["columnIndex"] + 1] > 0) {
                content["context"]["columnIndex"] += 1
                content["context"]["rowSpan"][content["context"]["columnIndex"]] -= 1
                content["body"][content["context"]["rowIndex"]].push({})
            }

        } else if (node.nodeName.toUpperCase() === "UL") {
        } else if (node.nodeName.toUpperCase() === "IMG") {
        } else if ("context" in content ) {
        } else {
            convertHtmlToPdfContent(node,ignoreElements,content)
        }
    })
    return content;
}

function exportAsPdf(elementId,ignoreElementSelector,filename) {
    var rootElement = document.getElementById(elementId);

    var ignoreElements = [];
    if (ignoreElementSelector) {
        var index = 0;
        var _ignoreElements = $(ignoreElementSelector);
        while (index < _ignoreElements.length) {
            ignoreElements.push(_ignoreElements[index]);
            index += 1;
        }
    }
    var docDefinition = {
        pageSize:'A4',
        pageOrientation:'landscape',
        //pageOrientation:'portrait',
        pageMargins:[5,5,5,5],
        content:convertHtmlToPdfContent(rootElement,ignoreElements)
    }
    pdfMake.createPdf(docDefinition).download(filename);
}

function exportAs(elementId,ignoreElementsSelector,filename) {
    var pos = filename.lastIndexOf('.');
    var format = "png";
    if (pos >= 0) {
        format = filename.substring(pos + 1).toLowerCase();
    } else {
        filename = filename + "." + format;
    }
    if (format === "png") {
        try{
            if (ignoreElementsSelector) {
                $(ignoreElementsSelector).hide();
            }
            window.scroll(0,0);
            var element = $("#" + elementId)
            html2canvas(element.get(),{
                letterRendering:true,
                width:getWidth(element),
                height:getHeight(element),
                background:"#ffffff",
                onrendered:function(canvas) {
                    try{
                        canvas.toBlob(function(blob){
                            saveAs(blob,filename);
                        })
                    } catch(ex) {
                        alert(ex.message || ex)
                    } finally {
                        if (ignoreElementsSelector) {
                            $(ignoreElementsSelector).show();
                        }
                    }
                }
            })
        } catch(ex) {
            alert(ex.message || ex)
            if (ignoreElementsSelector) {
                $(ignoreElementsSelector).show();
            }
        }
    } else if (format === "pdf") {
        try{
            $("#" + elementId).addClass(elementId + "-print")
            exportAsPdf(elementId,ignoreElementsSelector,filename)
        } finally {
            $("#" + elementId).removeClass(elementId + "-print")
        }
    } else {
        alert("File format(" + format + ") Not Support")
    }
}
