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
            color = 'analysis-green';
        } else if (percentage < 105) {
            color = 'analysis-orange';
        } else {
            color = 'analysis-red';
        }
        $(this).parent().addClass(color);
    });

};

$(document).ready(function () {
    $(document).ready(function () {
        $('#eventByAthlete').DataTable({
            "order": [[2, "asc"]]
        });
    });
    $('#bestByEvent').DataTable();
    $('#teamMaker').DataTable();


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
    console.log(label);
    label.addClass('ui input').contents().filter(function(){
    return (this.nodeType == 3);
}).remove();
    var input = label.find('input');
    input.prop('placeholder', 'Search..');

    //initialize mobile menu
    $('.ui.sidebar').sidebar('attach events', '#mobile_item');

    $('#content').fadeIn("slow")
});
