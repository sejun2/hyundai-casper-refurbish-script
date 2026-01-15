#!/usr/bin/env python3
"""
현대 캐스퍼 특별기획전 재고 확인 스크립트
- 리퍼브 기획전(R0003)과 다른 특별기획전(E20260133) 전용
"""

import requests
import json
from typing import Optional, Dict, Any, List
from enum import Enum


class SpecialCarModel(Enum):
    """특별기획전 캐스퍼 차량 모델"""
    CASPER_2026 = {
        "name": "2026 캐스퍼",
        "carCode": "AX06",
        "subsidyRegion": "",
        "minSalePrice": "15923000",
        "maxSalePrice": "17875000"
    }
    CASPER_ELECTRIC_2026 = {
        "name": "2026 캐스퍼 일렉트릭",
        "carCode": "AX05",
        "subsidyRegion": "2800",
        "minSalePrice": "35877000",
        "maxSalePrice": "37306000"
    }
    CASPER_NEW = {
        "name": "더 뉴 캐스퍼",
        "carCode": "AX04",
        "subsidyRegion": "",
        "minSalePrice": "",
        "maxSalePrice": ""
    }
    CASPER_ELECTRIC = {
        "name": "캐스퍼 일렉트릭",
        "carCode": "AX03",
        "subsidyRegion": "2800",
        "minSalePrice": "32060670",
        "maxSalePrice": "32060670"
    }


class SpecialChecker:
    """특별기획전 재고 확인 클래스"""

    # 특별기획전 번호
    EXHIBITION_NO = "E20260133"

    def __init__(self):
        self.base_url = f"https://casper.hyundai.com/gw/wp/product/v2/product/exhibition/cars/{self.EXHIBITION_NO}"
        self.headers = {
            "accept": "application/json, text/plain, */*",
            "accept-encoding": "gzip, deflate, br, zstd",
            "accept-language": "ko,en-US;q=0.9,en;q=0.8,ja;q=0.7",
            "content-type": "application/json;charset=UTF-8",
            "origin": "https://casper.hyundai.com",
            "referer": f"https://casper.hyundai.com/vehicles/car-list/promotion?exhbNo={self.EXHIBITION_NO}",
            "sec-ch-ua": '"Google Chrome";v="143", "Chromium";v="143", "Not A(Brand";v="24"',
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": '"macOS"',
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36",
            "ep-channel": "wpc",
            "ep-ip": "127.0.0.1",
            "ep-jsessionid": "",
            "ep-menu-id": f"/vehicles/car-list/promotion?exhbNo={self.EXHIBITION_NO}",
            "ep-version": "v2",
            "service-type": "product",
            "url": f"/vehicles/car-list/promotion?exhbNo={self.EXHIBITION_NO}",
            "x-b3-sampled": "1"
        }

    def check_inventory(
        self,
        model: Optional[SpecialCarModel] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        특별기획전 재고를 확인합니다.

        Args:
            model: SpecialCarModel enum (없으면 2026 캐스퍼)
            custom_params: 추가 커스텀 파라미터 (딕셔너리)

        Returns:
            API 응답 데이터
        """
        # 기본 모델 설정
        if model is None and custom_params is None:
            model = SpecialCarModel.CASPER_2026

        # 기본 파라미터 구성
        if custom_params is None:
            if model:
                model_data = model.value
                params = {
                    "carCode": model_data["carCode"],
                    "subsidyRegion": model_data["subsidyRegion"],
                    "exhbNo": self.EXHIBITION_NO,
                    "sortCode": "10",
                    "deliveryAreaCode": "H",
                    "deliveryLocalAreaCode": "H0",
                    "carBodyCode": "",
                    "carEngineCode": "",
                    "carTrimCode": "",
                    "exteriorColorCode": "",
                    "interiorColorCode": [],
                    "deliveryCenterCode": "",
                    "wpaScnCd": "",
                    "optionFilter": "",
                    "minSalePrice": model_data["minSalePrice"],
                    "maxSalePrice": model_data["maxSalePrice"],
                    "choiceOptYn": "Y",
                    "pageNo": 1,
                    "pageSize": 100
                }
            else:
                params = {
                    "carCode": "",
                    "subsidyRegion": "",
                    "exhbNo": self.EXHIBITION_NO,
                    "sortCode": "10",
                    "deliveryAreaCode": "H",
                    "deliveryLocalAreaCode": "H0",
                    "carBodyCode": "",
                    "carEngineCode": "",
                    "carTrimCode": "",
                    "exteriorColorCode": "",
                    "interiorColorCode": [],
                    "deliveryCenterCode": "",
                    "wpaScnCd": "",
                    "optionFilter": "",
                    "minSalePrice": "",
                    "maxSalePrice": "",
                    "choiceOptYn": "Y",
                    "pageNo": 1,
                    "pageSize": 100
                }
        else:
            params = custom_params

        try:
            response = requests.post(
                self.base_url,
                headers=self.headers,
                json=params,
                timeout=10
            )
            response.raise_for_status()

            return {
                "success": True,
                "status_code": response.status_code,
                "data": response.json(),
                "model": model.value["name"] if model else "전체"
            }

        except requests.exceptions.RequestException as e:
            return {
                "success": False,
                "error": str(e),
                "status_code": getattr(e.response, 'status_code', None) if hasattr(e, 'response') else None,
                "model": model.value["name"] if model else "전체"
            }

    def get_car_count(
        self,
        model: Optional[SpecialCarModel] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> int:
        """재고 개수를 반환합니다."""
        result = self.check_inventory(model, custom_params)

        if result["success"]:
            response_data = result["data"]
            if "data" in response_data and "totalCount" in response_data["data"]:
                return response_data["data"]["totalCount"]

        return 0

    def get_car_list(
        self,
        model: Optional[SpecialCarModel] = None,
        custom_params: Optional[Dict[str, Any]] = None
    ) -> list:
        """재고 차량 리스트를 반환합니다."""
        result = self.check_inventory(model, custom_params)

        if result["success"]:
            response_data = result["data"]
            if "data" in response_data and "discountsearchcars" in response_data["data"]:
                return response_data["data"]["discountsearchcars"]

        return []

    def check_all_models(self) -> Dict[str, Any]:
        """모든 모델의 재고를 한번에 확인합니다."""
        results = {}

        for model in SpecialCarModel:
            count = self.get_car_count(model)
            results[model.value["name"]] = {
                "count": count,
                "carCode": model.value["carCode"],
                "available": count > 0
            }

        return results

    def search_by_region(
        self,
        model: SpecialCarModel,
        sido_name: str,
        sigun_name: Optional[str] = None,
        **kwargs
    ) -> List[Dict[str, Any]]:
        """
        지역명으로 재고를 검색합니다.

        Args:
            model: 차량 모델
            sido_name: 시도명 (예: "경북", "서울")
            sigun_name: 시군구명 (예: "포항시", 선택사항)
            **kwargs: 추가 필터 옵션

        Returns:
            해당 지역의 차량 리스트
        """
        try:
            from region_helper import get_codes
            area_code, local_code = get_codes(sido_name, sigun_name)
        except (ImportError, ValueError) as e:
            print(f"지역 코드 조회 실패: {e}")
            print("fetch_regions.py를 먼저 실행하세요.")
            return []

        model_data = model.value

        params = {
            "carCode": model_data["carCode"],
            "subsidyRegion": model_data["subsidyRegion"],
            "exhbNo": self.EXHIBITION_NO,
            "sortCode": "10",
            "deliveryAreaCode": area_code,
            "deliveryLocalAreaCode": local_code,
            "carBodyCode": "",
            "carEngineCode": "",
            "carTrimCode": "",
            "exteriorColorCode": "",
            "interiorColorCode": [],
            "deliveryCenterCode": "",
            "wpaScnCd": "",
            "optionFilter": "",
            "minSalePrice": model_data["minSalePrice"],
            "maxSalePrice": model_data["maxSalePrice"],
            "choiceOptYn": "Y",
            "pageNo": 1,
            "pageSize": 100
        }

        params.update(kwargs)

        return self.get_car_list(custom_params=params)

    def print_car_info(self, car: Dict[str, Any]) -> None:
        """차량 정보를 보기 좋게 출력합니다."""
        print(f"\n{'='*60}")
        print(f"{car.get('carName', 'N/A')} - {car.get('saleModelName', 'N/A')}")
        print(f"{'='*60}")
        print(f"트림: {car.get('carTrimName', 'N/A')}")
        print(f"외장색: {car.get('exteriorColorName', 'N/A')}")
        print(f"내장색: {car.get('interiorColorName', 'N/A')}")

        print(f"\n가격 정보:")
        car_price = car.get('carPrice', '0')
        discount_price = car.get('discountPrice', '0')
        final_amount = car.get('finalAmount', '0')
        discount_rate = car.get('discountRate', '0')

        print(f"  차량 가격: {int(float(car_price)):,}원")
        print(f"  할인 금액: {int(float(discount_price)):,}원 ({discount_rate}%)")
        print(f"  최종 금액: {int(float(final_amount)):,}원")

        print(f"\n출고 정보:")
        print(f"  출고센터: {car.get('deliveryCenterName', 'N/A')}")
        prdnDt = car.get('prdnDt', '')
        if prdnDt and len(prdnDt) >= 8:
            print(f"  생산일: {prdnDt[:4]}-{prdnDt[4:6]}-{prdnDt[6:8]}")
        print(f"  차대번호: {car.get('carProductionNumber', 'N/A')}")
        print(f"{'='*60}\n")


def main():
    """메인 실행 함수"""
    checker = SpecialChecker()

    print("="*70)
    print(f"현대 캐스퍼 특별기획전 재고 확인 (기획전번호: {checker.EXHIBITION_NO})")
    print("="*70)

    # 모든 모델 재고 확인
    print("\n전체 모델 재고 현황:")
    print("-"*70)
    all_models = checker.check_all_models()

    total_stock = 0
    for model_name, info in all_models.items():
        status = "O" if info["available"] else "X"
        print(f"[{status}] {model_name:<25} | 재고: {info['count']:>3}대 | 코드: {info['carCode']}")
        total_stock += info["count"]

    print("-"*70)
    print(f"총 재고: {total_stock}대")

    # 재고가 있는 모델 상세 정보
    print("\n" + "="*70)
    print("재고 상세 정보")
    print("="*70)

    for model in SpecialCarModel:
        count = checker.get_car_count(model)

        if count > 0:
            print(f"\n[{model.value['name']}] - 총 {count}대")
            print("-"*70)

            cars = checker.get_car_list(model)
            for i, car in enumerate(cars[:5], 1):
                exterior = car.get('exteriorColorName', 'N/A')
                trim = car.get('carTrimName', 'N/A')
                final = int(float(car.get('finalAmount', 0)))
                discount = int(float(car.get('discountPrice', 0)))
                center = car.get('deliveryCenterName', 'N/A')

                print(f"  [{i}] {exterior} | {trim}")
                print(f"      가격: {final:,}원 (할인 {discount:,}원)")
                print(f"      출고: {center}")

            if count > 5:
                print(f"\n  ... 외 {count - 5}대 더 있음")


if __name__ == "__main__":
    main()
