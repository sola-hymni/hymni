from flask import Flask, render_template_string, url_for, send_from_directory
import pandas as pd
from datetime import datetime
import requests
from io import StringIO

app = Flask(__name__)

CSV_URL = "https://docs.google.com/spreadsheets/d/1XJ-MzLjds3Pe_YXOqnEgQQnPwpcvIORgnz9jSlwwaj4/export?format=csv"

# <--- INSERTAR AQUÍ --->
@app.route('/mostrar_imprimible/<filename>')
def mostrar_imprimible(filename):
    return send_from_directory('imprimibles', filename)
# <--- FIN DE LA INSERCIÓN --->

def obtener_datos():
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        response = requests.get(CSV_URL, headers=headers, timeout=10)
        response.raise_for_status()

        response.encoding = 'utf-8' # <--- ESTA ES LA LÍNEA NUEVA
        df = pd.read_csv(StringIO(response.text), dtype=str)

        df.columns = df.columns.str.strip()

        df['Fecha_DT'] = pd.to_datetime(df['Fecha_Publicacion'], dayfirst=True, errors='coerce')
        hoy = datetime.now().date()
        
        df_publicables = df.dropna(subset=['Fecha_DT'])
        df_publicables = df_publicables[df_publicables['Fecha_DT'].dt.date <= hoy].copy()

        if df_publicables.empty:
            return []

        df_publicables = df_publicables.sort_values(by='Fecha_DT', ascending=False)
        return df_publicables.to_dict(orient='records')

    except Exception as e:
        print(f"Error: {e}")
        return []

INDEX_HTML = """
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>hymni</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Georgia', serif;
            background-color: #162844;
            background-image: radial-gradient(rgba(255, 255, 255, 0.12) 1px, transparent 1px);
            background-size: 30px 30px;
            background-attachment: fixed;
            color: white;
            min-height: 100vh;
            display: flex; flex-direction: column; align-items: center;
        }

        /* Splash Screen */
        #splash {
            position: fixed; top: 0; left: 0; width: 100%; height: 100%;
            background: #162844; display: flex; flex-direction: column;
            justify-content: center; align-items: center; z-index: 9999;
            transition: opacity 1s ease; cursor: pointer;
        }
        .heartbeat { width: 140px; animation: beat 1.5s infinite; mix-blend-mode: screen; }
        @keyframes beat { 0%, 100% { transform: scale(1); } 50% { transform: scale(1.05); } }

        /* Botón de Audio Restaurado */
        #audio-control {
            position: fixed;
            top: 20px;
            right: 20px;
            background: rgba(255, 255, 255, 0.1);
            border: 1px solid rgba(255, 255, 255, 0.3);
            color: white;
            padding: 8px 12px;
            border-radius: 50px;
            cursor: pointer;
            z-index: 1000;
            font-family: sans-serif;
            font-size: 0.7rem;
            letter-spacing: 1px;
            display: none; /* Se oculta hasta entrar */
            transition: background 0.3s;
        }
        #audio-control:hover { background: rgba(255, 255, 255, 0.2); }

        /* Contenido Principal */
        #main-content { display: none; width: 100%; max-width: 500px; padding: 40px 20px; text-align: center; }
        .logo-mini { width: 120px; margin-bottom: 25px; mix-blend-mode: screen; opacity: 0.9; }
         .slogan {

            font-size: 0.75rem; /* Más pequeño para que parezca un sello */

            letter-spacing: 4px;

            text-transform: uppercase;

            opacity: 0.6;

            margin-bottom: 12px;

            line-height: 1.6;

            font-family: 'Arial', sans-serif; /* Fuente limpia para contraste */

            font-weight: bold;
        }



        .subtitulo-app {

            font-weight: 300;

            font-style: italic;

            font-size: 1.1rem; /* Un poco más pequeño que antes para elegancia */

            margin-bottom: 30px;

            color: rgba(255, 255, 255, 0.95);

            letter-spacing: 1px;

        }


        .divisor { border: 0; border-top: 1px solid rgba(255,255,255,0.1); width: 60%; margin: 0 auto 30px auto; }

        .himno-item { text-align: left; padding: 12px 10px; border-bottom: 1px solid rgba(255,255,255,0.1); }
        .himno-meta { font-size: 0.7rem; opacity: 0.5; margin-bottom: 5px; }
        .himno-titulo { font-size: 1.1rem; font-weight: 400; color: #fff; }

        /* Estilos del Modal */
        #modal-himno {
            display: none;
            position: fixed;
            z-index: 2000;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(22, 40, 68, 0.98);
            overflow-y: auto;
            padding: 40px 20px;
        }
        .modal-content {
            max-width: 500px;
            margin: 0 auto;
            text-align: left;
        }
        .btn-cerrar {
            position: fixed;
            top: 20px; right: 20px;
            background: none; border: none;
            color: white; font-size: 2rem; cursor: pointer;
            opacity: 0.5;
        }
        .himno-letra {
            white-space: pre-line;
            line-height: 1.8;
            font-size: 1.1rem;
            margin-top: 30px;
            color: rgba(255,255,255,0.9);
        }

        /* Estilos del Modal actualizados */
        #modal-himno {
            display: none;
            position: fixed;
            z-index: 2000;
            top: 0; left: 0; width: 100%; height: 100%;
            background-color: rgba(22, 40, 68, 0.98);
            overflow-y: auto;
            padding: 40px 20px;
        }
        .modal-content {
            max-width: 500px;
            margin: 0 auto;
            text-align: left;
        }
        .btn-cerrar {
            position: fixed;
            top: 20px; right: 20px;
            background: none; border: none;
            color: white; font-size: 2rem; cursor: pointer;
            opacity: 0.5;
        }
        .himno-letra {
            white-space: pre-line;
            line-height: 1.8;
            font-size: 1.2rem;
            margin-top: 25px;
            color: rgba(255,255,255,0.95);
            font-family: 'Georgia', serif;
        }
        .letra-enfasis {
            font-style: italic;
            color: #a5b4fc;
            margin: 15px 0;
            display: block;
        }

    </style>
</head>
<body>

    <div id="splash" onclick="iniciarApp()">
        <img src="{{ url_for('static', filename='Logo_hymni.jpg') }}" class="heartbeat">
        <h1 style="letter-spacing: 12px; font-weight: 300; margin-top: 20px;">hymni</h1>
        <p style="font-family: Arial; font-size: 0.7rem; margin-top: 30px; letter-spacing: 4px; opacity: 0.5;">TOCA PARA ENTRAR</p>
    </div>

    <button id="audio-control" onclick="toggleAudio()">PAUSAR MÚSICA</button>
    <audio id="intro" src="{{ url_for('static', filename='intro.mp3') }}" loop></audio>

    <div id="main-content">
        <header>
            <img src="{{ url_for('static', filename='Logo_hymni.jpg') }}" class="logo-mini" style="margin-bottom: 5px;">
            
            <h1 style="letter-spacing: 12px; font-weight: 300; margin: 0; font-size: 2.2rem; color: white;">hymni</h1>
            
            <p style="font-family: Arial; font-size: 0.55rem; opacity: 0.5; letter-spacing: 2px; margin-bottom: 15px;">Versión 1.0. Derechos reservados.</p>

            <div class="slogan">Sola Fide • Sola Gratia • Sola Scriptura <br> Solus Christus • Soli Deo Gloria</div>
            <h2 class="subtitulo-app">Aquí, solo himnos</h2>
            <hr class="divisor">
        </header>

        <div class="lista">
            {% if himnos %}
                {% for h in himnos %}
                <div class="himno-item" style="cursor:pointer;" 
                    data-audio="{{ h.URL_Audio }}"
                    data-score="{{ h.ID_Imagen_Imprimible }}"
                    data-imagen="{{ h.Archivo_Imagen }}"
                    data-biblico="{{ h.Texto_Biblico }}"
                    data-banner="{{ h.Banner_Anunciante }}"
                    
                    onclick="abrirModal('{{ h.Titulo_Himno|e|replace("\'", "") }}', 
                         '{{ h.Fecha_Publicacion }} | {{ h.Fuente_Himnario }} #{{ h.Numero_Himnario }}', 
                         '{{ h.Letra_Himno|e|replace("\'", "") }}', 
                         '{{ h.Compositor|e|replace("\'", "") }}', 
                         '{{ h.Anio_Composicion|e }}', 
                         '{{ h.Historia_Corta|e|replace("\'", "")|replace("\r", "")|replace("\n", " ") }}')">
                    
                         
                    <div class="himno-meta">{{ h.Fecha_Publicacion }} | {{ h.Fuente_Himnario }} #{{ h.Numero_Himnario }}</div>
                    <div class="himno-titulo">{{ h.Titulo_Himno }}</div>
                </div>
                {% endfor %}
            {% else %}
                <p style="margin-top: 50px; opacity: 0.4; font-style: italic;">No hay himnos disponibles.</p>
            {% endif %}

            <div id="publicidad-listado" style="text-align: center; margin-top: 50px; padding: 30px 20px; background: rgba(255,255,255,0.03); border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px; margin-bottom: 50px; margin-left: 10px; margin-right: 10px;">
                <p style="font-size: 0.75rem; opacity: 0.4; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">Espacio Publicitario Disponible</p>
                <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 10px; font-style: italic;">Tu empresa puede anunciar aquí.</p>
                <a href="mailto:sola.hymni@gmail.com" style="color: #a5b4fc; font-size: 0.9rem; text-decoration: none; border-bottom: 1px solid rgba(165, 180, 252, 0.3);">Contacto: sola.hymni@gmail.com</a>
            </div>
            </div> </div> </div>

        </div>
    
    </div>

    <div id="modal-himno">
        <button class="btn-cerrar" onclick="cerrarModal()">&times;</button>
        <div class="modal-content">

            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px; width: 100%;">
                <div id="modal-meta" class="himno-meta" style="margin: 0; padding: 0;"></div>
    
                <button id="audioBtnModal" onclick="toggleAudio()" style="background: none; border: 1px solid rgba(255,255,255,0.4); color: white; padding: 4px 12px; border-radius: 20px; font-size: 0.7rem; cursor: pointer; text-transform: uppercase; white-space: nowrap;">
                    ESCUCHAR INTRO
                </button>
            </div>

            <img src="{{ url_for('static', filename='Logo_hymni.jpg') }}" style="width: 80px; display: block; margin: 0 auto 20px auto; mix-blend-mode: screen; opacity: 0.8;">
            <h2 id="modal-titulo" style="margin-bottom: 5px; text-align: center;"></h2>
            <div id="modal-autoria" style="text-align: center; font-size: 0.85rem; opacity: 0.75; font-style: italic; margin-bottom: 15px;"></div>
            <hr class="divisor">
            <div id="seccion-biblica" style="display:none; text-align:center;">
                <p style="font-size: 0.70rem; opacity: 0.5; letter-spacing: 2px; margin-bottom: 4px; text-transform: uppercase;">Texto bíblico asociado</p>
                <div id="modal-biblico" style="font-size: 0.95rem; font-weight: bold; color: #a5b4fc;"></div>
                

            </div>
           


            <div id="modal-historia" style="font-size: 0.9rem; opacity: 0.8; text-align: justify; margin: 20px auto; max-width: 90%; line-height: 1.6; font-style: italic; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 15px; display:none;"></div>

            <hr class="divisor">

            <div id="modal-audio-link" style="text-align: center; margin: 15px 0; display: none;">
                <a id="youtube-link" href="#" target="_blank" style="color: #a5b4fc; font-size: 0.85rem; text-decoration: none; border: 1px solid #a5b4fc; padding: 5px 15px; border-radius: 15px;">
                    ▶ ESCUCHAR EN YOUTUBE
                </a>


            </div>

            <div id="modal-score-container" style="text-align: center; margin: 20px 0; display: none;">
                <p style="font-size: 0.7rem; opacity: 0.5; letter-spacing: 2px; margin-bottom: 10px;">PARTITURA ORIGINAL</p>
                <img id="score-img" src="" style="width: 75%; border-radius: 5px; margin-bottom: 15px; border: 1px solid rgba(255,255,255,0.1);">
                <br>
                <a id="download-link" href="#" target="_blank" style="color: #fff; font-size: 0.8rem; text-decoration: none; background: rgba(255,255,255,0.1); padding: 8px 20px; border-radius: 5px; border: 1px solid rgba(255,255,255,0.2);">
                    ⬇ DESCARGAR PARA IMPRIMIR (PDF/JPG)
                </a>
            </div>

            <div id="modal-publicidad" style="text-align: center; margin-top: 40px; padding: 25px 20px; background: rgba(255,255,255,0.03); border: 1px dashed rgba(255,255,255,0.1); border-radius: 16px;">
                <div id="publi-contenido">
                    <p style="font-size: 0.75rem; opacity: 0.4; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">Espacio Publicitario Disponible</p>
                    <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 10px; font-style: italic;">Tu empresa puede anunciar aquí.</p>
                    <a href="mailto:sola.hymni@gmail.com" style="color: #a5b4fc; font-size: 0.9rem; text-decoration: none; border-bottom: 1px solid rgba(165, 180, 252, 0.3);">Contacto: sola.hymni@gmail.com</a>
                </div>
            </div>

            
            <div id="modal-letra" class="himno-letra"></div>
        </div>
    </div>


    <script>
        const audio = document.getElementById('intro');
        const audioBtn = document.getElementById('audio-control');

        function iniciarApp() {
            audio.play().catch(e => console.log("Audio play error:", e));
            const splash = document.getElementById('splash');
            splash.style.opacity = '0';
            setTimeout(() => {
                splash.style.display = 'none';
                document.getElementById('main-content').style.display = 'block';
                audioBtn.style.display = 'block'; // Mostrar el botón de control al entrar
            }, 800);
        }

        function toggleAudio() {
            if (audio.paused) {
                audio.play();
                audioBtn.innerText = "PAUSAR MÚSICA";
            } else {
                audio.pause();
                audioBtn.innerText = "REPRODUCIR";
            }
        }

        function abrirModal(titulo, meta, letra, compositor, anio, historia) {

            // ESTA ES LA LÍNEA A INSERTAR:
            audio.pause(); audioBtn.innerText = "REPRODUCIR";

            // 1. Recogemos el link del atributo invisible
            const urlAudio = event.currentTarget.getAttribute('data-audio');

            document.getElementById('modal-titulo').innerText = titulo;
            document.getElementById('modal-meta').innerHTML = meta.replace("|", " • ");
            document.getElementById('modal-autoria').innerText = (compositor || "") + (anio ? " (" + anio + ")" : "");

            // Manejo seguro de la Historia
            const hDiv = document.getElementById('modal-historia');
            if (historia && historia !== 'nan' && historia.trim() !== "" && historia !== 'None') {
                hDiv.innerText = historia;
                hDiv.style.display = 'block';
            } else {
                hDiv.style.display = 'none';
            }

            // 2. Inyectamos el link en el contenedor del modal
            const audioContainer = document.getElementById('modal-audio-link');
            const ytLink = document.getElementById('youtube-link');

            if (urlAudio && urlAudio !== 'nan' && urlAudio.trim() !== "") {
                ytLink.href = urlAudio;
                audioContainer.style.display = 'block';
            } else {
                audioContainer.style.display = 'none';
            }

 // <--- SUSTITUIR DESDE AQUÍ --->
            
            // 1. Captura de datos y elementos
            const el = event.currentTarget;
            const textoBiblico = el.getAttribute('data-biblico');
            const nombreImagen = el.getAttribute('data-imagen');
            const scoreID = el.getAttribute('data-score');

            const seccionBiblica = document.getElementById('seccion-biblica');
            const biblicoDiv = document.getElementById('modal-biblico');

            const scoreContainer = document.getElementById('modal-score-container');
            const scoreImg = document.getElementById('score-img');
            const downloadLink = document.getElementById('download-link');

            // AÑADE ESTAS DOS LÍNEAS AQUÍ:
            const bannerUrl = el.getAttribute('data-banner');
            const publiContenedor = document.getElementById('publi-contenido');
            

            // 2. Lógica para el Texto Bíblico
            if (seccionBiblica && biblicoDiv) {
                if (textoBiblico && textoBiblico !== 'nan' && textoBiblico.trim() !== "" && textoBiblico !== 'None') {
                    biblicoDiv.innerText = textoBiblico;
                    seccionBiblica.style.display = 'block';
                } else {
                    seccionBiblica.style.display = 'none';
                }
            }

            // 3. Lógica para la Partitura (Imagen local)
            if (nombreImagen && nombreImagen !== 'nan' && nombreImagen.trim() !== "" && nombreImagen !== 'None') {
                scoreImg.src = "/mostrar_imprimible/" + nombreImagen;
                scoreContainer.style.display = 'block';
            } else {
                scoreContainer.style.display = 'none';
            }

            // 4. Lógica para la Descarga (Drive)
            if (scoreID && scoreID !== 'nan' && scoreID.trim() !== "" && scoreID !== 'None') {
                const cleanID = scoreID.includes('d/') ? scoreID.split('d/')[1].split('/')[0] : scoreID.split('/')[0];
                downloadLink.href = "https://drive.google.com/uc?export=download&id=" + cleanID;
                downloadLink.style.display = 'inline-block';
            } else {
                downloadLink.style.display = 'none';
            }

            // Lógica de Publicidad Dinámica
            if (publiContenedor) {
                if (bannerUrl && bannerUrl !== 'nan' && bannerUrl.trim() !== "" && bannerUrl !== 'None') {
                    // Si hay anunciante, insertamos la imagen
                    publiContenedor.innerHTML = `<img src="/static/banners/${bannerUrl}" style="width: 100%; max-width: 350px; border-radius: 4px; box-shadow: 0 4px 10px rgba(0,0,0,0.2);">`;
                } else {
                    // Si no hay, mantenemos el texto de captación de clientes
                    publiContenedor.innerHTML = `
                        <p style="font-size: 0.75rem; opacity: 0.4; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 10px;">Espacio Publicitario Disponible</p>
                        <p style="font-size: 0.95rem; opacity: 0.7; margin-bottom: 10px; font-style: italic;">Tu empresa puede anunciar aquí.</p>
                        <a href="mailto:sola.hymni@gmail.com" style="color: #a5b4fc; font-size: 0.9rem; text-decoration: none; border-bottom: 1px solid rgba(165, 180, 252, 0.3);">Contacto: sola.hymni@gmail.com</a>
                    `;
                }
            }

            let letraLimpia = letra.replace(/\\[(.*?)\\]/g, '<span class="letra-enfasis">$1</span>');
            document.getElementById('modal-letra').innerHTML = letraLimpia;
            
            document.getElementById('modal-himno').style.display = 'block';
            document.body.style.overflow = 'hidden'; 
        }

        function cerrarModal() {
            document.getElementById('modal-himno').style.display = 'none';
            document.body.style.overflow = 'auto'; 
        }

    </script>

    <script data-goatcounter="https://hymni.goatcounter.com/count" async src="//gc.zgo.at/count.js"></script>
    
    </body>
</html>
"""

@app.route('/')
def index():
    datos = obtener_datos()
    return render_template_string(INDEX_HTML, himnos=datos)

if __name__ == '__main__':
    app.run(debug=True)