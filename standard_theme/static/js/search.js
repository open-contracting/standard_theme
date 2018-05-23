$( document ).ready(function() {
    var queryDict = {};
    location.search.substr(1).split("&").forEach(function(item) {queryDict[item.split("=")[0]] = item.split("=")[1]})
    var term = $('#rtd-search-form input[name="q"]').val(decodeURIComponent(queryDict.q.replace(/\+/g, '%20')));
    renderResults();
    // This will make the search change without new url request but url parameters stay the same.
    //$('#rtd-search-form').submit(function( event ) {
    //    renderResults();
    //    event.preventDefault();
    //});
});

function escapeString(text) {
    return $("<div>").text(text).html();
}

function renderResults() {
    var term = $('#rtd-search-form input[name="q"]').val();
    var index = 'ocds-doc-search-' + DOCUMENTATION_OPTIONS.VERSION + '-' + (DOCUMENTATION_OPTIONS.LANGUAGE || 'en');
    $.ajax({
        url: "http://standard-search.default.opendataservices.uk0.bigv.io/v1/search?q=" + encodeURIComponent(term) + "&index=" + encodeURIComponent(index),
        success: function(data) {
            $('#search-results').hide();
            $('#search-results').html('<div id="resultsCount"></div> <ul id="resultsList" class="search"></ul>');
              

            var resultString = "Search finished, found %s page(s) matching the search query.";

            var translatedResultString = Documentation.TRANSLATIONS[resultString] || resultString;

            $('#resultsCount').html(translatedResultString.replace('%s', data.count.toString()));
            var html = '';
            

            for(idx in data.results) {
                var split = data.results[idx].url.split('#')
                var new_url = split[0] + '?highlight=' + encodeURIComponent(term) + '#' + split[1]

                html += '<li>';
                html += '<a href="'+new_url+'">';
                html += escapeString(data.results[idx].title);
                html += '</a>';
                html += '<div class="context">';

                for(hidx in data.results[idx].highlights) {
                    html += data.results[idx].highlights[hidx] + ' ';
                }
                html += '</div>';
                html += '</li>';
            }
            $('#resultsList').html(html);
            $('#search-results').show();
        }
    });
}

