// centra en mexico
var map = L.map('mi_mapa').setView([19.4326, -99.1332], 5);

//mapas base
var cartoDark = L.tileLayer("http://a.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}.png", {
    attribution: '&copy; CartoDB'
});

var googleStreets = L.tileLayer("https://mt1.google.com/vt/lyrs=r&x={x}&y={y}&z={z}", {
    attribution: '&copy; Google'
});

var googleSat = L.tileLayer("http://www.google.cn/maps/vt?lyrs=s@189&gl=cn&x={x}&y={y}&z={z}", {
    attribution: '&copy; Google'
});

// por defectio esta capa
googleStreets.addTo(map);

//Función de botones para cambiar el mapa base
function cambiarMapaBase(tipo, botonPresionado) {
    map.removeLayer(cartoDark);
    map.removeLayer(googleStreets);
    map.removeLayer(googleSat);

    // aqui se selecciona la capa
    if (tipo === 'dark') {
        cartoDark.addTo(map);
    } else if (tipo === 'streets') {
        googleStreets.addTo(map);
    } else if (tipo === 'sat') {
        googleSat.addTo(map);
    }

    // estilo al boton presionado
    var botones = document.querySelectorAll('.btn-base');
    botones.forEach(function(btn) {
        btn.classList.remove('activo');
    });
    botonPresionado.classList.add('activo');
}

// Lógica original para cargar el GeoJSON local
var capaGeojsonActual = null; 

document.getElementById('input-geojson').addEventListener('change', function(evento) {
    var archivo = evento.target.files[0];
    if (!archivo) return; 

    var lector = new FileReader();
    lector.onload = function(e) {
        try {
            var datosGeojson = JSON.parse(e.target.result);
            
            // Si ya hay un mapa dibujado, lo borramos
            if (capaGeojsonActual) {
                map.removeLayer(capaGeojsonActual);
            }
            
            //POPUPS
            capaGeojsonActual = L.geoJSON(datosGeojson, {
                onEachFeature: function (feature, layer) {
                    if (feature.properties) {
                        var contenidoPopup = '<div style="max-height: 200px; overflow-y: auto;">';
                        contenidoPopup += '<h4 style="margin: 0 0 10px 0; color: #2c3e50; border-bottom: 1px solid #ccc; padding-bottom: 5px;">Atributos</h4>';
                        contenidoPopup += '<table style="width: 100%; border-collapse: collapse; font-size: 0.9em;">';
                        
                        for (var propiedad in feature.properties) {
                            contenidoPopup += '<tr>';
                            contenidoPopup += '<td style="padding: 4px; border-bottom: 1px solid #eee;"><strong>' + propiedad + ':</strong></td>';
                            contenidoPopup += '<td style="padding: 4px; border-bottom: 1px solid #eee;">' + feature.properties[propiedad] + '</td>';
                            contenidoPopup += '</tr>';
                        }
                        
                        contenidoPopup += '</table></div>';
                        layer.bindPopup(contenidoPopup);
                    }
                }
            }).addTo(map);

            // para hacer zoom al cargar el geojson
            map.fitBounds(capaGeojsonActual.getBounds());
            
        } catch (error) {
            alert("Hubo un error al leer el archivo. Asegúrate de que sea un GeoJSON válido.");
            console.error(error);
        }
    };
    lector.readAsText(archivo);
});