const container = document.getElementById('container')
container.addEventListener('click', (event) => {
  if (event.target.id === "btn-add") {
    event.target.id = "btn-non"
    event.target.class = "wish_item_non"
    event.target.style = "color:#B6AD90;"
    let outfitId = event.target.value
    fetch('/wishlist', {
      method: 'delete',
      headers: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      body: JSON.stringify(
        {'outfit_id': outfitId}
      )
    })
  } else if (event.target.id === "btn-non") {
    event.target.id = "btn-add"
    event.target.class = "wish_item_add"
    event.target.style = "color:#E76F51;"
    let outfitId = event.target.value 
    console.log(outfitId)
    fetch('/wishlist', {
      method: 'post',
      headers: {
        'content-type': 'application/x-www-form-urlencoded'
      },
      body: JSON.stringify(
        {'outfit_id': outfitId}
      )
    })
  } else {
    // pass
  }
})  