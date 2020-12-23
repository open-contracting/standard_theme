$(document).ready(function () {
  var parameters = {};

  // https://developer.mozilla.org/en-US/docs/Web/API/URLSearchParams not fully supported.
  location.search.substr(1).split('&').forEach(function (pair) {
    var parts = pair.split('=');
    parameters[parts[0]] = parts[1];
  });

  // https://developer.mozilla.org/en-US/docs/Web/JavaScript/Reference/Global_Objects/decodeURIComponent#Decoding_query_parameters_from_a_URL
  $('#rtd-search-form input[name="q"]').val(decodeURIComponent(parameters.q.replace(/\+/g, ' ')));

  render();
});

function render() {
  var query = $('#rtd-search-form input[name="q"]').val();
  var baseUrl = location.href.substring(0, location.href.indexOf('/search/?') - 2);

  $.ajax({
    url: 'https://standard.open-contracting.org:9200/ocdsindex_en/_search?size=100',
    // The "public" user has read-only access to Elasticsearch indices created by OCDS Index. We set a password
    // only to limit the impact of untargeted scans (e.g. bots).
    headers: {
      Authorization: 'Basic ' + btoa('public:G*PweUnH4u@r') // IE > 9
    },
    method: 'POST',
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
              "base_url": baseUrl
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
    success: function (data) {
      $('#search-results').hide();

      $('#search-results').html('<div id="results-count"></div><ul id="results-list" class="search"></ul>');

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
        data.hits.hits[i].highlights.forEach(function (highlight) {
          listHtml += highlight + ' ';
        });
        listHtml += '</div>';
        listHtml += '</li>';
      }

      $('#results-count').html(countHtml);
      $('#results-list').html(listHtml);

      $('#search-results').show();
    }
  });
}
