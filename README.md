# Hyundai Casper 재고 확인

현대 캐스퍼 재고 확인 스크립트

## 설치

```bash
pip install -r requirements.txt
python fetch_regions.py  # 최초 1회 - 지역 데이터 수집
```

## 실행 방법

### 리퍼브 기획전 (R0003)

```bash
python run_search.py         # 전국 재고 검색
python casper_checker.py     # 기본 재고 확인
python search_by_region.py   # 대화형 지역 검색
python monitor.py            # 실시간 모니터링
```

### 특별기획전 (E20260133)

```bash
python run_special.py        # 전국 재고 검색
python special_checker.py    # 기본 재고 확인
```

## 지원 모델

| 모델명 | 코드 | 비고 |
|--------|------|------|
| 2026 캐스퍼 일렉트릭 | AX05 | 전기차 |
| 2026 캐스퍼 | AX06 | 일반 |
| 캐스퍼 일렉트릭 | AX03 | 전기차 |
| 더 뉴 캐스퍼 | AX04 | 일반 |
