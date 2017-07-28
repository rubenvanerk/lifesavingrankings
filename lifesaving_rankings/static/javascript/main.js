var colorPercentages = function () {
    var analysisResults = $(".analysis-percentage");

    analysisResults.each(function () {
        var percentage = $(this).text();
        percentage = percentage.replace('%', '');
        var color = 'red';
        if(percentage < 100) {
            color = 'green';
        } else if(percentage < 105) {
            color = 'orange';
        } else {
            color = 'red';
        }
        $(this).parent().css('background-color', color);
    });

};