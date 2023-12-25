const content = document.querySelector(".content")
const path = URL(window.location.href).searchParams.get('path')
if (path === '' || !path) {
  window.location = '/tmovies'
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

const url = new URL(path, "http://dheisom.vps-kinghost.net:8899")
fetch(url.href, { mode: 'no-cors' })
  .then(r => r.json())
  .then(onResponse)
  .catch(e => console.error(e))
