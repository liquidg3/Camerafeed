#Camerafeed
A simple app (or can be used as a module) to track people as they move in a video. You can also draw "triplines" that
will emit events when a person crosses them. You can use the camerafeed module in your own app or you can run it as a
stand-alone app that pulls from settings.ini.

##Getting Started
1. First things first, you gotta install Python 3.4+ and OpenCV 3.0+. Luckily, computer vision expert __Adrian__ has made his
fantastic [tutorials available](http://www.pyimagesearch.com/opencv-tutorials-resources-guides/).
2. Clone the repo:
    ```bash
    $ git clone git@github.com:liquidg3/Camerafeed.git
    ```
3. Jump into the repo
    ```bash
    $ cd Camerafeed
    ```
4. Install additional dependencies
    ```bash
    $ pip setup.py develop
    ```
5. Run the app
    ```bash
    $python run.py
    ```

##Settings
Checkout `settings.ini` for everything you can customize when running Camerafeed as an app.

```ini
[video_source]
#the video to load (put 0 to use your computer's camera)
source : footage/sample-trimmed.m4v
```
```ini
#the following are for cropping the video (try and only show parts you need)
frame_x1 : 250
frame_y1 : 40
frame_x2 : 550
frame_y2 : 240
```
```ini
#set a max width and the video will be proportionality scaled to this size (smaller is usually better)
max_width : 500
```
```ini
#black and white?
b_and_w : False
```
```ini
#settings for hog.detectMultiScale
[hog]
win_stride : 4
padding : 6
scale : 1.05
```
```ini
#use background removal
[mog]
enabled : False
```
```ini
#when tracking a person
[person]
life : 20 #how many frames to wait before considering the person gone
max_distance : 50 #how far can a person move between detections?
```
```ini
#for crossing lines
[triplines]
total_lines = 1
line1_start : (100,60)
line1_end : (200, 160)
line1_buffer : 10
line1_direction_1: north
line1_direction_2: south
```
```ini
line2_start : (50,180)
line2_end : (200, 150)
line2_buffer : 10
line2_direction_1: out
line2_direction_2: in

```

##Recommended Reading
1. [Pedestrian Detection OpenCV](http://www.pyimagesearch.com/2015/11/09/pedestrian-detection-opencv/)
2. [HOG detectMultiScale parameters explained](http://www.pyimagesearch.com/2015/11/16/hog-detectmultiscale-parameters-explained/)