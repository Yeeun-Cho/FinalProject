var suggestions = $('.suggestions-box');
var allStocks;

$(document).ready(function() {
    suggestions.hide();
    getStocksInfo()
});

$('.search').on('keyup', function() {
    sub = $('.search').val();
    tbody = $('.suggestions-box > tbody');
    tbody.empty()
    if (sub) {
        suggestions.show()
        search = allStocks.filter(stock => searchStock(stock, sub))
        for (var i = 0; i < Math.min(search.length, 10); i++) {
            suggestTickerHTML = make_bold(search[i][0], sub)
            suggestCompanyHTML = make_bold(search[i][1], sub)
            var $tr = $('<tr class="stock"></tr>')
            var $suggestTicker = $('<td class="ticker">' + suggestTickerHTML + '</td>')
            var $suggestCompany = $('<td class="company">' + suggestCompanyHTML + '</td>')
            $tr.append($suggestTicker)
            $tr.append($suggestCompany)
            tbody.append($tr)
            $tr.click(function(e) {  // suggestion is clicked, move to chart
                e.stopPropagation()
                var ticker = $(this).children('.ticker').text()
                location.replace('/chart?ticker=' + ticker)
            })
        }
    }
});

$('.search').focus(function() {
    suggestions.show()
    suggestions.mouseover(function() {
        console.log('Focus')
        suggestions.show();
    })
    suggestions.mouseout(function() {
        suggestions.hide()
    })
})





function searchStock(stock, sub) {
    sub = sub.toLowerCase()
    first = stock[0].toLowerCase().includes(sub)
    if (stock[1] === null) {
        stock[1] = 'Not Updated'
        return first
    }
    second = stock[1].toLowerCase().includes(sub)
    return first || second
}

function make_bold(input, sub) {
    var regexp = new RegExp(sub, "gi");
    const found = input.trim().match(regexp);
    if (found) {
        for (var i = 0; i < found.length; i++) {
            console.log(i, input)
            input = input.trim().replace(regexp, "<b>" + found[i] + "</b>");
        }
    }
    return input
}

function getStocksInfo() {
    $.ajax({
        type : 'post',
        url : '/info',
        dataType : 'json',
        success : function(result) { // success callback
            allStocks = result['allStocks'];
            console.log(result)
        },
        error : function(request, status, error) { // error callback
            console.log(error)
        }
    })
}
