# *******************************************************************
#
# Author : Thanh Nguyen, 2018
# Email  : sthanhng@gmail.com
# Github : https://github.com/sthanhng
#
# BAP, AI Team
# Face detection using the YOLOv3 algorithm
#
# Description : yoloface.py
# The main code of the Face detection using the YOLOv3 algorithm
#
# *******************************************************************

# Usage example:  python yoloface.py --image samples/outside_000001.jpg \
#                                    --output-dir outputs/
#                 python yoloface.py --video samples/subway.mp4 \
#                                    --output-dir outputs/
#                 python yoloface.py --src 1 --output-dir outputs/

import time
import argparse
import sys
import os
import glob
# from sexmodel.sexnet import *



from utils import *

#####################################################################
#parser = argparse.ArgumentParser()
#parser.add_argument('--model-cfg', type=str, default='./cfg/yolov3-face.cfg',
#                    help='path to config file')
#parser.add_argument('--model-weights', type=str,
#                    default='./model-weights/yolov3-wider_16000.weights',
#                    help='path to weights of model')
#parser.add_argument('--image', type=str, default='',
#                    help='path to image file')
#parser.add_argument('--video', type=str, default='',
#                    help='path to video file')
#parser.add_argument('--src', type=int, default=0,
#                    help='source of the camera')
#parser.add_argument('--output-dir', type=str, default='outputs/',
#                    help='path to the output directory')
#args = parser.parse_args()

#####################################################################
# print the arguments
print('----- info -----')
#print('[i] The config file: ', args.model_cfg)
#print('[i] The weights of model file: ', args.model_weights)
#print('[i] Path to image file: ', args.image)
#print('[i] Path to video file: ', args.video)
#print('###########################################################\n')

# check outputs directory

def _main(filetype,finput,foutputdir,foutputname):
    print("--------tracking start")
    # net = cv2.dnn.readNetFromDarknet('./yoloface/cfg/yolov3-face.cfg', './yoloface/model-weights/yolov3-wider_16000.weights')
    net = cv2.dnn.readNetFromDarknet('./cfg/yolov3-face.cfg', './model-weights/yolov3-wider_16000.weights')
    net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
    net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

    # wind_name = 'face detection using YOLOv3'
    #cv2.namedWindow(wind_name, cv2.WINDOW_NORMAL)
    output_file = ''
    foutput = foutputdir + os.sep +foutputname 
    cap = None
    print("finput:"+finput)
    print("filetype:"+filetype)
    if filetype=="image":
        if not os.path.isfile(finput):
            print("[!] ==> Input image file {} doesn't exist".format(finput))
            sys.exit(1)
        cap = cv2.VideoCapture(finput)
        output_file = foutput
    elif filetype=="movie":
        if not os.path.isfile(finput):
            print("[!] ==> Input video file {} doesn't exist".format(finput))
            sys.exit(1)
        cap = cv2.VideoCapture(finput)
        output_file = foutput
    # else:
        # Get data from the camera
        # cap = cv2.VideoCapture(args.src)

    # Get the video writer initialized to save the output video
    video_writer = None
    if filetype=="movie":
        video_writer = cv2.VideoWriter(output_file,
                                       cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'),
                                       cap.get(cv2.CAP_PROP_FPS), (
                                           round(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                                           round(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))))

    while True:

        has_frame, frame = cap.read()

        # Stop the program if reached end of video
        if not has_frame:
            print('[i] ==> Done processing!!!')
            print('[i] ==> Output file is stored at', output_file)
            cv2.waitKey(1000)
            break

        # Create a 4D blob from a frame.
        blob = cv2.dnn.blobFromImage(frame, 1 / 255, (IMG_WIDTH, IMG_HEIGHT),
                                     [0, 0, 0], 1, crop=False)

        # Sets the input to the network
        net.setInput(blob)

        # Runs the forward pass to get output of the output layers
        outs = net.forward(get_outputs_names(net))

        # Remove the bounding boxes with low confidence
        faces = post_process(frame, outs, CONF_THRESHOLD, NMS_THRESHOLD,foutputname)
        print('[i] ==> # detected faces: {}'.format(len(faces)))
        print(type(faces))
        print(type(faces[0]))

        print('#' * 60)
        # initialize the set of information we'll displaying on the frame
        info = [
            ('number of faces detected', '{}'.format(len(faces)))
        ]

        # for (i, (txt, val)) in enumerate(info):
        #     text = '{}: {}'.format(txt, val)

            #TODO 23.3.5
            # 顔を切り出し、予測をかける
            # 取得したラベルをtextにセットする。
            # print("----------------------------")
            # print(txt+":"+val)
            
                



            # cv2.putText(frame, text, (10, (i * 20) + 20),
            #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, COLOR_RED, 2)
        

        # Save the output video to file
        if filetype=="image":
            print("")
            # cv2.imwrite(output_file, frame.astype(np.uint8))
        else:
            video_writer.write(frame.astype(np.uint8))

        #cv2.imshow(wind_name, frame)

        key = cv2.waitKey(1)
        if key == 27 or key == ord('q'):
            print('[i] ==> Interrupted by user!')
            break

    cap.release()
    cv2.destroyAllWindows()
    if(not video_writer == None):
        video_writer.release()
    # foutput = foutputdir + "/tmp"+foutputname
    # time.sleep(1)
    # os.rename(foutput,foutputdir + os.sep+foutputname) 
    print('==> All done!')
    print('***********************************************************')


if __name__ == '__main__':
    
     finputpath = "C:"+os.sep+"work"+os.sep+"kapp"+os.sep+"kapp"+os.sep+"application"+os.sep+"input\*"  
     foutputdir = "C:"+os.sep+"work"+os.sep+"kapp"+os.sep+"kapp"+os.sep+"application"+os.sep+"output"
     filename = "test.jpg"
     files = glob.glob(finputpath)
     cnt = 0
     for finputpath in files:
        cnt = cnt + 1
        if cnt % 100 == 0:
            print(cnt)
        filename = os.path.split(finputpath)[1]
        try:
            _main("image",finputpath,foutputdir,filename)
        except Exception as e:
            print(filename)
            print(e)
