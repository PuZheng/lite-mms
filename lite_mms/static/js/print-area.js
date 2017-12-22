(function(root, factory) {
    if (typeof define === 'function' && define.amd) {
        define([], factory);
    } else if (typeof exports === 'object') {
        module.exports = factory();
    } else {
        root.printArea = factory();
    }
}(this, function() {
    'use strict';
    function extractHead() {
        return Array.prototype.slice.apply(document.querySelectorAll('link'), [0])
            .filter(function(el){
                return el.getAttribute("rel").toLowerCase() == "stylesheet";
            })
            .map(function(el){
                return '<link type="text/css" rel="stylesheet" href="' + el.getAttribute("href") + '" >';
            })
            .join('');
    }
    function printArea(el) {
        const head = extractHead();
        console.log(head);
        const iframe = document.createElement('iframe');
        document.body.appendChild(iframe);
        iframe.setAttribute('style', [
            ['border', 0],
            ['position', 'absolute'],
            ['width', 0],
            ['height', 0],
            ['left', 0],
            ['top', 0],
        ].map(p => p.join(':')).join(';'));
        iframe.setAttribute('src', '');
        iframe.setAttribute('id', new Date().getTime());
        if (iframe.contentDocument) {
            iframe.doc = iframe.contentDocument;
        } else if (iframe.contentWindow)  {
            iframe.doc = iframe.contentWindow.document;
        } else {
            iframe.doc = iframe.document;
        }
        (function(doc) {
            doc.open();
            doc.write('<html><head>' + head + '</head><body>' + el.outerHTML + '</body></html>')
            doc.close();
        }(iframe.doc));


        setTimeout((function(pw) {
            return function () {
                pw.focus();
                pw.print();
            };
        }(iframe.contentWindow || f)), 1000);
    }
    return printArea;
}));
