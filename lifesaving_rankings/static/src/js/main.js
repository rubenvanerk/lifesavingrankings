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

var colorPercentages = function () {
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
    $card = $(card);
    $('.merge.cards .card').removeClass('selected');
    $card.addClass('selected');
    $('#main-athlete-input').val($card.data('athlete-pk'));
};

$(document).ready(function () {
    $('#eventByAthlete').DataTable({
        'order': [1, 'asc']
    });
    $('#bestByEvent').DataTable();
    $('#teamMaker').DataTable();
    $('.init-datatable').DataTable();
    $('.popup').popup();
    $('.ui.checkbox').checkbox();
    $('.ui.accordion').accordion();
    $('#labeledAthletes').progress();

    //initialize mobile menu
    $('.ui.sidebar').sidebar('attach events', '#mobile_item');

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

    $('[data-scroll-to]').on('click', function(e) {
        let $target = $(e.target);
        window.scroll(0, findPos(document.getElementById($target.data('scroll-to'))) - 100);
    })

    $('body').removeClass('loading');
    $('#content').fadeIn();
});
