var WorkFlowRepr = function (canvas, tree, width, height) {
    this.canvas = canvas;
    this.tree = tree;
    this.width = width? width: 960;
    this.height = height? height: 640;
}

WorkFlowRepr.prototype.margin = 60;
WorkFlowRepr.prototype.lifeCycleLineWidth = 5;

function _getNodeCount(tree) {
    if (!tree) {
        return 0;
    }
    var ret = 1;
    for (group in tree.childrenGroups) {
        for (children in group.items()) {
            ret += _getNodeCount(children);
        }
    }
    return ret;
}

_traversTree = function(tree) {
    var ret = [];
    function _doTraverseTree(subTree, list) {
        if (!subTree) {
            return;
        }
        list.push(subTree);
        if (subTree.hasOwnProperty('childrenGroups')) {
            for (var i=0; i < subTree.childrenGroups.length; ++i) {
                var group = subTree.childrenGroups[i];
                for (var j=0; j < group.items.length; ++j) {
                    var children = group.items[j];
                    children.parent_ = subTree;
                    _doTraverseTree(children, list)
                }
            }
        }
    };
    _doTraverseTree(tree, ret);
    return ret;
};

WorkFlowRepr.prototype.draw = function () {
    var nodes = _traversTree(this.tree);
    var steps = (this.height - 2 * this.margin) / nodes.length;
    var drawableWidth = this.width - 2 * this.margin;

    var draw = SVG(this.canvas).size(this.width, this.height);
    // draw the swim lane
    var firstNode = nodes[0];
    var beginTime = new Date(firstNode.events[0].datetime);
    var endTime = new Date("1970-01-01T00:00:00");
    for (var i=0; i < nodes.length; ++i) {
        var node = nodes[i];
        node.idx = i;
        var x = this.margin;
        var y = this.margin + i * steps;
        for (var j=x; j < x + drawableWidth; j += 10) {
            draw.line(j, y, j + 5, y).stroke({width: 1, color: 'grey'});
        }
        
        var text = draw.text(node.name).move(x, y - 30).font({
            size: 20,
            anchor: 'top',
        }).attr({
            'data-ot': node.description,
            'data-role': 'node-name'
        }).fill({color: 'gray'});
        text.click((function (target) {
            return function () {
                window.open(target); 
            }
        })(node.target));
        var node_begin_time = new Date(node.events[0].datetime);
        var node_end_time = new Date(node.events[node.events.length-1].datetime); 
        if (node_begin_time < beginTime) {
            beginTime = node_begin_time;
        }
        if (node_end_time > endTime) {
            endTime = node_end_time;
        }
    }
    var timespan = endTime.getTime() - beginTime.getTime();


    function _calcEventPos(event_) {
        return drawableWidth * (new Date(event_.datetime).getTime() - beginTime.getTime()) / timespan;
    }

    var lifeCycleLayer = [];

    var eventDiameter = 10;
    for (var i=0; i < nodes.length; ++i) {
        var node = nodes[i];
        for (var j=0; j < node.events.length; ++j) {
            var event_ = node.events[j];
            var eventPoint = [this.margin + _calcEventPos(event_), this.margin + i * steps];
            if (j==0) {
                var start = eventPoint;
            }
            var circle = draw.circle(eventDiameter).center(eventPoint[0], eventPoint[1]).fill({color: 'green'}).attr({
                'data-actor': event_.actor,
                'data-datetime': event_.datetime,
                'data-name': event_.name,
                'data-placement': 'bottom',
                'data-trigger': 'hover',
                'data-content': event_.description
            });
            circle.mouseover((function (eventPoint) { 
                return function (event) {
                    this.scale(2, 2).center(eventPoint[0], eventPoint[1]);
                    this.fill({color: 'red'});
                }
            })(eventPoint));
            circle.mouseleave((function (eventPoint) {
                return function (event) {
                    this.scale(1, 1).center(eventPoint[0], eventPoint[1]).fill({color: 'green'});
                } 
            })(eventPoint))
            var textPoint = [eventPoint[0], eventPoint[1] + 5];
            if (j & 1) {
                textPoint[1] -= 40;
            }
            var d = new Date(event_.datetime);
            function pad(n){
                return n<10 ? '0'+n : n
            } 
            var dateString = '';
            if (!(lastDate && lastDate.year == d.getUTCFullYear() && lastDate.month == d.getUTCMonth() && lastDate.day == d.getUTCDate())) {
                dateString += pad(d.getUTCMonth()+1) + '-' + pad(d.getUTCDate())+' ';
            }
            dateString += pad(d.getUTCHours()) + ':' + pad(d.getUTCMinutes())
                var lastDate = {
                    year: d.getUTCFullYear(),
                    month: d.getUTCMonth(),
                    day: d.getUTCDate(),
                };
            draw.text(event_.name+"\n"+dateString).move(textPoint[0], textPoint[1]).font({
                size: 13,
                anchor: 'middle',
            });
        }
        var line = draw.line(start[0], start[1], eventPoint[0], eventPoint[1]).stroke({color: 'lightblue', width: this.lifeCycleLineWidth}).attr({
            'data-role': 'life-cycle',
            'data-ot': node.description,
        });
        line.mouseover((function (line_width) {
            return function (event) {
            this.stroke({width: line_width * 2});
            }
        })(this.lifeCycleLineWidth));
        line.mouseleave((function (line_width) {
            return function (event) {
            this.stroke({width: line_width});
            }
        })(this.lifeCycleLineWidth));
        lifeCycleLayer.push(line); 
        // draw branches
        var childCnt = 0;
        for (var j=0; j < node.childrenGroups.length; ++j) {
            var group = node.childrenGroups[j];
            for (var k=0; k < group['items'].length; ++k) {
                var child_node = group['items'][k];
                var y1 = this.margin + child_node.idx * steps;
                var y2 = this.margin + node.idx * steps;
                var x1 = x2 = this.margin + _calcEventPos(child_node.events[0]);
                var path = 'M' + x2 + ',' + y2 + ' ';
                path += 'A' + (childCnt * 25) + ',' + (y1 - y2)/2 + ' ';
                path += '0 ';
                path += '0,0 ';
                path += x1 + ',' + (y1 - eventDiameter);
                draw.path(path, true).stroke({width: 1}).fill('none').attr('marker-end', 'url(#Triangle)');
                ++childCnt;
            }
        }
    }
    for (var i=0; i < lifeCycleLayer.length; ++i) {
        lifeCycleLayer[i].back();
    }
    $('text[data-role="node-name"], line[data-role="life-cycle"], ellipse').each(function () {
        if ($(this).attr('data-ot')) {
            new Opentip($(this), $(this).attr('data-ot'));
        }
   });

    var svgNode = document.getElementsByTagName('svg')[0];
    var defs = svgNode.getElementsByTagName('defs')[0];
    var marker = document.createElementNS('http://www.w3.org/2000/svg', 'marker');
    marker.setAttribute('id', 'Triangle');
    marker.setAttribute('refX', '5');
    marker.setAttribute('refY', '5');
    marker.setAttribute('markerWidth', '14');
    marker.setAttribute('markerHeight', '13');
    marker.setAttribute('orient', 'auto');
    var path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
    marker.appendChild(path);
    path.setAttribute('d', 'M 0 0 L 10 5 L 0 10 z');
    svgNode.appendChild(defs);
    defs.appendChild(marker);
}
