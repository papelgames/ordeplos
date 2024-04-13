function imprSelec(nombre, titulo) {
    var ficha = document.getElementById(nombre);
    var ventimp = window.open('', 'popimpr');
    ventimp.document.write('<html><head><title>'+titulo+'</title>');
    ventimp.document.write(
      '<link rel="stylesheet" href="/static/css/bootstrap/bootstrap.min.css">'
    );
    ventimp.document.write(
      '<link rel="stylesheet" href="/static/css/style.css">'
    );
    ventimp.document.write('</head><body>');
    ventimp.document.write(ficha.innerHTML);
    ventimp.document.write('</body></html>');
    ventimp.document.close();
    
    ventimp.print();
    ventimp.close();
    
  }

function evitarCaracter(event, caracterProhibido) {
  var key = String.fromCharCode(event.keyCode);
  if (key === caracterProhibido) {
      event.preventDefault();
      return false;
  }
  return true;
}

window.addEventListener('load', () => {
  // Elemento HTML donde se muestra el QR
  const contenedorQR = document.getElementById('contenedorQR');

  // Obtiene el valor del div contenedorQR
  const valorParaQR = contenedorQR.textContent;
  // Crea una instancia de QRCode con el valor obtenido
  const QR = new QRCode(contenedorQR, valorParaQR);


});