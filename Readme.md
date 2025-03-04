# Run
```bash
$ uvicorn main:app --reload

# 포트 지정 실행
$ uvicorn main:app --reload --port 8001   
```
* http://127.0.0.1:8000
  ![image](https://github.com/user-attachments/assets/01a7dde4-28ea-4d24-906d-92815c7efbc5)

# API 문서
### - ReDic
* http://127.0.0.1:8000/redoc
### - Swagger
* http://127.0.0.1:8000/docs
![image](https://github.com/user-attachments/assets/bdcc14fc-3de3-40d9-ae92-a31857bc30b0)

# 환경 구성 (WatchMAN+ 연동)
![image](https://github.com/user-attachments/assets/e3d7951a-f060-42a6-9a56-963b9123ec2a)
- (참고)USB C to AUX 젠더 : https://search.shopping.naver.com/catalog/40569751618?adId=nad-a001-02-000000248726605&channel=nshop.npla&query=usbCtoaux&NaPm=ct%3Dm29ryveg%7Cci%3D0zW0002VLKPBKsZ8Hfib%7Ctr%3Dpla%7Chk%3Dd6a8f05e6f257c7193a79876f2b883fd10d53985%7Cnacn%3D7RcxBUwRwSGM&cid=0zW0002VLKPBKsZ8Hfib
- (참고)AUX 케이블 4극 : [https://smartstore.naver.com/machsys/products/5060409987?n_media=11068&n_query=AUX4%EA%B7%B9&n_rank=1&n_ad_group=grp-a001-02-000000037996760&n_ad=nad-a001-02-000000268959871&n_campaign_type=2&n_mall_id=mach611&n_mall_pid=5060409987&n_ad_group_type=2&n_match=3&NaPm=ct%3Dm2a46aug%7Cci%3D0Hb%2D003f5KTBjFsyhLiF%7Ctr%3Dpla%7Chk%3D12648b7f2721357ddcb4baafac6bed6468ef5be0%7Cnacn%3D7RcxBUwRwSGM](https://search.shopping.naver.com/catalog/18713142965?query=aux%20%EC%BC%80%EC%9D%B4%EB%B8%94%204%EA%B7%B9&NaPm=ct%3Dm2a49d6o%7Cci%3D28e8ecfa7d3cfa5d122485c2329747e3b68a0f10%7Ctr%3Dslsl%7Csn%3D95694%7Chk%3D7a9e538cebac95936d99c2410383c4f1ae90318d)
# port 사용중인 process 확인 
- Mac/Linux ```lsof -i :8000```
- Windows  ```netstat -ano | findstr :8000```


## FastAPI 디버그 구성 만들기(PyCharm)
1. **PyCharm 실행**: 먼저 PyCharm에서 FastAPI 프로젝트를 엽니다. 

2. **Run/Debug Configuration 설정**: 
* 상단 메뉴에서 **Run** > **Edit Configurations**로 이동합니다. 
* 왼쪽 상단의 **"+"** 버튼을 클릭하고, **Python**을 선택해 새로운 설정을 추가합니다. 
3. **Configuration 설정**:
* **Name**: 이 필드에 적절한 이름을 지정합니다 (예: "FastAPI Debug"). 
* **Script Path**: `uvicorn` 모듈을 직접 실행할 것이므로, **Module name**을 선택한 후 `uvicorn`이라고 입력합니다. 
* **Parameters**: FastAPI 애플리케이션을 실행할 때 사용하는 인자를 입력합니다. 예를 들어,

```
main:app --reload
````
여기서 `main:app`은 `main.py` 파일 안의 FastAPI 인스턴스 `app`을 의미합니다. 

* **Python Interpreter**: 현재 프로젝트에서 사용 중인 Python 인터프리터를 선택합니다.”


