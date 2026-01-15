#!/usr/bin/env python3
"""
캐스퍼 특별기획전 전국 재고 검색

특별기획전(E20260133) 전용 전국 재고 검색 스크립트입니다.
리퍼브 기획전(R0003)은 run_search.py를 사용하세요.
"""

import time
from datetime import datetime
from special_checker import SpecialChecker, SpecialCarModel
from region_helper import RegionHelper
from typing import Dict, List


def check_all_regions(model: SpecialCarModel) -> Dict[str, Dict[str, List]]:
    """
    전국 모든 지역의 특별기획전 재고를 검색합니다.

    Args:
        model: 검색할 차량 모델

    Returns:
        지역별 재고 딕셔너리
    """
    helper = RegionHelper()
    checker = SpecialChecker()

    if not helper.is_available():
        print("지역 데이터가 없습니다.")
        print("먼저 실행: python fetch_regions.py")
        return {}

    results = {}
    total_cars = 0

    print(f"\n[특별기획전] 전국 재고 검색 중... (모델: {model.value['name']})")
    print("="*80)

    sidos = helper.list_sidos()

    for i, sido in enumerate(sidos, 1):
        print(f"\n[{i:2d}/17] {sido} ", end="")
        print("-"*70)

        siguns = helper.list_siguns(sido)

        sido_total = 0
        sido_results = {}

        if len(siguns) > 1:
            for sigun in siguns:
                try:
                    cars = checker.search_by_region(model, sido, sigun)
                    if cars:
                        sido_results[sigun] = cars
                        sido_total += len(cars)
                        print(f"  [O] {sigun:<20} {len(cars):>3}대")
                except Exception:
                    pass
                time.sleep(0.1)

            if sido_total == 0:
                print(f"  [X] 재고 없음")
        else:
            try:
                cars = checker.search_by_region(model, sido)
                if cars:
                    sido_results[sido] = cars
                    sido_total = len(cars)
                    print(f"  [O] {sido:<20} {sido_total:>3}대")
                else:
                    print(f"  [X] 재고 없음")
            except Exception:
                print(f"  [!] 오류")

        results[sido] = sido_results
        total_cars += sido_total

        if sido_total > 0:
            print(f"  {'─'*70}")
            print(f"  >> {sido} 합계: {sido_total}대")

        time.sleep(0.2)

    print("\n" + "="*80)
    print(f"[완료] 전국 총 재고: {total_cars}대\n")

    return results


def print_summary(results: Dict[str, Dict[str, List]], model: SpecialCarModel):
    """검색 결과 요약 출력"""
    if not results:
        print("검색 결과가 없습니다.")
        return

    print("\n" + "="*80)
    print(f"[특별기획전] 전국 재고 요약 - {model.value['name']}")
    print("="*80)

    regions_with_stock = []
    for sido, sigun_dict in results.items():
        if sigun_dict:
            for sigun, cars in sigun_dict.items():
                if cars:
                    regions_with_stock.append((sido, sigun, cars))

    if not regions_with_stock:
        print("\n전국에 재고가 없습니다.")
        return

    regions_with_stock.sort(key=lambda x: len(x[2]), reverse=True)

    print(f"\n{'시도':<8} {'시군구':<20} {'재고':<8} {'최저가':<15} {'최고가':<15}")
    print("-"*80)

    sido_totals = {}

    for sido, sigun, cars in regions_with_stock:
        count = len(cars)
        min_price = min(int(float(car['finalAmount'])) for car in cars)
        max_price = max(int(float(car['finalAmount'])) for car in cars)

        print(f"{sido:<8} {sigun:<20} {count:<8} {min_price:>12,}원 {max_price:>12,}원")

        if sido not in sido_totals:
            sido_totals[sido] = 0
        sido_totals[sido] += count

    print("-"*80)
    print("\n시도별 합계:")
    print("-"*80)
    for sido, total in sorted(sido_totals.items(), key=lambda x: x[1], reverse=True):
        if total > 0:
            print(f"  {sido:<10} {total:>3}대")

    total = sum(sido_totals.values())
    print("-"*80)
    print(f"  {'전국 합계':<10} {total:>3}대")
    print("="*80)


def print_detail(results: Dict[str, Dict[str, List]], max_per_region: int = 3):
    """상세 정보 출력"""
    print("\n" + "="*80)
    print(f"[특별기획전] 지역별 상세 정보 (각 시군구 최대 {max_per_region}대)")
    print("="*80)

    for sido, sigun_dict in results.items():
        if not sigun_dict:
            continue

        sido_total = sum(len(cars) for cars in sigun_dict.values())
        if sido_total == 0:
            continue

        print(f"\n{'='*80}")
        print(f">> {sido} - 총 {sido_total}대")
        print(f"{'='*80}")

        for sigun, cars in sigun_dict.items():
            if not cars:
                continue

            print(f"\n  [{sigun}] - {len(cars)}대")
            print("  " + "-"*76)

            for i, car in enumerate(cars[:max_per_region], 1):
                exterior = car.get('exteriorColorName', 'N/A')
                trim = car.get('carTrimName', 'N/A')
                final = int(float(car.get('finalAmount', 0)))
                discount = int(float(car.get('discountPrice', 0)))
                center = car.get('deliveryCenterName', 'N/A')

                print(f"  {i}. {exterior:<15} | {trim:<12} | {final:>12,}원 | 할인 {discount:>10,}원")
                print(f"     출고: {center}")

            if len(cars) > max_per_region:
                print(f"     ... 외 {len(cars) - max_per_region}대")


def save_results(results: Dict[str, Dict[str, List]], model: SpecialCarModel, filename: str = None):
    """결과를 JSON 파일로 저장"""
    import json

    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"special_stock_{model.value['carCode']}_{timestamp}.json"

    total_count = 0
    for sigun_dict in results.values():
        for cars in sigun_dict.values():
            total_count += len(cars)

    data = {
        "timestamp": datetime.now().isoformat(),
        "exhibition_type": "특별기획전",
        "exhibition_no": SpecialChecker.EXHIBITION_NO,
        "model": model.value['name'],
        "model_code": model.value['carCode'],
        "total_count": total_count,
        "regions": {}
    }

    for sido, sigun_dict in results.items():
        if not sigun_dict:
            continue

        data["regions"][sido] = {}

        for sigun, cars in sigun_dict.items():
            if not cars:
                continue

            data["regions"][sido][sigun] = [
                {
                    "color": car.get('exteriorColorName', ''),
                    "interior": car.get('interiorColorName', ''),
                    "trim": car.get('carTrimName', ''),
                    "price": car.get('finalAmount', ''),
                    "discount": car.get('discountPrice', ''),
                    "discount_rate": car.get('discountRate', ''),
                    "center": car.get('deliveryCenterName', ''),
                    "production_date": car.get('prdnDt', ''),
                }
                for car in cars
            ]

    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"\n결과 저장: {filename}")


def main():
    """메인 실행 함수"""
    print("="*70)
    print("캐스퍼 특별기획전 전국 재고 검색")
    print(f"기획전 번호: {SpecialChecker.EXHIBITION_NO}")
    print("="*70)
    print("\n* 리퍼브 기획전은 run_search.py를 사용하세요.\n")

    # 모델 선택
    print("모델을 선택하세요:")
    models = list(SpecialCarModel)
    for i, model in enumerate(models, 1):
        print(f"{i}. {model.value['name']}")
    print(f"{len(models) + 1}. 모든 모델 (전체 검색)")

    try:
        choice = input(f"\n모델 번호 (1-{len(models) + 1}): ").strip()

        if choice == str(len(models) + 1):
            search_all_models = True
            selected_models = models
        else:
            model_idx = int(choice) - 1

            if model_idx < 0 or model_idx >= len(models):
                print("잘못된 선택입니다.")
                return

            search_all_models = False
            selected_models = [models[model_idx]]

    except (ValueError, KeyboardInterrupt):
        print("\n중단됨")
        return

    if search_all_models:
        print("\n" + "="*70)
        print("[특별기획전] 모든 모델 전국 재고 검색")
        print("="*70)

        all_results = {}
        for model in selected_models:
            print(f"\n{'='*70}")
            print(f"모델: {model.value['name']}")
            print(f"{'='*70}")

            results = check_all_regions(model)
            all_results[model.value['name']] = results
            print_summary(results, model)

            if model != selected_models[-1]:
                time.sleep(1)

        # 전체 요약
        print("\n" + "="*80)
        print("[특별기획전] 전체 모델 재고 요약")
        print("="*80)

        for model_name, results in all_results.items():
            total = 0
            regions_count = 0
            for sigun_dict in results.values():
                if sigun_dict:
                    regions_count += len([s for s in sigun_dict.values() if s])
                    for cars in sigun_dict.values():
                        total += len(cars)

            print(f"\n{model_name}")
            print(f"  전국 재고: {total}대")
            print(f"  재고 있는 시군구: {regions_count}개")

        # 상세 정보
        detail = input("\n각 모델의 상세 정보를 보시겠습니까? (y/n): ").strip().lower()
        if detail == 'y':
            for model_name, results in all_results.items():
                print(f"\n{'='*70}")
                print(f"{model_name} 상세")
                print(f"{'='*70}")
                print_detail(results, max_per_region=2)

        # 저장
        save = input("\n결과를 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            for i, (model_name, results) in enumerate(all_results.items()):
                model = selected_models[i]
                save_results(results, model)
    else:
        # 단일 모델 검색
        results = check_all_regions(selected_models[0])
        print_summary(results, selected_models[0])

        detail = input("\n상세 정보를 보시겠습니까? (y/n): ").strip().lower()
        if detail == 'y':
            print_detail(results)

        save = input("\n결과를 저장하시겠습니까? (y/n): ").strip().lower()
        if save == 'y':
            save_results(results, selected_models[0])


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n중단됨")
    except Exception as e:
        print(f"\n오류 발생: {e}")
        import traceback
        traceback.print_exc()
