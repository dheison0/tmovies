const content = document.querySelector(".content")
const url = new URL(window.location.href)
const path = url.searchParams.get('path')
if (path === '' || !path) {
  window.location = '/web'
}

const onResponse = (r) => {
  const magnets = r.links.map(e => `
    <div class="magnet">
      <a href="${e.magnet}">${e.title}</a>
    </div>
  `)
  content.innerHTML = `
  <div class="flex download-container">
    <img class="thumbnail" src="${r.thumbnail}" />
    <h2 class="title">${r.title}</h2>
    <span class="sinopse">${r.sinopse}</span>
    <div class="magnets-container">${magnets.join("\n")}</div>
  </div>
  `
}


fetch(path)
  .then(r => r.json())
  .then(onResponse)
  .catch(e => console.error(e))
