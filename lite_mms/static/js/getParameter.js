/**
 * Created with PyCharm.
 * User: wangjiali
 * Date: 13-1-28
 * Time: 上午10:25
 * To change this template use File | Settings | File Templates.
 */
function getParameter(name) {
    var url = location.href;
    var start = url.indexOf("?")+1;
    if (start==0) {
        return "";
    }
    var value = "";
    var queryString = url.substring(start);
    var paraNames = queryString.split("&");
    for (var i=0; i<paraNames.length; i++) {
        if (name==getParameterName(paraNames[i])) {
            value = getParameterValue(paraNames[i])
        }
    }
    return value;
}

function getParameterName(str) {
    var start = str.indexOf("=");
    if (start==-1) {
        return str;
    }
    return str.substring(0,start);
}

function getParameterValue(str) {
    var start = str.indexOf("=");
    if (start==-1) {
        return "";
    }
    return str.substring(start+1);
}
