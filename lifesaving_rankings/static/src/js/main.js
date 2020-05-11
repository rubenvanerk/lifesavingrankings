$.fn.api.settings.api = {
    'search athletes': '/athletes/{query}/'
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

/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function (settings, data, dataIndex) {
        if (settings.nTable.id !== 'competitionList') {
            return true;
        }
        var imported = $('#competition-filters input[name=imported]').is(':checked');
        console.log(imported);
        var wanted = $('#competition-filters input[name=wanted]').is(':checked');
        var scheduled = $('#competition-filters input[name=scheduled]').is(':checked');
        var unable = $('#competition-filters input[name=unable]').is(':checked');
        var status = data[3];
        if (imported && $.isNumeric(status) && status > 0) {
            return true;
        } else if (wanted && (status.toString().indexOf('Wanted') !== -1 || status.toString().indexOf('Upcoming') !== -1)) {
            return true;
        } else if (scheduled && status.toString().indexOf('Scheduled') !== -1) {
            return true;
        } else if (unable && status.toString().indexOf('Unable') !== -1) {
            return true;
        }
        return false;
    }
);

$(document).ready(function () {
    $('#eventByAthlete').DataTable({
        'order': [1, 'asc']
    });
    $('#bestByEvent').DataTable();
    $('#teamMaker').DataTable();
    var competitionList = $('#competitionList').DataTable({
        'order': [1, 'desc'],
        "columnDefs": [
            {"type": "num", "targets": 3}
        ]
    });
    competitionList.draw();
    $('#competition-filters input').change(function () {
        competitionList.draw();
    });

    $('.init-datatable').DataTable();
    $('.popup').popup();
    $('.ui.checkbox').checkbox();
    $('.ui.accordion').accordion();
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
        onChange: function(value, text, choice) {
            console.log(value);
        },
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


    $('body').removeClass('loading');
    $('#content').fadeIn();
});
