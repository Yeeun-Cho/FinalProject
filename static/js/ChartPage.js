container = document.getElementById('lightweight')
const chartOptions = {
    layout: { textColor: 'white', background: { type: 'solid', color: 'black' }},
    crosshair: {
        // Change mode from default 'magnet' to 'normal'.
        // Allows the crosshair to move freely without snapping to datapoints
        mode: LightweightCharts.CrosshairMode.Normal,

        // Vertical crosshair line (showing Date in Label)
        vertLine: {
            width: 8,
            color: '#C3BCDB44',
            style: LightweightCharts.LineStyle.Solid,
            labelBackgroundColor: '#9B7DFF',
        },

        // Horizontal crosshair line (showing Price in Label)
        horzLine: {
            color: '#9B7DFF',
            labelBackgroundColor: '#9B7DFF',
        },
    },
    grid: {
        vertLines: {
            visible: false,
        },
        horzLines: {
            visible: false,
        },
    },
};
const chart = LightweightCharts.createChart(container, chartOptions);
const candlestickSeries = chart.addCandlestickSeries({upColor: '#26a69a', downColor: '#ef5350', borderVisible: false, wickUpColor: '#26a69a', wickDownColor: '#ef5350'});

const legend = document.getElementById('legend');

var ticker;
$(document).ready(function() {
    const queryString = window.location.search
    const urlParams = new URLSearchParams(queryString);
    ticker = urlParams.get('ticker')
    var tickerLegend = document.getElementById('ticker')
    tickerLegend.innerText = ticker
    graphTicker(ticker, '1d')
});

$('.timeframe span').on('click', function() {
    var before = $('.selected')
    var timeframe = $(this).attr('id')
    if (before.attr('id') !== timeframe) {
        before.removeClass('selected')
        $(this).addClass('selected')
        graphTicker(ticker, timeframe)
    }
})

function graphTicker(ticker, timeframe) {
    $.ajax({
        type : 'post',
        url : '/stock',
        dataType : 'json',
        data : {
          "ticker" : ticker,
          "timeframe": timeframe,
        },
        success : function(result) { // success callback
            stock = result['stock'];
            candlestickSeries.setData(stock);
            // chart.timeScale().fitContent();
            const getLastBar = () => stock[stock.length - 1];
            const buildDateString = time => `${time.year} - ${time.month} - ${time.day}`;
            const setTooltipHtml = (date, ohlc) => {
                var dateLegend = document.getElementById('date')
                dateLegend.innerText = date;
                var listItems = $("#legend li span");
                listItems.each(function(idx, span) {
                    var price = $(span)
                    var id = price.attr('id')
                    if (ohlc[id] !== undefined) {
                        price.text(`${id}: ${ohlc[id]}`);
                    }
                    else {
                        price.text('');
                    }
                });
            };

            const updateLegend = param => {
            	const validCrosshairPoint = !(
            		param === undefined || param.time === undefined || param.point.x < 0 || param.point.y < 0
            	);
            	const bar = validCrosshairPoint ? param : getLastBar();
            	const time = bar.time;
            	const date = buildDateString(time);
            	const ohlc = validCrosshairPoint ? param.seriesPrices.get(candlestickSeries) : bar.value;
            	setTooltipHtml(date, ohlc);
            };
            chart.subscribeCrosshairMove(updateLegend);
            updateLegend(undefined);
        },
        error : function(request, status, error) { // error callback
            console.log(error)
        }
    })
}

// window.addEventListener('resize', () => {
//     chart.resize(window.innerWidth, window.innerHeight);
// });
