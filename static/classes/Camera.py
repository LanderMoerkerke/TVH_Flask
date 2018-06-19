import cv2
import time
from shutil import copyfile
from skimage.io import imsave


class Camera():
    # Constructor...
    def __init__(self):
        self.cap = cv2.VideoCapture(1)  # Prepare the camera...
        # time.sleep(1)

        # Prepare Capture
        self.ret, self.frame = self.cap.read()

        # Prepare output window...
        self.winName = "Motion Indicator"
        # cv2.namedWindow(self.winName, cv2.WINDOW_AUTOSIZE)

    # Frame generation for Browser streaming wiht Flask...
    def get_frame(self):
        self.frames = open("static/uploads/camera.jpg", 'wb+')
        s, img = self.cap.read()
        if s:  # frame captures without errors...
            cv2.imwrite("static/uploads/camera.jpg", img)  # Save image...
            # imsave("static/uploads/camera.jpg", img)  # Save image...
        return self.frames.read()

    def get_pic(self):
        s, img = self.cap.read()
        if s:  # frame captures without errors...
            cv2.imwrite("static/uploads/camera_sk.jpg", img)  # Save image...
            # imsave("static/uploads/camera_sk.jpg", img)  # Save image...
        return img

    def captureVideo(self):
        # Read in a new frame...
        self.ret, self.frame = self.cap.read()
        cv2.imshow(self.winName, self.frame)
        return ()

    def __del__(self):
        self.cap.release()
        cv2.destroyAllWindows()
        print("Camera disabled and all output windows closed...")
        return ()


def main():
    # Create a camera instance...
    cam1 = Camera()

    while (True):
        # Display the resulting frames...
        cam1.captureVideo()  # Live stream of video on screen...
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    return ()


if __name__ == '__main__':
    main()
