var colorPercentages = function () {
    var analysisResults = $(".analysis-percentage");

    analysisResults.each(function () {
        var percentage = $(this).text();
        percentage = percentage.replace('%', '');
        var color = '';
        if(percentage < 100) {
            color = 'analysis-green';
        } else if(percentage < 105) {
            color = 'analysis-orange';
        } else {
            color = 'analysis-red';
        }
        $(this).parent().addClass(color);
    });

};