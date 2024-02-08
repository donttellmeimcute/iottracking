import cv2
import numpy as np

cap = cv2.VideoCapture('video.mp4')

fgbg = cv2.createBackgroundSubtractorMOG2()
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(3,3))

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    cv2.rectangle(frame,(0,0),(frame.shape[1],40),(0,0,0),-1)
    color = (0, 255, 0)
    texto_estado = "Estado: En espera"

    area_pts = np.array([[0, 0], [frame.shape[1], 0], [frame.shape[1], frame.shape[0]], [0, frame.shape[0]]])
    
    imAux = np.zeros(shape=(frame.shape[:2]), dtype=np.uint8)
    imAux = cv2.drawContours(imAux, [area_pts], -1, (255), -1)
    image_area = cv2.bitwise_and(gray, gray, mask=imAux)

    fgmask = fgbg.apply(image_area)
    fgmask = cv2.morphologyEx(fgmask, cv2.MORPH_OPEN, kernel)
    fgmask = cv2.dilate(fgmask, None, iterations=2)
    depth_map = cv2.applyColorMap(fgmask, cv2.COLORMAP_JET)
    depth_map = cv2.bitwise_and(frame, frame, mask=fgmask)

    cnts, _ = cv2.findContours(fgmask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    merged_rect = None 
    
    for cnt in cnts:
        if cv2.contourArea(cnt) > 20:
            x, y, w, h = cv2.boundingRect(cnt)
            if merged_rect is None:
                merged_rect = (x, y, x+w, y+h)  
            else:
                merged_rect = (min(merged_rect[0], x), min(merged_rect[1], y), max(merged_rect[2], x+w), max(merged_rect[3], y+h))
            texto_estado = "Estado: movimiento detectado"
            color = (0, 0, 255)    
            
    if merged_rect is not None:
        x, y, w, h = merged_rect
        cv2.rectangle(frame, (x, y), (w, h), color, 2)
        center_x = int((x + w) / 2)
        center_y = int((y + h) / 2)
        cv2.circle(frame, (center_x, center_y), 5, (0, 255, 0), -1)
        print("Coordenadas del centro: ({}, {})".format(center_x - frame.shape[1] // 2, frame.shape[0] // 2 - center_y))

    cv2.drawContours(frame, [area_pts], -1, color, 2)
    cv2.putText(frame, texto_estado , (10, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 1, color,2)

    cv2.imshow('depth_map', depth_map)
    cv2.imshow("frame", frame)

    if cv2.waitKey(70) == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()