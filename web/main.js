const query = document.querySelector('#query')
const search = document.querySelector('#search')
const empty_results = document.querySelector('.empty-results')
const loading_animation = document.querySelector('.loading')
const results_container = document.querySelector('.search-results')

const hidden_element = (e) => e.classList.add('hidden')
const show_element = (e) => e.classList.remove('hidden')

query.focus()

search.onclick = () => {
  hidden_element(empty_results)
  hidden_element(results_container)
  show_element(loading_animation)
  fetch('/api/search/all?query=' + query.value)
    .then(r => r.json())
    .then(r => console.log(r))
    .catch(e => console.error(e))
}