Open 2 cmd prompt and put below commands

```commandline 
cd ~/SmartTrafficLight/Smart-Traffic-System
source .venv/bin/activate
```

Tab 1

```commandline
python vehicle_detection.py --cam=http://172.27.207.154:8080/video
```

Tab 2

```commandline
python final_traffic.py
```

If any issue with camera check port with below command

```commandline
v4l2-ctl --list-devices
```
