import cv2
import mediapipe as mp
import serial
import time
import random
import math

# Inicialização do Arduino (ajuste a porta conforme necessário)
arduino = serial.Serial('COM3', 9600, timeout=1)
time.sleep(2)

# Inicialização do MediaPipe
mp_face = mp.solutions.face_mesh
face_mesh = mp_face.FaceMesh(max_num_faces=1)
mp_draw = mp.solutions.drawing_utils

cap = cv2.VideoCapture(0)

# Limiar para detectar piscadas
LIMIAR_FECHAR = 0.38
LIMIAR_ABRIR = 0.42
frames_fechado = 0
piscadas = 0
tiros = 0
acertos = 0

# Criação de um alvo inicial
alvo_x = random.randint(100, 500)
alvo_y = random.randint(100, 400)
alvoraio = 40

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame = cv2.flip(frame, 1)
    altura, largura, _ = frame.shape


    # Converte imagem para RGB
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resultados = face_mesh.process(rgb)

    # Desenha o alvo
    cv2.circle(frame, (alvo_x, alvo_y), alvoraio, (255, 0, 0), -1)

    if resultados.multi_face_landmarks:
        pontos = resultados.multi_face_landmarks[0].landmark

        # Desenha malha facial
        mp_draw.draw_landmarks(frame, resultados.multi_face_landmarks[0],
                               mp_face.FACEMESH_TESSELATION)

        # EAR (Eye Aspect Ratio)
        h = abs(pontos[33].x - pontos[133].x)
        v1 = abs(pontos[159].y - pontos[145].y)
        v2 = abs(pontos[158].y - pontos[153].y)
        ear = (v1 + v2) / (2.0 * h)
        
        # Posição do centro do rosto (usando ponto do nariz)
        nariz_x = int(pontos[1].x * largura)
        nariz_y = int(pontos[1].y * altura)
        cv2.circle(frame, (nariz_x, nariz_y), 5, (255, 255, 255), -1)

        # Exibe EAR na tela
        cv2.putText(frame, f"EAR: {ear:.2f}", (10, 60),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)

        # Detecta piscada
        if ear <= LIMIAR_FECHAR:
            frames_fechado += 1
        elif ear > LIMIAR_ABRIR:
            if frames_fechado >= 2:
                piscadas += 1
                tiros += 1

                # Verifica se "mirou" no alvo
                dist = math.hypot(nariz_x - alvo_x, nariz_y - alvo_y)
                if dist < alvoraio:
                    acertos += 1
                    arduino.write(b'G')  # Acerto = LED verde
                    # Gera novo alvo
                    alvo_x = random.randint(100, 500)
                    alvo_y = random.randint(100, 400)
                else:
                    arduino.write(b'R')  # Erro = LED vermelho

            frames_fechado = 0

    # Exibe contadores
    cv2.putText(frame, f"PISCADAS: {piscadas}", (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.putText(frame, f"ACERTOS: {acertos}", (10, 90),
                cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
    cv2.putText(frame, f"TIROS: {tiros}", (10, 120),
                cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 200), 2)

    # Exibe imagem
    cv2.imshow("Jogo com Piscadas - Mira com Nariz", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
arduino.close()
cv2.destroyAllWindows()