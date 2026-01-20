"""
1. 데이터셋 생성
"""

import pandas as pd
from datetime import datetime

# 테이블 1: 상품 데이터 (전자기기와 컴퓨터 카테고리 통합)
products = [
    {"id": "P001", "name": "프리미엄 헤드폰", "category": "전자기기", "brand": "사운드마스터", "price": 129000, "stock": 45, "rating": 4.7, "discount": 10},
    {"id": "P002", "name": "유기농 바나나", "category": "식품", "brand": "자연마을", "price": 8900, "stock": 120, "rating": 4.8, "discount": 0},
    {"id": "P003", "name": "울트라 슬림 노트북", "category": "전자기기", "brand": "테크노바", "price": 1290000, "stock": 10, "rating": 4.8, "discount": 5},
    {"id": "P004", "name": "프리미엄 가죽 지갑", "category": "패션", "brand": "럭셔리스타일", "price": 89000, "stock": 30, "rating": 4.6, "discount": 0},
    {"id": "P005", "name": "캐주얼 스니커즈", "category": "신발", "brand": "스포츠플러스", "price": 79000, "stock": 25, "rating": 4.4, "discount": 20},
    {"id": "P006", "name": "실내 자전거", "category": "스포츠", "brand": "피트니스마스터", "price": 350000, "stock": 8, "rating": 4.9, "discount": 8},
    {"id": "P007", "name": "아로마 테라피 세트", "category": "뷰티", "brand": "힐링라이프", "price": 35000, "stock": 15, "rating": 4.6, "discount": 12},
    {"id": "P008", "name": "무선 블루투스 이어폰", "category": "전자기기", "brand": "사운드마스터", "price": 159000, "stock": 35, "rating": 4.5, "discount": 15},
    {"id": "P009", "name": "프로틴 파우더", "category": "건강식품", "brand": "헬시라이프", "price": 45000, "stock": 18, "rating": 4.7, "discount": 10},
    {"id": "P010", "name": "프로그래밍 책 세트", "category": "도서", "brand": "지식출판", "price": 120000, "stock": 22, "rating": 4.8, "discount": 5},
    {"id": "P011", "name": "유아 교구 세트", "category": "유아용품", "brand": "키즈랜드", "price": 85000, "stock": 15, "rating": 4.9, "discount": 7},
    {"id": "P012", "name": "스테인리스 냄비세트", "category": "주방용품", "brand": "홈쿠킹", "price": 159000, "stock": 12, "rating": 4.6, "discount": 15},
    {"id": "P013", "name": "면세점 향수 세트", "category": "화장품", "brand": "프랑스향수", "price": 210000, "stock": 20, "rating": 4.7, "discount": 8},
    {"id": "P014", "name": "고급 침대 프레임", "category": "가구", "brand": "슬립웰", "price": 890000, "stock": 5, "rating": 4.5, "discount": 10},
    {"id": "P015", "name": "게이밍 마우스", "category": "전자기기", "brand": "게이머프로", "price": 89000, "stock": 30, "rating": 4.8, "discount": 5},
    {"id": "P016", "name": "대형 선인장 화분", "category": "원예", "brand": "그린가든", "price": 35000, "stock": 25, "rating": 4.4, "discount": 0},
    {"id": "P017", "name": "레트로 턴테이블", "category": "음향기기", "brand": "올드스쿨", "price": 320000, "stock": 8, "rating": 4.9, "discount": 5},
    {"id": "P018", "name": "스마트 TV", "category": "전자기기", "brand": "디지털라이프", "price": 750000, "stock": 15, "rating": 4.6, "discount": 12},
    {"id": "P019", "name": "강아지 장난감 세트", "category": "반려동물", "brand": "펫라이프", "price": 28000, "stock": 40, "rating": 4.3, "discount": 5},
    {"id": "P020", "name": "캠핑 텐트", "category": "아웃도어", "brand": "네이처하이킹", "price": 180000, "stock": 18, "rating": 4.7, "discount": 10}
]

# 테이블 2: 사용자 데이터
users = [
    {"id": "U001", "name": "김철수", "email": "kim@example.com", "phone": "010-1234-5678", "address": "서울시 강남구 테헤란로 123", "points": 5000, "membership": "골드"},
    {"id": "U002", "name": "이영희", "email": "lee@example.com", "phone": "010-2345-6789", "address": "서울시 서초구 서초대로 456", "points": 2500, "membership": "실버"},
    {"id": "U003", "name": "박지민", "email": "park@example.com", "phone": "010-3456-7890", "address": "서울시 송파구 올림픽로 789", "points": 1000, "membership": "브론즈"},
    {"id": "U004", "name": "정수민", "email": "jung@example.com", "phone": "010-4567-8901", "address": "서울시 마포구 홍대로 101", "points": 4800, "membership": "골드"},
    {"id": "U005", "name": "최유진", "email": "choi@example.com", "phone": "010-5678-9012", "address": "서울시 영등포구 여의도로 202", "points": 12000, "membership": "플래티넘"},
    {"id": "U006", "name": "강민수", "email": "kang@example.com", "phone": "010-6789-0123", "address": "서울시 종로구 종로 333", "points": 800, "membership": "브론즈"},
    {"id": "U007", "name": "윤서연", "email": "yoon@example.com", "phone": "010-7890-1234", "address": "서울시 용산구 이태원로 444", "points": 3200, "membership": "실버"},
    {"id": "U008", "name": "장준호", "email": "jang@example.com", "phone": "010-8901-2345", "address": "서울시 강서구 공항대로 555", "points": 7500, "membership": "골드"},
    {"id": "U009", "name": "한지원", "email": "han@example.com", "phone": "010-9012-3456", "address": "서울시 강동구 천호대로 666", "points": 1500, "membership": "브론즈"},
    {"id": "U010", "name": "오민지", "email": "oh@example.com", "phone": "010-0123-4567", "address": "서울시 성북구 성북로 777", "points": 6400, "membership": "골드"}
]

# 테이블 3: 장바구니 데이터
carts = [
    {"id": "C001", "user_id": "U001", "product_id": "P001", "quantity": 1, "added_at": "2025-04-10 14:30"},
    {"id": "C002", "user_id": "U001", "product_id": "P003", "quantity": 1, "added_at": "2025-04-10 14:35"},
    {"id": "C003", "user_id": "U002", "product_id": "P002", "quantity": 2, "added_at": "2025-04-12 10:15"},
    {"id": "C004", "user_id": "U003", "product_id": "P005", "quantity": 2, "added_at": "2025-04-13 16:45"},
    {"id": "C005", "user_id": "U004", "product_id": "P004", "quantity": 1, "added_at": "2025-04-14 09:20"},
    {"id": "C006", "user_id": "U005", "product_id": "P007", "quantity": 1, "added_at": "2025-04-14 11:30"},
    {"id": "C007", "user_id": "U006", "product_id": "P009", "quantity": 3, "added_at": "2025-04-15 13:45"},
    {"id": "C008", "user_id": "U007", "product_id": "P012", "quantity": 1, "added_at": "2025-04-15 14:20"},
    {"id": "C009", "user_id": "U008", "product_id": "P015", "quantity": 2, "added_at": "2025-04-15 15:10"},
    {"id": "C010", "user_id": "U009", "product_id": "P016", "quantity": 1, "added_at": "2025-04-15 16:30"}
]

# 테이블 4: 주문 데이터
orders = [
    {"id": "O001", "user_id": "U001", "order_date": "2025-04-01 15:30", "total": 1419000, "payment_method": "신용카드", "payment_status": "완료", "delivery_status": "배송완료"},
    {"id": "O002", "user_id": "U002", "order_date": "2025-04-05 11:20", "total": 17800, "payment_method": "무통장입금", "payment_status": "완료", "delivery_status": "배송중"},
    {"id": "O003", "user_id": "U003", "order_date": "2025-04-08 09:45", "total": 126400, "payment_method": "간편결제", "payment_status": "완료", "delivery_status": "배송준비중"},
    {"id": "O004", "user_id": "U001", "order_date": "2025-03-20 16:00", "total": 89000, "payment_method": "신용카드", "payment_status": "완료", "delivery_status": "배송완료"},
    {"id": "O005", "user_id": "U004", "order_date": "2025-04-10 13:15", "total": 89000, "payment_method": "간편결제", "payment_status": "취소", "delivery_status": "취소됨"},
    {"id": "O006", "user_id": "U005", "order_date": "2025-04-11 10:30", "total": 35000, "payment_method": "신용카드", "payment_status": "완료", "delivery_status": "배송완료"},
    {"id": "O007", "user_id": "U006", "order_date": "2025-04-12 14:45", "total": 135000, "payment_method": "간편결제", "payment_status": "완료", "delivery_status": "배송중"},
    {"id": "O008", "user_id": "U007", "order_date": "2025-04-13 09:20", "total": 159000, "payment_method": "신용카드", "payment_status": "완료", "delivery_status": "배송준비중"},
    {"id": "O009", "user_id": "U008", "order_date": "2025-04-14 11:15", "total": 178000, "payment_method": "무통장입금", "payment_status": "완료", "delivery_status": "배송준비중"},
    {"id": "O010", "user_id": "U009", "order_date": "2025-04-15 15:40", "total": 35000, "payment_method": "간편결제", "payment_status": "대기중", "delivery_status": "주문접수"}
]

# 테이블 5: 주문 상세 데이터
order_items = [
    {"id": "OI001", "order_id": "O001", "product_id": "P001", "quantity": 1, "price": 129000, "discount_price": 116100},
    {"id": "OI002", "order_id": "O001", "product_id": "P003", "quantity": 1, "price": 1290000, "discount_price": 1225500},
    {"id": "OI003", "order_id": "O002", "product_id": "P002", "quantity": 2, "price": 8900, "discount_price": 8900},
    {"id": "OI004", "order_id": "O003", "product_id": "P005", "quantity": 2, "price": 79000, "discount_price": 63200},
    {"id": "OI005", "order_id": "O004", "product_id": "P004", "quantity": 1, "price": 89000, "discount_price": 89000},
    {"id": "OI006", "order_id": "O005", "product_id": "P004", "quantity": 1, "price": 89000, "discount_price": 89000},
    {"id": "OI007", "order_id": "O006", "product_id": "P007", "quantity": 1, "price": 35000, "discount_price": 30800},
    {"id": "OI008", "order_id": "O007", "product_id": "P009", "quantity": 3, "price": 45000, "discount_price": 40500},
    {"id": "OI009", "order_id": "O008", "product_id": "P012", "quantity": 1, "price": 159000, "discount_price": 135150},
    {"id": "OI010", "order_id": "O009", "product_id": "P015", "quantity": 2, "price": 89000, "discount_price": 84550},
    {"id": "OI011", "order_id": "O010", "product_id": "P016", "quantity": 1, "price": 35000, "discount_price": 35000}
]

# 테이블 6: 배송 데이터
deliveries = [
    {"id": "D001", "order_id": "O001", "courier": "CJ대한통운", "tracking_number": "123456789012", "start_date": "2025-04-02", "end_date": "2025-04-04", "status": "배송완료"},
    {"id": "D002", "order_id": "O002", "courier": "로젠택배", "tracking_number": "234567890123", "start_date": "2025-04-06", "end_date": None, "status": "배송중"},
    {"id": "D003", "order_id": "O003", "courier": "한진택배", "tracking_number": "345678901234", "start_date": None, "end_date": None, "status": "배송준비중"},
    {"id": "D004", "order_id": "O004", "courier": "우체국택배", "tracking_number": "456789012345", "start_date": "2025-03-21", "end_date": "2025-03-23", "status": "배송완료"},
    {"id": "D005", "order_id": "O005", "courier": "", "tracking_number": "", "start_date": None, "end_date": None, "status": "취소됨"},
    {"id": "D006", "order_id": "O006", "courier": "CJ대한통운", "tracking_number": "567890123456", "start_date": "2025-04-12", "end_date": "2025-04-13", "status": "배송완료"},
    {"id": "D007", "order_id": "O007", "courier": "로젠택배", "tracking_number": "678901234567", "start_date": "2025-04-13", "end_date": None, "status": "배송중"},
    {"id": "D008", "order_id": "O008", "courier": "한진택배", "tracking_number": "789012345678", "start_date": None, "end_date": None, "status": "배송준비중"},
    {"id": "D009", "order_id": "O009", "courier": "CJ대한통운", "tracking_number": "890123456789", "start_date": None, "end_date": None, "status": "배송준비중"},
    {"id": "D010", "order_id": "O010", "courier": "", "tracking_number": "", "start_date": None, "end_date": None, "status": "주문접수"}
]

# 테이블 7: 리뷰 데이터
reviews = [
    {"id": "R001", "user_id": "U001", "product_id": "P001", "order_id": "O001", "rating": 5, "content": "음질이 정말 좋고 착용감도 편안합니다.", "date": "2025-04-05", "helpful_count": 12},
    {"id": "R002", "user_id": "U001", "product_id": "P003", "order_id": "O001", "rating": 4, "content": "가볍고 성능이 좋아요. 배터리가 조금 아쉽습니다.", "date": "2025-04-05", "helpful_count": 8},
    {"id": "R003", "user_id": "U002", "product_id": "P002", "order_id": "O002", "rating": 5, "content": "정말 맛있고 신선해요! 다음에 또 구매할게요.", "date": "2025-04-10", "helpful_count": 5},
    {"id": "R004", "user_id": "U001", "product_id": "P004", "order_id": "O004", "rating": 4, "content": "가죽 질감이 좋고 수납공간이 넉넉합니다.", "date": "2025-03-25", "helpful_count": 3},
    {"id": "R005", "user_id": "U003", "product_id": "P005", "order_id": "O003", "rating": 3, "content": "디자인은 좋지만 내구성이 조금 아쉽습니다.", "date": "2025-04-12", "helpful_count": 1},
    {"id": "R006", "user_id": "U005", "product_id": "P007", "order_id": "O006", "rating": 5, "content": "향이 너무 좋고 효과도 만족스러워요.", "date": "2025-04-14", "helpful_count": 7},
    {"id": "R007", "user_id": "U006", "product_id": "P009", "order_id": "O007", "rating": 4, "content": "맛은 괜찮은데 가격이 조금 비싼 것 같아요.", "date": "2025-04-15", "helpful_count": 2},
    {"id": "R008", "user_id": "U007", "product_id": "P012", "order_id": "O008", "rating": 5, "content": "열전도율이 좋고 세척도 편리해요.", "date": "2025-04-16", "helpful_count": 4},
    {"id": "R009", "user_id": "U008", "product_id": "P015", "order_id": "O009", "rating": 5, "content": "게임할 때 정확하고 반응속도가 빨라요.", "date": "2025-04-16", "helpful_count": 6},
    {"id": "R010", "user_id": "U001", "product_id": "P008", "order_id": "O001", "rating": 4, "content": "노이즈캔슬링 기능이 훌륭하네요.", "date": "2025-04-05", "helpful_count": 9}
]

# 테이블 8: 쿠폰 데이터
coupons = [
    {"id": "CP001", "name": "신규가입 10% 할인", "discount_type": "percent", "discount_value": 10, "min_order": 50000, "max_discount": 50000, "start_date": "2025-01-01", "end_date": "2025-12-31"},
    {"id": "CP002", "name": "전자기기 15% 할인", "discount_type": "percent", "discount_value": 15, "min_order": 100000, "max_discount": 100000, "start_date": "2025-04-01", "end_date": "2025-04-30"},
    {"id": "CP003", "name": "5천원 할인", "discount_type": "amount", "discount_value": 5000, "min_order": 30000, "max_discount": 5000, "start_date": "2025-04-01", "end_date": "2025-04-20"},
    {"id": "CP004", "name": "패션 20% 할인", "discount_type": "percent", "discount_value": 20, "min_order": 50000, "max_discount": 30000, "start_date": "2025-04-01", "end_date": "2025-05-31"},
    {"id": "CP005", "name": "VIP 회원 특별 20% 할인", "discount_type": "percent", "discount_value": 20, "min_order": 200000, "max_discount": 100000, "start_date": "2025-04-01", "end_date": "2025-04-15"},
    {"id": "CP006", "name": "생일 축하 15% 할인", "discount_type": "percent", "discount_value": 15, "min_order": 20000, "max_discount": 30000, "start_date": "2025-04-10", "end_date": "2025-05-10"},
    {"id": "CP007", "name": "반려동물용품 10% 할인", "discount_type": "percent", "discount_value": 10, "min_order": 30000, "max_discount": 20000, "start_date": "2025-04-15", "end_date": "2025-04-30"},
    {"id": "CP008", "name": "식품 2만원 할인", "discount_type": "amount", "discount_value": 20000, "min_order": 100000, "max_discount": 20000, "start_date": "2025-04-01", "end_date": "2025-04-30"},
    {"id": "CP009", "name": "주방용품 30% 할인", "discount_type": "percent", "discount_value": 30, "min_order": 50000, "max_discount": 50000, "start_date": "2025-04-10", "end_date": "2025-04-25"},
    {"id": "CP010", "name": "첫 구매 1만원 할인", "discount_type": "amount", "discount_value": 10000, "min_order": 30000, "max_discount": 10000, "start_date": "2025-01-01", "end_date": "2025-12-31"}
]

# 테이블 9: 사용자 쿠폰 데이터
user_coupons = [
    {"id": "UC001", "user_id": "U001", "coupon_id": "CP001", "issue_date": "2023-05-15", "used": True, "use_date": "2025-04-01"},
    {"id": "UC002", "user_id": "U001", "coupon_id": "CP002", "issue_date": "2025-04-01", "used": False, "use_date": None},
    {"id": "UC003", "user_id": "U002", "coupon_id": "CP003", "issue_date": "2025-04-02", "used": True, "use_date": "2025-04-05"},
    {"id": "UC004", "user_id": "U003", "coupon_id": "CP003", "issue_date": "2025-04-05", "used": True, "use_date": "2025-04-08"},
    {"id": "UC005", "user_id": "U004", "coupon_id": "CP004", "issue_date": "2025-04-03", "used": False, "use_date": None},
    {"id": "UC006", "user_id": "U005", "coupon_id": "CP005", "issue_date": "2025-04-01", "used": False, "use_date": None},
    {"id": "UC007", "user_id": "U006", "coupon_id": "CP006", "issue_date": "2025-04-11", "used": True, "use_date": "2025-04-12"},
    {"id": "UC008", "user_id": "U007", "coupon_id": "CP004", "issue_date": "2025-04-10", "used": True, "use_date": "2025-04-13"},
    {"id": "UC009", "user_id": "U008", "coupon_id": "CP002", "issue_date": "2025-04-05", "used": True, "use_date": "2025-04-14"},
    {"id": "UC010", "user_id": "U009", "coupon_id": "CP010", "issue_date": "2025-04-01", "used": False, "use_date": None}
]

# 테이블 10: 약관 데이터
regulations = [
    # 주문 취소
    {"keyword": "주문 취소", "content": "주문 취소는 상품이 출고되기 전에는 언제든 가능합니다. 출고 이후에는 반품으로 처리됩니다."},
    {"keyword": "주문 취소", "content": "주문 취소 시 사용한 포인트는 자동 환불됩니다."},
    {"keyword": "주문 취소", "content": "주문 취소는 상준몰 주문내역 > 주문취소 버튼을 통해 가능합니다."},

    # 반품
    {"keyword": "반품", "content": "반품 신청은 배송일로부터 5일 이내에 가능합니다."},
    {"keyword": "반품", "content": "반품 시 왕복 배송비가 부과됩니다."},
    {"keyword": "반품", "content": "반품 신청은 상준몰 주문내역 > 배송완료 > 반품 버튼을 눌러 신청할 수 있습니다."},

    # 환불
    {"keyword": "환불", "content": "환불 처리는 반품 완료 후 3영업일 이내에 진행됩니다."},
    {"keyword": "환불", "content": "결제 수단에 따라 환불 소요 시간이 달라질 수 있습니다."},
    {"keyword": "환불", "content": "카드 환불은 카드사 영업일 기준으로 약 5~7일 소요됩니다."},

    # 배송
    {"keyword": "배송", "content": "상품은 결제일로부터 2~3일 이내 출고됩니다."},
    {"keyword": "배송", "content": "배송은 택배사를 통해 이루어지며 평균 배송 소요 기간은 3~5일입니다."},
    {"keyword": "배송", "content": "배송 조회는 상준몰 마이페이지 > 주문내역 > 배송조회 버튼을 통해 확인할 수 있습니다."},

    # 재입고
    {"keyword": "재입고", "content": "일부 품절 상품은 재입고 시점이 불확정입니다."},
    {"keyword": "재입고", "content": "상품 상세 페이지에서 '재입고 알림 신청'이 가능하면 알림 설정을 해주세요."},
    {"keyword": "재입고", "content": "재입고 여부는 판매자 또는 상준몰 담당자가 별도 안내드립니다."}
]

# (실제 서비스에서는 외부 데이터베이스나 API를 통해 데이터가 입력된다고 가정)
df_products   = pd.DataFrame(products)
df_users      = pd.DataFrame(users)
df_carts      = pd.DataFrame(carts)
df_orders     = pd.DataFrame(orders)
df_order_items= pd.DataFrame(order_items)
df_deliveries = pd.DataFrame(deliveries)
df_reviews    = pd.DataFrame(reviews) # 실제 함수에서 사용되지는 않았습니다.
df_coupons    = pd.DataFrame(coupons)
df_user_coupons = pd.DataFrame(user_coupons)
df_regulations = pd.DataFrame(regulations)


"""
2. 함수 생성
"""

# 1. 장바구니 상태 조회 함수
def show_cart(user_id):
    user_cart = df_carts[df_carts['user_id'] == user_id].copy()
    # 제품 정보와 조인 (제품명, 가격, 수량 등)
    user_cart = user_cart.merge(df_products[['id', 'name', 'price']],
                                left_on='product_id', right_on='id',
                                suffixes=('', '_prod'))
    user_cart = user_cart[['id', 'name', 'price', 'quantity', 'added_at']]
    if user_cart.empty:
        return {
            "success": False,
            "message": f"사용자 {user_id}님의 장바구니에 상품이 없습니다."
        }
    return {
        "success": True,
        "user_id": user_id,
        "item_count": len(user_cart),
        "cart_items": user_cart.to_dict(orient="records")
    }


# 2. 제품 검색 함수 (예: "노트북")
def search_product(keyword, category=None):
    # 기본 키워드로 제품명에 포함하는 항목 검색
    condition = df_products['name'].str.contains(keyword, case=False, na=False)
    if category:
        condition &= df_products['category'] == category
    results = df_products[condition]
    if results.empty:
        return {
            "success": False,
            "message": f"키워드 '{keyword}'에 해당하는 상품을 찾을 수 없습니다."
        }
    # 평점 순 혹은 최신상품 등 다양한 기준을 적용할 수 있음. 여기서는 평점순 정렬을 예로 사용
    results = results.sort_values(by='rating', ascending=False)
    return {
        "success": True,
        "keyword": keyword,
        "category_filter": category,
        "result_count": len(results),
        "products": results.to_dict(orient="records")
    }

# 3. 장바구니에 상품 추가하는 함수
def add_to_cart(user_id, product_id, quantity=1):
    global df_carts
    new_id = f"C{str(len(df_carts) + 1).zfill(3)}"
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M")

    new_item = {
        "id": new_id,
        "user_id": user_id,
        "product_id": product_id,
        "quantity": quantity,
        "added_at": now_str
    }

    df_carts = pd.concat([df_carts, pd.DataFrame([new_item])], ignore_index=True)

    return {
        "success": True,
        "message": f"상품 {product_id}가 장바구니에 {quantity}개 추가되었습니다.",
        "cart_item": new_item
    }

# 4. 장바구니에서 상품 제거하는 함수
def remove_from_cart(user_id, keyword=None, product_id=None):
    global df_carts

    if product_id is not None:
        to_remove = df_carts[(df_carts['user_id'] == user_id) & (df_carts['product_id'] == product_id)]
        if to_remove.empty:
            return {
                "success": False,
                "message": f"장바구니에서 상품 ID {product_id}를 찾을 수 없습니다."
            }
        df_carts = df_carts.drop(to_remove.index)
        return {
            "success": True,
            "removed_by": "product_id",
            "product_id": product_id,
            "removed_count": len(to_remove),
            "message": f"장바구니에서 상품 {product_id}를 제거했습니다."
        }

    if keyword is not None:
        user_cart = df_carts[df_carts['user_id'] == user_id].merge(
            df_products[['id', 'name']], left_on='product_id', right_on='id', suffixes=('', '_prod')
        )
        to_remove = user_cart[user_cart['name'].str.contains(keyword, case=False, na=False)]
        if to_remove.empty:
            return {
                "success": False,
                "message": f"장바구니에서 '{keyword}'와 관련된 상품을 찾지 못했습니다."
            }
        df_carts = df_carts[~df_carts['id'].isin(to_remove['id'])]
        return {
            "success": True,
            "removed_by": "keyword",
            "keyword": keyword,
            "removed_count": len(to_remove),
            "message": f"장바구니에서 '{keyword}' 관련 상품 {len(to_remove)}건을 제거했습니다."
        }

    return {
        "success": False,
        "message": "제거할 상품 키워드 또는 product_id를 지정해주세요."
    }

# 5. 주문 내역 전체 보기 함수
def view_order_history(user_id):
    """
    해당 사용자의 전체 주문 내역과 관련 배송 정보, 그리고 주문에 포함된 상품명을 집계하여 반환합니다.
    반환 형식은 JSON(list of dict)입니다.
    """
    orders = df_orders[df_orders["user_id"] == user_id].copy()
    if orders.empty:
        return {"message": f"사용자 {user_id}님의 주문 내역이 없습니다."}

    orders["order_date"] = pd.to_datetime(orders["order_date"])
    orders = orders.sort_values(by="order_date", ascending=False)

    orders = orders.merge(
        df_deliveries[["order_id", "courier", "tracking_number", "status"]],
        left_on="id", right_on="order_id",
        how="left",
        suffixes=('_order', '_delivery')
    )

    order_items_agg = (
        df_order_items
        .merge(df_products[["id", "name"]], left_on="product_id", right_on="id", how="left")
        .groupby("order_id")["name"]
        .apply(lambda x: ", ".join(x.tolist()))
        .reset_index()
        .rename(columns={"name": "products"})
    )

    orders = orders.merge(
        order_items_agg,
        left_on="id", right_on="order_id",
        how="left",
        suffixes=('', '_items')
    )

    orders["order_id"] = orders["id"]

    result_df = orders[
        [
            "order_id",
            "order_date",
            "total",
            "payment_status",
            "delivery_status",
            "courier",
            "tracking_number",
            "status",
            "products"
        ]
    ].copy()

    # 날짜를 문자열로 변환
    result_df["order_date"] = result_df["order_date"].dt.strftime('%Y-%m-%d')

    # JSON 변환
    return result_df.to_dict(orient="records")

# 6. 특정 주문의 상세 내역 보기 함수
def view_order_details(user_id, order_id):
    """
    특정 주문의 상세 내역(주문 상품, 수량, 가격, 할인 가격 등)을 JSON 형식으로 반환합니다.
    """
    order = df_orders[(df_orders["id"] == order_id) & (df_orders["user_id"] == user_id)]
    if order.empty:
        return {"error": f"주문 {order_id}은/는 사용자 {user_id}님의 주문 내역에 없습니다."}

    details = df_order_items[df_order_items["order_id"] == order_id].copy()
    details = details.merge(df_products[["id", "name"]],
                            left_on="product_id", right_on="id", how="left")

    result = details[["order_id", "product_id", "name", "quantity", "price", "discount_price"]]
    return result.to_dict(orient="records")

# 7. 사용자 정보 조회 함수
def view_user_profile(user_id):
    """
    주어진 user_id에 해당하는 사용자의 프로필 정보를 반환합니다.
    - 사용자 기본 정보: 이름, 이메일, 전화번호, 주소, 포인트, 멤버십 등
    - 사용자 쿠폰 정보: 쿠폰 ID, 쿠폰명, 할인 유형/값, 최소 주문 금액, 최대 할인 한도, 유효 기간, 사용 여부, 사용 일자
    """
    # 1) 사용자 기본 정보 조회
    user = df_users[df_users["id"] == user_id].copy()
    if user.empty:
        return f"사용자 {user_id}을(를) 찾을 수 없습니다."
    user_info = user.iloc[0].to_dict()

    # 2) 사용자 쿠폰 정보 조회 및 쿠폰 상세 조인
    user_cp = df_user_coupons[df_user_coupons["user_id"] == user_id].copy()
    if not user_cp.empty:
        user_cp = user_cp.merge(
            df_coupons,
            left_on="coupon_id",
            right_on="id",
            how="left",
            suffixes=("", "_coupon")
        )
        # 필요한 컬럼만 선택
        user_cp = user_cp[[
            "coupon_id", "name", "discount_type", "discount_value",
            "min_order", "max_discount", "start_date", "end_date",
            "used", "use_date"
        ]]
        # 리스트 형태로 변환
        user_info["coupons"] = user_cp.to_dict(orient="records")
    else:
        user_info["coupons"] = []

    return user_info

# 8. 약관 조회 함수
def search_policy_info(keyword):
    """
    특정 키워드(예: '주문 취소', '반품')에 해당하는 상준몰 정책 정보를 검색하여 반환합니다.
    """
    results = df_regulations[df_regulations["keyword"] == keyword]["content"].tolist()
    if not results:
        return {
            "keyword": keyword,
            "search_result": [f"'{keyword}'에 대한 정책 정보를 찾을 수 없습니다."]
        }
    return {
        "keyword": keyword,
        "search_result": results
    }