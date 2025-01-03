from flask import Flask, render_template, Response, request, jsonify
import cv2

app = Flask(__name__)

# Inicia la cámara
camera = cv2.VideoCapture(0)

# Umbrales por defecto para bordes
low_threshold = 50
high_threshold = 150
# Parámetro de sensibilidad para la detección de objetos
scale_factor = 1.1

# Cargar el clasificador de objetos (rostros)
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

def generate_original():
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Codifica el frame en formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_processed():
    global low_threshold, high_threshold
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Aplica el filtro de detección de bordes con los umbrales actuales
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edges = cv2.Canny(gray, int(low_threshold), int(high_threshold))

            # Codifica el frame procesado en formato JPEG
            ret, buffer = cv2.imencode('.jpg', edges)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

def generate_objects():
    global scale_factor
    while True:
        success, frame = camera.read()
        if not success:
            break
        else:
            # Aplica la detección de objetos (rostros)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = face_cascade.detectMultiScale(gray, scaleFactor=float(scale_factor), minNeighbors=5, minSize=(30, 30))

            # Dibujar un rectángulo alrededor de los rostros detectados
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                cv2.putText(frame, "Rostro", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (255, 0, 0), 2)

            # Codifica el frame procesado en formato JPEG
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_original')
def video_original():
    return Response(generate_original(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_processed')
def video_processed():
    return Response(generate_processed(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/video_objects')
def video_objects():
    return Response(generate_objects(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/update_thresholds')
def update_thresholds():
    global low_threshold, high_threshold, scale_factor
    low_threshold = request.args.get('low', default=50, type=int)
    high_threshold = request.args.get('high', default=150, type=int)
    scale_factor = request.args.get('scale', default=1.1, type=float)
    return jsonify({"low": low_threshold, "high": high_threshold, "scale": scale_factor})

if __name__ == "__main__":
    app.run(debug=True)
