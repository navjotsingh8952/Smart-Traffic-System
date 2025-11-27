Open 2 cmd prompt and put below commands


GiTBash in laptop for connecting to rasp pi

```commandline
cd ~/SmartTrafficLight/Smart-Traffic-System
source .venv/bin/activate
python final_traffic.py
```

GiTBash in laptop for Vehicle detection

```commandline
cd ~/Desktop/Smart-Traffic-System
source .venv/Scripts/activate
python vehicle_detection.py --cam=http://172.27.207.154:8080/video
```