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

var selectAsMain = function(card) {
    $card = $(card);
    $('.merge.cards .card').removeClass('selected');
    $card.addClass('selected');
    $('#main-athlete-input').val($card.data('athlete-pk'));
};

/* Custom filtering function which will search data in column four between two values */
$.fn.dataTable.ext.search.push(
    function( settings, data, dataIndex ) {
        if ( settings.nTable.id !== 'competitionList' ) {
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
        } else if (wanted && status.toString().indexOf('Wanted') !== -1) {
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
        'order': [1, 'desc']
    });
    competitionList.draw();
    $('#competition-filters input').change( function() {
        competitionList.draw();
    } );
    $('.init-datatable').DataTable();


    $('.popup').popup();
    $('#pick-athletes').selectize({
        plugins: ['remove_button'],
        delimiter: ',',
        persist: false,
        create: function (input) {
            return {
                value: input,
                text: input
            }
        }
    });


    var label = $('.dataTables_filter label');
    label.addClass('ui input').contents().filter(function () {
        return (this.nodeType == 3);
    }).remove();
    var input = label.find('input');
    input.prop('placeholder', 'Search..');

    //initialize mobile menu
    $('.ui.sidebar').sidebar('attach events', '#mobile_item');

    $('.ui.checkbox').checkbox();

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

    $('#labeledAthletes').progress();

    $('#content').fadeIn()
});
