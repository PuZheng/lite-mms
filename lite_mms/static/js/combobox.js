(function ($) {
    $.widget("ui.combobox", {
        _create:function () {
            var input,
                that = this,
                select = this.element.hide(),
                selected = select.children(":selected"),
                value = selected.val() ? selected.text() : "",
                wrapper = this.wrapper = $("<span>")
                    .addClass("ui-combobox")
                    .insertAfter(select);

            function addOption(element) {
                var value = $(element).val(),
                    matcher = new RegExp("^" + $.ui.autocomplete.escapeRegex(value) + "$", "i"),
                    valid = false;
                select.children("option").each(function () {
                    if ($(this).text().match(matcher)) {
                        this.selected = valid = true;
                        return false;
                    }
                });
                if (!valid) {
                    $("option").first().val(value).text(value).attr("disabled", false);
                    //select.add();
                    select.val(value);
                    input.data("ui-autocomplete").term = value;
                    return true;
                }
            }

            input = $("<input>")
                .appendTo(wrapper)
                .val(value)
                .attr("title", "")
                .addClass("ui-state-default ui-combobox-input")
                .autocomplete({
                    delay:0,
                    minLength:0,
                    source:function (request, response) {
                        var matcher = new RegExp($.ui.autocomplete.escapeRegex(request.term), "i");
                        response(select.children("option").map(function () {
                            var text = $(this).text();
                            if (this.value && (!request.term || matcher.test(text)))
                                return {
                                    label:text.replace(
                                        new RegExp(
                                            "(?![^&;]+;)(?!<[^<>]*)(" +
                                                $.ui.autocomplete.escapeRegex(request.term) +
                                                ")(?![^<>]*>)(?![^&;]+;)", "gi"), "<strong>$1</strong>"),
                                    value:text,
                                    option:this
                                };
                        }));
                    },
                    select:function (event, ui) {
                        ui.item.option.selected = true;
                        that._trigger("selected", event, {
                            item:ui.item.option
                        });
                    },
                    change:function (event, ui) {
                        if (!ui.item)
                            return addOption(this);
                    }
                })
                .addClass("ui-widget ui-widget-content ui-corner-left");

            input.data("ui-autocomplete")._renderItem = function (ul, item) {
                return $("<li>")
                    .data("item.autocomplete", item)
                    .append("<a>" + item.label + "</a>")
                    .appendTo(ul);
            };

            $("<a>")
                .attr("tabIndex", -1)
                .attr("title", "点击查看所有选项")
                .tooltip()
                .appendTo(wrapper)
                .button({
                    icons:{
                        primary:"ui-icon-triangle-1-s"
                    },
                    text:false
                })
                .removeClass("ui-corner-all")
                .addClass("ui-corner-right ui-combobox-toggle")
                .click(function () {
                    // close if already visible
                    if (input.autocomplete("widget").is(":visible")) {
                        input.autocomplete("close");
                        addOption(input);
                        return;
                    }

                    // work around a bug (likely same cause as #5265)
                    $(this).blur();

                    // pass empty string as value to search for, displaying all results
                    input.autocomplete("search", "");
                    input.focus();
                });

            input
                .tooltip({
                    position:{
                        of:this.button
                    },
                    tooltipClass:"ui-state-highlight"
                });
        },

        destroy:function () {
            this.wrapper.remove();
            this.element.show();
            $.Widget.prototype.destroy.call(this);
        }
    });
})(jQuery);

$(function () {
    $("#combobox").combobox();
    $("span input").val("浙B ");
    $("span input").focus();
    $("#toggle").click(function () {
        $("#combobox").toggle();
    });
    $("span input").change(function(){
        var value = $(this).val();
        var patt =  /^[\u4E00-\u9FA3][a-zA-Z]\s[\w^_]{5}$/g;
        if(!patt.test(value)){
            alert("请输入正确的车牌号码，格式为汉字 + 字母 +空格+ 5位英文或者数字");
            $("span input").focus();
        }else{
            value = value.match(/^[\u4E00-\u9FA3][a-zA-Z]/g) + " " + value.split(/^[\u4E00-\u9FA3][a-zA-Z]\s?/g)[1];
            $(this).val(value);
        }
    });
    $("button:submit").click(function () {
            if ($("#combobox").val() == "") {
                alert("车牌号码不能为空");
                return false;
            }
        }
    );
});

