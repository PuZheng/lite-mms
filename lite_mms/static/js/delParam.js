function delParam(url, ref) //删除参数值
{
    var str = "";
    if (url.indexOf('?') != -1)
        str = url.substr(url.indexOf('?') + 1);
    else
        return url;
    var arr = "";
    var returnurl = "";
    if (str.indexOf('&') != -1) {
        arr = str.split('&');
        for (i in arr) {
            if (arr[i].split('=')[0] != ref) {
                returnurl = returnurl + arr

                    [i].split('=')[0] + "=" + arr[i].split('=')[1] + "&";
            }
        }
        return url.substr(0, url.indexOf('?')) + "?" +
            returnurl.substr(0, returnurl.length - 1);
    }
    else {
        arr = str.split('=');

        if (arr[0] == ref)
            return url.substr(0, url.indexOf('?'));
        else
            return url;
    }


}