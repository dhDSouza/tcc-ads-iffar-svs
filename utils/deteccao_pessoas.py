# Importando bibliotecas necessárias
import cv2
import numpy as np
from ultralytics import YOLO
from datetime import datetime

def realizar_heatmap(camera_ip):
    # Inicializando a captura de vídeo com o endereço IP da câmera
    video = cv2.VideoCapture(camera_ip)
    # Carregando o modelo YOLO pré-treinado
    modelo = YOLO('yolov8n.pt')

    # Criando uma imagem em branco para o heatmap
    imagem_branca = np.ones([360, 640], np.uint32)

    while video.isOpened():
        # Lendo o próximo frame do vídeo
        status, frame = video.read()

        if status:
            # Redimensionando o frame para o formato esperado pelo modelo YOLO
            frame = cv2.resize(frame, (640, 360))

            # Executando o modelo YOLO no frame atual
            resultados = modelo(frame, classes=0, conf=0.3, iou=0.1, stream=True)

            # Iterando sobre os resultados do modelo
            for resultado in resultados:

                boxes = resultado.boxes

                # Iterando sobre as caixas delimitadoras encontradas
                for box in boxes:

                    x1, y1, x2, y2 = box.xyxy[0]
                    x1, y1, x2, y2 = map(int, [x1, y1, x2, y2])
                    largura = x2 - x1
                    altura = y2 - y1

                    # Aumentando o valor da região da caixa delimitadora no heatmap
                    imagem_branca[y1:y2, x1:x2] += 1
                    # Desenhando a caixa delimitadora no frame original
                    cv2.rectangle(frame, (x1, y1), (x1 + largura, y1 + altura), (255, 0, 255), 2)

            # Normalizando e suavizando o heatmap
            imagem_branca_normalizada = 255 * ((imagem_branca - imagem_branca.min()) / (imagem_branca.max() - imagem_branca.min()))
            imagem_branca_normalizada = imagem_branca_normalizada.astype('uint8')
            imagem_branca_normalizada = cv2.GaussianBlur(imagem_branca_normalizada, (9, 9), 0)

            # Aplicando um mapa de cores ao heatmap
            heat_map = cv2.applyColorMap(imagem_branca_normalizada, cv2.COLORMAP_JET)
            # Combinando o heatmap com o frame original
            frame_final = cv2.addWeighted(heat_map, 0.5, frame, 0.5, 0)

            # Codificando o frame final em formato JPEG
            _, jpeg = cv2.imencode('.jpeg', frame_final)
            imagem = jpeg.tobytes()

            # Retornando o frame final como parte do streaming de vídeo
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + imagem + b'\r\n\r\n')

        else:
            # Finalizando o loop quando o vídeo termina
            break

    # Liberando os recursos da captura de vídeo
    video.release()

def realizar_contagem(camera_ip, linha, entrada):

    # Importando o módulo 'mongo' do aplicativo
    from app import mongo

    # Inicializando a captura de vídeo com o endereço IP da câmera
    video = cv2.VideoCapture(camera_ip)
    # Carregando o modelo YOLO pré-treinado
    modelo = YOLO('yolov8n.pt')

    ids = []  # Lista para rastrear IDs únicos
    _id = None  # Variável para armazenar o ID atual
    contador = 0  # Inicializando o contador

    while video.isOpened():
        # Lendo o próximo frame do vídeo
        status, frame = video.read()

        if status:
            # Redimensionando o frame para o formato esperado pelo modelo YOLO
            frame = cv2.resize(frame, (640, 360))

            # Desenhando a linha de contagem no frame
            cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (255, 255, 255), 2)

            # Adicionando a contagem atual no frame
            cv2.putText(frame, f'Contador: {contador}', (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

            # Executando o modelo YOLO no frame atual
            resultados = modelo.track(frame, classes=0, conf=0.3, iou=0.1, stream=True, persist=True)

            # Iterando sobre os resultados do modelo
            for resultado in resultados:

                boxes = resultado.boxes

                # Iterando sobre as caixas delimitadoras encontradas
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

                    # Desenhando a caixa delimitadora e informações no frame
                    cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 0, 255), 2)
                    cv2.circle(frame, (centro_x, centro_y), 2, (255, 0, 255), 2)
                    cv2.putText(frame, str(int(_id)), (x1, y1 - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

                    # Determinando a posição da linha de contagem (vertical ou horizontal)
                    if linha[0] == linha[2]:
                        posicao = 'vertical'
                    elif linha[1] == linha[3]:
                        posicao = 'horizontal'

                    if _id not in ids:

                        # Verifica se a posição da linha é vertical
                        if posicao == 'vertical':

                            # Verifica se a direção de entrada é pela esquerda
                            if entrada == 'esquerda':

                                # Verifica se o centro da caixa está dentro da margem à esquerda da linha
                                if linha[1] < centro_y < linha[3] and centro_x < linha[0] and centro_x >= linha[0] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    # Registra a entrada no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now().timestamp(),
                                        'saida': ''
                                    })
                                    # Desenha uma linha verde no frame indicando a contagem
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)

                            # Verifica se a direção de entrada é pela direita
                            elif entrada == 'direita':

                                # Verifica se o centro da caixa está dentro da margem à direita da linha
                                if linha[1] < centro_y < linha[3] and centro_x > linha[0] and centro_x <= linha[0] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    # Registra a entrada no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now().timestamp(),
                                        'saida': ''
                                    })                                    
                                    # Desenha uma linha verde no frame indicando a contagem
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)

                        # Caso a posição da linha não seja vertical (assume-se que seja horizontal)
                        else:

                            # Verifica se a direção de entrada é de cima para baixo
                            if entrada == 'cima':

                                # Verifica se o centro da caixa está acima da linha dentro da margem
                                if linha[0] < centro_x < linha[2] and centro_y < linha[1] and centro_y >= linha[1] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    # Registra a entrada no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now().timestamp(),
                                        'saida': ''
                                    })                                    
                                    # Desenha uma linha verde no frame indicando a contagem
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)

                            # Verifica se a direção de entrada é de baixo para cima
                            elif entrada == 'baixo':

                                # Verifica se o centro da caixa está abaixo da linha dentro da margem
                                if linha[0] < centro_x < linha[2] and centro_y > linha[1] and centro_y <= linha[1] - 15:
                                    contador += 1
                                    ids.append(_id)
                                    # Registra a entrada no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': datetime.now().timestamp(),
                                        'saida': ''
                                    })
                                    # Desenha uma linha verde no frame indicando a contagem
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 255, 0), 2)
                    
                    else:

                        # Verifica se a posição da linha é vertical
                        if posicao == 'vertical':

                            # Verifica se a direção de entrada é pela esquerda
                            if entrada == 'esquerda':

                                # Verifica se o centro da caixa está dentro da margem à direita da linha
                                if linha[1] < centro_y < linha[3] and centro_x > linha[0] and centro_x <= linha[0] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    # Registra a saída no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now().timestamp()
                                    })
                                    # Desenha uma linha vermelha no frame indicando a contagem inversa
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

                            # Verifica se a direção de entrada é pela direita
                            elif entrada == 'direita':

                                # Verifica se o centro da caixa está dentro da margem à esquerda da linha
                                if linha[1] < centro_y < linha[3] and centro_x < linha[0] and centro_x >= linha[0] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    # Registra a saída no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now().timestamp()
                                    })                                    
                                    # Desenha uma linha vermelha no frame indicando a contagem inversa
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

                        # Caso a posição da linha não seja vertical (assume-se que seja horizontal)
                        else:

                            # Verifica se a direção de entrada é de cima para baixo
                            if entrada == 'cima':

                                # Verifica se o centro da caixa está abaixo da linha dentro da margem
                                if linha[0] < centro_x < linha[2] and centro_y > linha[1] and centro_y <= linha[1] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    # Registra a saída no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now().timestamp()
                                    })                                    
                                    # Desenha uma linha vermelha no frame indicando a contagem inversa
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

                            # Verifica se a direção de entrada é de baixo para cima
                            elif entrada == 'baixo':

                                # Verifica se o centro da caixa está acima da linha dentro da margem
                                if linha[0] < centro_x < linha[2] and centro_y < linha[1] and centro_y >= linha[1] + 15:
                                    contador -= 1
                                    ids.remove(_id)
                                    # Registra a saída no banco de dados com o timestamp atual
                                    mongo.get_database().get_collection('registros').insert_one({
                                        'camera_ip': camera_ip,
                                        'entrada': '',
                                        'saida': datetime.now().timestamp()
                                    })
                                    # Desenha uma linha vermelha no frame indicando a contagem inversa
                                    cv2.line(frame, (linha[0], linha[1]), (linha[2], linha[3]), (0, 0, 255), 2)

            # Prepara a imagem para transmissão
            _, jpeg = cv2.imencode('.jpeg', frame)
            imagem = jpeg.tobytes()

            # Retorna a imagem como um frame JPEG
            yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + imagem + b'\r\n\r\n')

        else:
            # Finalizando o loop quando o vídeo termina
            break

    # Liberando os recursos da captura de vídeo
    video.release()
