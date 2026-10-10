document.addEventListener('DOMContentLoaded', function () {
  document.querySelector('#rtd-search-form input[name="q"]').value = new URLSearchParams(location.search).get('q') || '';

  render();
});

function render() {
  var query = document.querySelector('#rtd-search-form input[name="q"]').value;
  var position = location.href.indexOf('/search/?');
  // OCDS Index indexes each language directory separately, under a base URL that omits the language code.
  var baseUrl = location.href.substring(0, position - 2);
  var language = location.href.substring(position - 2, position);

  fetch('https://standard.open-contracting.org/search/ocdsindex_' + language + '/_search?size=100', {
    method: 'POST',
    // The "public" user has read-only access to Elasticsearch indices created by OCDS Index. We set a password
    // only to limit the impact of untargeted scans (e.g. bots).
    headers: {
      Authorization: 'Basic ' + btoa('public:G*PweUnH4u@r'),
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
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
            // https://www.elastic.co/guide/en/elasticsearch/guide/current/_finding_exact_values.html#_term_query_with_text
            "term": {
              "base_url": baseUrl
            }
          }
        }
      },
      // https://www.elastic.co/guide/en/elasticsearch/reference/7.10/highlighting.html
      "highlight": {
        "fields": {
          "text": {},
          "title": {}
        }
      }
    })
  }).then(function (response) {
    if (!response.ok) {
      throw new Error('Search failed: ' + response.status);
    }
    return response.json();
  }).then(function (data) {
    var results = document.getElementById('search-results');
    results.style.display = 'none';

    results.innerHTML = '<div id="results-count"></div><ul id="results-list" class="search"></ul>';

    var messages = JSON.parse(document.getElementById('search-messages').textContent);
    var total = data.hits.total.value;

    var list = document.getElementById('results-list');
    data.hits.hits.forEach(function (hit) {
      var parts = hit._source.url.split('#');
      var highlights = hit.highlight.text || hit.highlight.title;

      var item = document.createElement('li');
      var link = document.createElement('a');
      link.href = parts[0] + '?highlight=' + encodeURIComponent(query) + '#' + parts[1];
      link.textContent = hit._source.title;
      item.appendChild(link);
      var context = document.createElement('div');
      context.className = 'context';
      // Elasticsearch's highlights are HTML, with <em> around matches.
      context.innerHTML = highlights.join(' ') + ' ';
      item.appendChild(context);
      list.appendChild(item);
    });

    document.getElementById('results-count').textContent = (total === 1 ? messages.one : messages.other).replace('${resultCount}', total);

    results.style.display = '';
  });
}
