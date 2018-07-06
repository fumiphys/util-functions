# -*- coding: utf-8 -*-

import cv2


if __name__ == '__main__':
    capt = cv2.VideoCapture(0)

    while True:
        ret, frame = capt.read()

        cv2.imshow("camera", frame)

        if cv2.waitKey(0) & 0xFF == ord('q'):
            break

    capt.release()
    cv2.destroyAllWindows()
