$(document).ready(function () {
  renderResults();
});

function renderResults() {
  var query = $('#rtd-search-form input[name="q"]').val();
  var base_url = location.href.substring(0, location.href.indexOf('/search/?') - 2)

  $.ajax({
    url: 'https://standard.open-contracting.org:9200/ocdsindex_en/_search?size=100',
    username: 'public',
    // The "public" user has read-only access to Elasticsearch indices created by OCDS Index. We set a password
    // only to limit the impact of untargeted scans (e.g. bots).
    password: 'G*PweUnH4u@r',
    contentType: 'application/json',
    data: JSON.stringify({
      "query": {
        "bool": {
          "must": {
            "simple_query_string": {
              "query": query,
              "fields": ["text", "title^3"],
              "default_operator": "and"
            }
          },
          "filter": {
            "term": {
              "base_url": base_url
            }
          }
        }
      },
      "highlight": {
        "fields": {
          "text": {},
          "title": {}
        }
      }
    }),
    success: function(data) {
      $('#search-results').hide();

      $('#search-results').html('<div id="resultsCount"></div><ul id="resultsList" class="search"></ul>');

      var message = "Search finished, found %s page(s) matching the search query.";

      var countHtml = (Documentation.TRANSLATIONS[message] || message).replace('%s', data.hits.total.value.toString());

      var listHtml = '';
      for (var i = 0, l = data.hits.hits.length; i < l; i++) {
        var parts = data.hits.hits[i].url.split('#');

        listHtml += '<li>';
        listHtml += '<a href="' + parts[0] + '?highlight=' + encodeURIComponent(query) + '#' + parts[1] + '">';
        listHtml += $("<div>").text(data.hits.hits[i].title).html();
        listHtml += '</a>';
        listHtml += '<div class="context">';
        for (var j = 0, m = data.hits.hits[i].highlights.length; j < k; j++) {
          listHtml += data.hits.hits[i].highlights[j] + ' ';
        }
        listHtml += '</div>';
        listHtml += '</li>';
      }

      $('#resultsCount').html(countHtml);
      $('#resultsList').html(listHtml);

      $('#search-results').show();
    }
  });
}
