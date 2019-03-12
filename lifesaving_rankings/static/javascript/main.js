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

var reportDuplicateAthlete = function (button, query) {
    button = $(button);
    button.addClass('disabled');

    $.ajax(
        {
            url: "/rankings/report-duplicate?query=" + query
        }
    );

    button.html('<i class="check icon"></i> Thanks!');
};

$(document).ready(function () {
    $('#eventByAthlete').DataTable({
        'order': [1, 'asc']
    });
    $('#bestByEvent').DataTable();
    $('#teamMaker').DataTable();
    $('.europe-cup').each(
        function () {
            $(this).DataTable({
                "order": [[1, "desc"]]
            });
        }
    );


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

    $('.ui.checkbox')
        .checkbox()
    ;

    $('#content').fadeIn()
});
