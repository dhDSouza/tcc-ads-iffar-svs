import cv2
import numpy as np
from ultralytics import YOLO

def detectar_pessoas(camera_ip):
    
    video = cv2.VideoCapture(camera_ip)
    modelo = YOLO('yolov8n.pt')

    imagem_branca = np.ones([360, 640], np.uint32)

    while True:
        status, frame = video.read()

        if not status:
            break

        frame = cv2.resize(frame, (640, 360))

        objetos = modelo(frame, stream=True)

        for objeto in objetos:
            info = objeto.boxes
            for box in info:
                x1, y1, x2, y2 = box.xyxy[0]
                x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                conf = int(box.conf[0] * 100) / 100
                classe = int(box.cls[0])

                if classe == 0:
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 0), 2)
                    imagem_branca[y1:y2, x1:x2] += 1

        imagem_branca_normalizada = 255 * ((imagem_branca - imagem_branca.min()) / (imagem_branca.max() - imagem_branca.min()))
        imagem_branca_normalizada = imagem_branca_normalizada.astype('uint8')
        imagem_branca_normalizada = cv2.GaussianBlur(imagem_branca_normalizada, (9, 9), 0)

        heat_map = cv2.applyColorMap(imagem_branca_normalizada, cv2.COLORMAP_JET)
        frame_final = cv2.addWeighted(heat_map, 0.5, frame, 0.5, 0)

        _, jpeg = cv2.imencode('.jpeg', frame_final)
        imagem = jpeg.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + imagem + b'\r\n\r\n')

    video.release()
