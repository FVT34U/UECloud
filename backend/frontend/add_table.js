fetch('static/folder_table.html')
.then(response => response.text())
.then(data => {
  document.getElementById('table-container').innerHTML = data;
});