$.fn.api.settings.api = {
    'search athletes': '/athletes/{query}/'
}

//Finds y value of given object
function findPos(obj) {
    var curtop = 0;
    if (obj.offsetParent) {
        do {
            curtop += obj.offsetTop;
        } while (obj = obj.offsetParent);
        return [curtop];
    }
}

var colorPercentages = function () { // TODO: delete this function when replaced
    var analysisResults = $(".analysis-percentage");

    analysisResults.each(function () {
        var percentage = $(this).text();
        if (percentage === "") {
            return;
        }
        percentage = percentage.replace('%', '');
        var color = '';
        if (percentage < 100) {
            color = 'positive';
        } else if (percentage < 105) {
            color = 'warning';
        } else {
            color = 'negative';
        }
        $(this).parents('td').addClass(color);
    });

};

var selectAsMain = function (card) {
    let $card = $(card);
    $('.merge.cards .card').removeClass('selected');
    $card.addClass('selected');
    $('#main-athlete-input').val($card.data('athlete-pk'));
};

$(document).ready(function () {
    let $body = $('body');
    $('#eventByAthlete').DataTable({
        'order': [1, 'asc']
    });
    $('#bestByEvent').DataTable();
    $('#teamMaker').DataTable();
    $('.init-datatable').DataTable();
    $('.popup').popup();
    $('.ui.checkbox').checkbox();
    $('.ui.accordion').accordion();
    $('.ui.date.calendar').calendar({type: 'date'});
    $('#labeledAthletes').progress();

    //initialize mobile menu
    $('.ui.sidebar').sidebar('attach events', '#mobile_item');

    var label = $('.dataTables_filter label');
    label.addClass('ui input').contents().filter(function () {
        return (this.nodeType == 3);
    }).remove();
    var input = label.find('input');
    input.prop('placeholder', 'Search..');

    $('.ui.dropdown.nationalities').dropdown({
        fullTextSearch: true
    });
    $('.ui.dropdown .default.text').select();
    $('.ui.dropdown.year-of-birth').dropdown({
        fullTextSearch: false
    });

    $('#rangestart').calendar({
        type: 'date',
        endCalendar: $('#rangeend'),
        startMode: 'year'
    });
    $('#rangeend').calendar({
        type: 'date',
        startCalendar: $('#rangestart'),
        startMode: 'year'
    });

    let $selectAthletes = $('#select-athletes');
    let values = $selectAthletes.data('values');
    $selectAthletes.dropdown({
        apiSettings: {action: 'search athletes'},
        values: $selectAthletes.data('values'),
        minCharacters: 2,
        saveRemoteData: false
    });

    if (values) {
        var arrayLength = values.length;
        for (var i = 0; i < arrayLength; i++) {
            let valueObject = values[i];
            $selectAthletes.dropdown('set selected', valueObject.value)
        }
    }

    $('[data-scroll-to]').on('click', function (e) {
        let $target = $(e.target);
        window.scroll(0, findPos(document.getElementById($target.data('scroll-to'))) - 100);
    })

    $body.on('click', function (event) {
        if ($(event.target).closest('#competition-navigation').length < 1) {
            $('#competition-navigation').accordion('close', 0);
        }
    });

    $('.special-result input').on('change', function (e) {
        let $target = $(e.target);
        let specialTime = new Duration($target.val());
        $target.val(specialTime.time);
        let eventId = $target.closest('.special-result').data('event-id');
        $('.analysis-time[data-event-id="' + eventId + '"]').each(function (index, analysisTime) {
            let timeToCompare = new Duration($(analysisTime).text());
            let percentage = specialTime.getPercentageOf(timeToCompare);
            $(analysisTime).removeClass('positive warning negative');
            let color;
            if (percentage < 100) {
                color = 'positive';
            } else if (percentage < 105) {
                color = 'warning';
            } else {
                color = 'negative';
            }
            $(analysisTime).addClass(color);
        });
    });

    $body.removeClass('loading');
    $('#content').fadeIn();
});

class Duration {
    constructor(input) {
        this.time = input.replace(/[^0-9](?=[0-9]{2}$)/, '.');
        this.time = this.time.replace(/[^0-9](?=[0-9]{2}\.[0-9]{2}$)/, ':')
    }

    getPercentageOf(timeToCompare) {
        return timeToCompare.getTimeInSeconds() / this.getTimeInSeconds() * 100;
    }

    getTimeInSeconds() {
        let minutes = Number(this.time.match(/[0-9]+(?=:[0-9]{2}\.[0-9]{2})/));
        let seconds = parseFloat(this.time.match(/[0-9]{2}\.[0-9]{2}/))
        return minutes * 60 + seconds;
    }
}