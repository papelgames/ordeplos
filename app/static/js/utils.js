function imprSelec(nombre, titulo) {
  var ficha = document.getElementById(nombre);
  var ventimp = window.open('', 'popimpr');
  
  ventimp.document.write('<html><head><title>' + titulo + '</title>');
  
  // Agregar referencias a los estilos
  var stylesheets = document.styleSheets;
  for (var i = 0; i < stylesheets.length; i++) {
      var styleSheet = stylesheets[i];
      if (styleSheet.href) {
          ventimp.document.write('<link rel="stylesheet" href="' + styleSheet.href + '">');
      }
  }

  ventimp.document.write('</head><body>');
  
  // Agregar el contenido a imprimir
  ventimp.document.write('<div>' + ficha.innerHTML + '</div>');
  
  ventimp.document.write('</body></html>');
  ventimp.document.close();
  
  ventimp.onload = function () {
      ventimp.print();
      ventimp.close();
  };
}


function evitarCaracter(event, caracterProhibido) {
  var key = String.fromCharCode(event.keyCode);
  if (key === caracterProhibido) {
      event.preventDefault();
      return false;
  }
  return true;
}

//funciones para el editor
document.addEventListener("DOMContentLoaded", function () {
    var quill = new Quill('#editor', {
        theme: 'snow',
        modules: {
            toolbar: [
                [{ 'size': [] }],
                ['bold', 'italic', 'underline'],
                [{ 'list': 'ordered' }, { 'list': 'bullet' }],
            ]
        }
    });

    var Parchment = Quill.import('parchment');
    var LineHeight = new Parchment.Attributor.Style('lineheight', 'line-height', {
        scope: Parchment.Scope.BLOCK
    });
    Quill.register(LineHeight, true);

    // Crear dropdown de interlineado
    var toolbar = quill.getModule('toolbar');
    var select = document.createElement("select");
    select.classList.add("ql-lineheight");
    ["1", "1.5", "2", "2.5", "3"].forEach(value => {
        var option = document.createElement("option");
        option.value = value;
        option.textContent = value;
        select.appendChild(option);
    });

    select.addEventListener("change", function () {
        var value = this.value;
        quill.format('lineheight', value);
    });

    var toolbarContainer = document.querySelector(".ql-toolbar");
    if (toolbarContainer) {
        toolbarContainer.appendChild(select);
    }

    // Guardar HTML en el input oculto
    var form = document.querySelector('form');
    if (form) {
        form.onsubmit = function () {
            var html = quill.root.innerHTML;
            document.querySelector('#contenido_html').value = html;
        };
    }
});