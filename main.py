import cv2
import numpy as np

cap = cv2.VideoCapture('aeropuerto.mp4')

fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

while True:
    ret, frame = cap.read()
    if ret == False: break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Dibujamos un rectángulo en frame, para señalar el estado
    # del área en análisis (movimiento detectado o no detectado)
    cv2.rectangle(frame,(0,0),(frame.shape[1],40),(0,0,0),-1)
    color = (0, 255, 0)
    texto_estado = "Estado: No se ha detectado movimiento"

    # Especificamos los puntos extremos del área a analizar
    area_pts = np.array([[0, 0], [frame.shape[1], 0], [frame.shape[1], frame.shape[0]], [0, frame.shape[0]]])
    
    # Con ayuda de una imagen auxiliar, determinamos el área
    # sobre la cual actuará el detector de movimiento
    imAux = np.zeros(shape=(frame.shape[:2]), dtype=np.uint8)
    imAux = cv2.drawContours(imAux, [area_pts], -1, (255), -1)
    image_area = cv2.bitwise_and(gray, gray, mask=imAux)

    fgmask = fgbg.apply(image_area)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    fgmask = cv2.dilate(fgmask, None, iterations=2)

    cnts = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[0]
    
    # Variables para almacenar la persona más cercana al centro
    min_distance = float('inf')
    closest_person = None
    
    for cnt in cnts:
        if cv2.contourArea(cnt) > 500:
            x, y, w, h = cv2.boundingRect(cnt)
            center_x = x + w // 2
            center_y = y + h // 2
            distance = np.sqrt((frame.shape[1] // 2 - center_x) ** 2 + (frame.shape[0] // 2 - center_y) ** 2)
            
            # Actualizar la persona más cercana al centro
            if distance < min_distance:
                min_distance = distance
                closest_person = cnt
    
    if closest_person is not None:
        x, y, w, h = cv2.boundingRect(closest_person)
        cv2.rectangle(frame, (x,y), (x+w, y+h),(0,255,0), 2)
        texto_estado = "Estado: Alerta Movimiento Detectado!"
        color = (0, 0, 255)    

    # Visualizamos el alrededor del área que vamos a analizar
    # y el estado de la detección de movimiento        
    cv2.drawContours(frame, [area_pts], -1, color, 2)
    cv2.putText(frame, texto_estado , (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color,2)

    cv2.imshow('fgmask', fgmask)
    cv2.imshow("frame", frame)

    k = cv2.waitKey(70) & 0xFF
    if k == 27:
        break

cap.release()
cv2.destroyAllWindows()