import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime

def realizar_heatmap(camera_ip):
    
    video = cv2.VideoCapture(camera_ip)
    modelo = YOLO('yolov8n.pt')

    imagem_branca = np.ones([360, 640], np.uint32)

    while video.isOpened():

        status, frame = video.read()

        if status:
            
            frame = cv2.resize(frame, (640, 360))

            resultados = modelo(frame, classes=0, conf=0.3, iou=0.1, stream=True)

            for resultado in resultados:

                boxes = resultado.boxes

                for box in boxes:
        
                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    largura = x2 - x1
                    altura = y2 - y1

                    precisao = int(box.conf[0] * 100)

                    imagem_branca[y1:y2, x1:x2] += 1
                    cv2.rectangle(frame, (x1, y1), (x1 + largura, y1 + altura), (255, 0, 255), 2)

            imagem_branca_normalizada = 255 * ((imagem_branca - imagem_branca.min()) / (imagem_branca.max() - imagem_branca.min()))
            imagem_branca_normalizada = imagem_branca_normalizada.astype('uint8')
            imagem_branca_normalizada = cv2.GaussianBlur(imagem_branca_normalizada, (9, 9), 0)

            heat_map = cv2.applyColorMap(imagem_branca_normalizada, cv2.COLORMAP_JET)
            frame_final = cv2.addWeighted(heat_map, 0.5, frame, 0.5, 0)

            _, jpeg = cv2.imencode('.jpeg', frame_final)
            imagem = jpeg.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + imagem + b'\r\n\r\n')

        else:
            break

    video.release()

def realizar_contagem(camera_ip, linha, entrada):

    from app import mongo

    video = cv2.VideoCapture(camera_ip)
    modelo = YOLO('yolov8n.pt')

    ids = []
    _id = None
    contador = 0

    while video.isOpened():

        status, frame = video.read()

        if status:

            frame = cv2.resize(frame, (640, 360))

            cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (255, 255, 255), 2)

            cv2.putText(frame, f'Contador: {contador}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            resultados = modelo.track(frame, classes=0, conf=0.3, iou=0.1, stream=True, persist=True)

            for resultado in resultados:

                boxes = resultado.boxes

                for box in boxes:

                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    largura = x2 - x1
                    altura = y2 - y1
                    centro_x = x1 + largura // 2
                    centro_y = y1 + altura // 2

                    precisao = int(box.conf[0] * 100)

                    if box.id is not None:
                        _id = box.id.cpu().numpy().astype(int)

                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.circle(frame, (centro_x, centro_y), 2, (255, 0, 255), 2)
                    cv2.putText(frame, str(int(_id)), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    if linha[0] == linha[2]:
                        posicao = 'vertical'
                    elif linha[1] == linha[3]:
                        posicao = 'horizontal'

                    if _id not in ids:

                        if posicao == 'vertical':

                            if entrada == 'esquerda':

                                if linha[1] < centro_y < linha[3] and centro_x < linha[0] and centro_x >= linha[0] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now(),
                                        'saida': ''
                                    })
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)

                            elif entrada == 'direita':

                                if linha[1] < centro_y < linha[3] and centro_x > linha[0] and centro_x <= linha[0] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now(),
                                        'saida': ''
                                    })                                    
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)

                        else:

                            if entrada == 'cima':

                                if linha[0] < centro_x < linha[2] and centro_y < linha[1] and centro_y >= linha[1] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now(),
                                        'saida': ''
                                    })                                    
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)

                                elif entrada == 'baixo':

                                    if linha[0] < centro_x < linha[2] and centro_y > linha[1] and centro_y <= linha[1] - 15:
                                        contador += 1
                                        ids.append(_id)
                                        mongo.get_database().get_collection('registros').insert_one({
                                            'camera_ip': camera_ip,
                                            'entrada': datetime.now(),
                                            'saida': ''
                                        })
                                        cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)
                                        
                    else:

                        if posicao == 'vertical':

                            if entrada == 'esquerda':

                                if linha[1] < centro_y < linha[3] and centro_x > linha[0] and centro_x <= linha[0] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now()
                                    })
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

                            elif entrada == 'direita':

                                if linha[1] < centro_y < linha[3] and centro_x < linha[0] and centro_x >= linha[0] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now()
                                    })                                    
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

                        else:

                            if entrada == 'cima':

                                if linha[0] < centro_x < linha[2] and centro_y > linha[1] and centro_y <= linha[1] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now()
                                    })                                    
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

                                elif entrada == 'baixo':

                                    if linha[0] < centro_x < linha[2] and centro_y < linha[1] and centro_y >= linha[1] + 15:
                                        contador -= 1
                                        ids.remove(_id)
                                        mongo.get_database().get_collection('registros').insert_one({
                                            'camera_ip': camera_ip,
                                            'entrada': '',
                                            'saida': datetime.now()
                                        })                                        
                                        cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)
                        
            _, jpeg = cv2.imencode('.jpeg', frame)
            imagem = jpeg.tobytes()

            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + imagem + b'\r\n\r\n')

        else:
            break
            
    video.release()
