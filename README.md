# Real-Time Drone Flight Fault Detection System [2021.03~2021.12]<br>
<mark>보수 공사 중으로, 곧 새로운 코드가 업데이트 될 예정입니다.</mark><br>
## Overview
* Needs, Problems<br>
 최근 4차 산업 혁명의 부상과 함께 더불어 주목받고 있는 분야가 드론, 그 중에서도 자율 주행이 가능한 드론이다. 하지만 드론의 완전한 자율 주행 구현은 난이도가 높아 아직 많이 개척되지 않은 분야이며, 여러 이슈를 갖고 있다. 그 중에서도 '드론의 신속, 정확한 이상 탐지'에 대한 수요가 있다. 드론의 내부 안전 장치가 약하고 정교하지 못해 드론의 비상 임무 수행 시 안전 예측 및 갑작스런 고장에 대한 대응에 어려움이 있기 때문이다. 드론 손상 시 손실되는 비용의 문제 역시 심각하다. 따라서 드론 자율 주행의 성능, 신뢰 수준을 높이기 위해 드론의 하드웨어 및 소프트웨어 문제를 감지하기 위한 모델과 이를 적용한 시스템이 필요하다.

* Goals, objectives<br>
 실시간으로 드론의 이상을 감지하고 관련 정보를 시각화해서 보여주는 대시보드를 개발한다.
![image](https://user-images.githubusercontent.com/48075848/143085416-e147f761-4ef6-4782-8e79-e05a1f31611d.png)


* Tech Stack
    - Data Storage: Google Cloud BigQuery
    - Pipeline(ETL), Event Publisher: Google Dataflow (use code written by Apache Beam)
    - Real Time Event: Google Cloud Pub/Sub
    - LSTM Model: Pytorch
    - Visualization: Bokeh

## Model Development & Evaluation
- Dataset: https://github.com/mrtbrnz/fault_detection
- Model: LSTM
- GCS log data (실제 시스템에서 사용 가능한 데이터)를 가공해 학습한 모델의 accuracy
![image](https://user-images.githubusercontent.com/48075848/122979223-44745680-d3d2-11eb-9537-f40cf2404e4d.png)

## Results
![Hnet com-image](https://user-images.githubusercontent.com/48075848/144088827-0e4dae4e-7cd7-49e5-85e1-aae0ce6c085a.gif)

## Reports
발표 슬라이드: https://drive.google.com/file/d/1qQ00HKr3U7K7Xuv-jqbAivG-1mp5c8GH/view?usp=sharing<br>
논문: https://drive.google.com/file/d/1YLvcg1MeU5_jR6eLRPNVXIUnFGQRPk9N/view?usp=sharing
