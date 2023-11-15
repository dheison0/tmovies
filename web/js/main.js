const query = document.querySelector('#query')
const search = document.querySelector('#search')
const empty_results = document.querySelector('.empty-results')
const loading_animation = document.querySelector('.loading')
const results_container = document.querySelector('.search-results')

const hide_element = (e) => e.classList.add('hidden')
const show_element = (e) => e.classList.remove('hidden')

const ResponseItem = ({ title, thumbnail, path }) => {
  return `
  <div class="response">
    <a href="/web/download.html?path=${path}">
      <div><img src="${thumbnail}" /></div>
      <span class="flex">${title}</span>
    </a>
  </div>`
}

const ResponseContainer = ({ title, children }) => {
  return `
  <h2 class="server-title">${title}</h2>
  <div class="server-response flex">${children}</div>`
}

query.focus()

search.onclick = () => {
  if (query.value.trim() === '') {
    alert('Você não pode fazer uma pesquisa vazia!')
    return
  }

  const onResponse = async (data) => {
    const html = data.map(extractor_result => {
      if (extractor_result.error || extractor_result.response.results.length === 0) return
      const responseItems = extractor_result.response.results.map(ResponseItem)
      return ResponseContainer({ title: extractor_result.extractor_title, children: responseItems.join("\n") })
    })
    if (html.length === 0) {
      hide_element(loading_animation)
      show_element(empty_results)
      return
    }
    results_container.innerHTML = html.join("\n")
    hide_element(loading_animation)
    show_element(results_container)
  }

  hide_element(empty_results)
  hide_element(results_container)
  show_element(loading_animation)
  fetch('/api/search/all?query=' + query.value.trim())
    .then(r => r.json())
    .then(onResponse)
    .catch(e => console.error(e))
}