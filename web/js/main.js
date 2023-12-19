const query = document.querySelector('#query')
const search = document.querySelector('#search')
const content = document.querySelector('.js-content')

const EmptyResults = ({ message = "Sem resultados!" }) => {
  content.innerHTML = `
    <div class="flex empty-results">
      <ion-icon name="cafe-outline"></ion-icon>
      <h2>${message}</h2>
    </div>`
}

const LoadingAnimation = ({ message = "Carregando..." }) => {
  content.innerHTML = `
    <div class="flex loading">
      <ion-icon name="reload-circle-outline"></ion-icon>
      <h2>${message}</h2>
    </div>`
}

const SearchResults = (results) => {
  content.innerHTML = `<div class="flex search-results">${results}</div>`
}

const ResponseContainer = ({ title, children }) => {
  return `
  <h2 class="server-title">${title}</h2>
  <div class="server-response flex">${children}</div>`
}

const ResponseItem = ({ title, thumbnail, path }) => {
  return `
  <div class="response">
    <a href="/download.html?path=${path}">
      <div><img loading="lazy" src="${thumbnail}" /></div>
      <span class="flex">${title}</span>
    </a>
  </div>`
}

const RenderResponseItems = ({ title, items }) => {
  const responseItems = items.map(ResponseItem)
  return ResponseContainer({ title, children: responseItems.join("\n") })
}

search.onclick = () => {
  if (query.value.trim() === '') {
    alert('Você não pode fazer uma pesquisa vazia!')
    return
  }
  LoadingAnimation({ message: "Pesquisando..." })

  const onResponse = async (data) => {
    const html = data.map(extractor_result => {
      if (extractor_result.error || extractor_result.response.results.length === 0) return
      return RenderResponseItems({ title: extractor_result.extractor_title, items: extractor_result.response.results })
    })
    if (html.length === 0) {
      return
    }
    SearchResults(html)
  }

  fetch('/api/search/all?query=' + query.value.trim())
    .then(r => r.json())
    .then(onResponse)
    .catch(e => console.error(e))
}


query.focus()
fetch('/api/recommendations')
  .then(r => r.json())
  .then(r => SearchResults(RenderResponseItems({ title: "Recomendações", items: r })))
  .catch(e => console.error(e))