"""Proposal-derived demo service and membership catalog.

All names and VND prices in this module are estimates from the proposal, not
verified retail quotations.
"""

from typing import TypedDict


class ServicePackage(TypedDict):
    code: str
    category: str
    name: str
    description: str
    species: str
    coat_types: str
    min_weight: float
    max_weight: float | None
    duration_minutes: int
    list_price: int
    member_price: int | None
    included_weight_kg: float
    surcharge_per_kg: int
    coat_surcharge: int
    is_demo: bool


class MembershipPackage(TypedDict):
    code: str
    name: str
    description: str
    price: int
    duration_days: int
    billing_mode: str
    included_visits: int
    discount_percent: int
    max_pets: int
    service_category: str


def _build_services(
    category: str, code_prefix: str, offerings: str
) -> tuple[ServicePackage, ...]:
    packages: list[ServicePackage] = []
    for index, row in enumerate(offerings.strip().splitlines(), start=1):
        name, description, price = row.split("|")
        packages.append(
            {
                "code": f"{code_prefix}-{index:03d}",
                "category": category,
                "name": name,
                "description": description,
                "species": "Chó,Mèo",
                "coat_types": "ANY",
                "min_weight": 0.0,
                "max_weight": None,
                "duration_minutes": 60,
                "list_price": int(price),
                "member_price": None,
                "included_weight_kg": 0.0,
                "surcharge_per_kg": 0,
                "coat_surcharge": 0,
                "is_demo": True,
            }
        )
    return tuple(packages)


BATH_SERVICES: tuple[ServicePackage, ...] = _build_services(
    "BATH",
    "SVC-BATH",
    """
Tắm Basic XS|Tắm + sấy|49000
Tắm Basic S|Tắm + sấy|59000
Tắm Basic M|Tắm + sấy|69000
Tắm Basic L|Tắm + sấy|89000
Tắm Basic XL|Tắm + sấy|109000
Puppy Bath|Tắm puppy + sấy|79000
Kitten Bath|Tắm kitten + sấy|79000
Gentle Bath|Tắm dịu nhẹ|89000
Sensitive Bath|Tắm da nhạy cảm|99000
Oatmeal Bath|Tắm dưỡng da|109000
Aloe Bath|Tắm dưỡng ẩm|109000
Whitening Bath|Tắm trắng lông|119000
Deodorizing Bath|Tắm khử mùi|109000
Anti-Odor Premium|Tắm khử mùi cao cấp|139000
Coat Care Bath|Tắm dưỡng lông|119000
Long Hair Bath|Tắm lông dài|129000
Short Hair Bath|Tắm lông ngắn|99000
Double Coat Bath|Tắm lông 2 lớp|149000
Curly Coat Bath|Tắm lông xoăn|139000
Thick Coat Bath|Tắm lông dày|149000
Anti-Itch Bath|Tắm hỗ trợ da nhạy cảm|139000
Moisture Bath|Tắm dưỡng ẩm|129000
Silk Coat Bath|Tắm mượt lông|139000
Fresh Bath|Tắm + khử mùi|119000
Perfume Bath|Tắm + nước hoa|129000
Relax Bath|Tắm thư giãn|149000
Spa Bath Basic|Tắm + dưỡng|159000
Spa Bath Plus|Tắm + xả + dưỡng|179000
Premium Bath|Tắm cao cấp|189000
Premium Coat|Tắm + dưỡng lông chuyên sâu|219000
Luxury Bath|Tắm + dưỡng + nước hoa|249000
Royal Bath|Tắm cao cấp toàn diện|279000
Puppy Premium|Puppy + dưỡng|149000
Kitten Premium|Kitten + dưỡng|149000
Senior Bath|Tắm nhẹ cho thú lớn tuổi|149000
Active Dog Bath|Tắm cho chó vận động nhiều|139000
Indoor Pet Bath|Tắm thú nuôi trong nhà|119000
Outdoor Pet Bath|Tắm + khử mùi|149000
Deep Clean Bath|Tắm làm sạch chuyên sâu|179000
Ultimate Bath|Tắm + dưỡng + khử mùi|249000
""",
)

BATH_HYGIENE_SERVICES: tuple[ServicePackage, ...] = _build_services(
    "BATH_HYGIENE",
    "SVC-BATH-HYG",
    """
Bath + Ear|Tắm + vệ sinh tai|89000
Bath + Eye|Tắm + vệ sinh mắt|89000
Bath + Teeth|Tắm + vệ sinh răng|99000
Bath + Nail|Tắm + cắt móng|99000
Bath + Paw|Tắm + vệ sinh chân|99000
Bath + Face|Tắm + vệ sinh mặt|99000
Bath + Ear + Nail|Tai + móng|119000
Bath + Eye + Ear|Mắt + tai|119000
Bath + Teeth + Nail|Răng + móng|129000
Bath + Face + Paw|Mặt + chân|119000
Bath + Ear + Eye|Tai + mắt|119000
Bath + Ear + Teeth|Tai + răng|129000
Bath + Ear + Paw|Tai + chân|119000
Bath + Eye + Nail|Mắt + móng|119000
Bath + Eye + Paw|Mắt + chân|119000
Bath + Teeth + Ear|Răng + tai|129000
Bath + Teeth + Paw|Răng + chân|129000
Bath + Nail + Paw|Móng + chân|119000
Bath + Face + Ear|Mặt + tai|119000
Bath + Face + Eye|Mặt + mắt|119000
Bath Hygiene Basic|Tai + mắt + móng|139000
Bath Hygiene Plus|Tai + mắt + chân|139000
Bath Dental Care|Răng + tai + móng|149000
Bath Face Care|Mặt + mắt + tai|149000
Bath Paw Care|Chân + móng + dưỡng|149000
Bath Oral Care|Răng + miệng + tai|159000
Bath Full Hygiene|Tai + mắt + răng + móng|169000
Bath Full Clean|Tai + mắt + chân + móng|169000
Bath 5 Care|Tai + mắt + răng + móng + chân|189000
Bath 6 Care|Full vệ sinh + mặt|209000
Bath Puppy Hygiene|Tắm + vệ sinh puppy|139000
Bath Kitten Hygiene|Tắm + vệ sinh kitten|139000
Bath Senior Hygiene|Tắm + vệ sinh nhẹ|169000
Bath Sensitive Hygiene|Tắm + vệ sinh dịu nhẹ|169000
Bath Long Hair Hygiene|Tắm + vệ sinh lông dài|189000
Bath Premium Hygiene|Tắm + full vệ sinh|229000
Bath Deluxe Hygiene|Tắm + vệ sinh chuyên sâu|259000
Bath Spa Hygiene|Tắm + spa + vệ sinh|299000
Bath VIP Hygiene|Tắm + full hygiene|349000
Ultimate Hygiene|Tắm + vệ sinh toàn diện|399000
""",
)

GROOMING_SERVICES: tuple[ServicePackage, ...] = _build_services(
    "GROOMING",
    "SVC-GROOM",
    """
Brush Basic|Chải lông|39000
Brush Plus|Chải + gỡ rối nhẹ|59000
Brush Premium|Chải + dưỡng|89000
Nail Basic|Cắt móng|39000
Nail Premium|Cắt + mài móng|59000
Ear Grooming|Vệ sinh tai|49000
Face Grooming|Vệ sinh mặt|59000
Paw Grooming|Vệ sinh chân|59000
Teeth Grooming|Vệ sinh răng|59000
Basic Grooming|Chải + móng|79000
Grooming S|Chải + móng + tai|99000
Grooming M|Chải + tai + móng|119000
Grooming L|Chải + tai + mắt + móng|139000
Grooming XL|Full grooming cơ bản|169000
Face Trim|Tỉa mặt|99000
Paw Trim|Tỉa chân|99000
Sanitary Trim|Tỉa vệ sinh|109000
Ear Trim|Tỉa lông tai|89000
Body Trim|Tỉa thân|149000
Full Trim|Tỉa toàn thân|199000
Bath Grooming|Tắm + grooming|149000
Grooming Plus|Tắm + chải + móng|169000
Grooming Care|Tắm + grooming + tai|189000
Grooming Dental|Grooming + răng|199000
Grooming Paw|Grooming + chân|199000
Grooming Face|Grooming + mặt|199000
Long Hair Grooming|Grooming lông dài|229000
Short Hair Grooming|Grooming lông ngắn|169000
Double Coat Grooming|Grooming lông 2 lớp|249000
Curly Grooming|Grooming lông xoăn|239000
Puppy Grooming|Grooming puppy|149000
Kitten Grooming|Grooming kitten|149000
Senior Grooming|Grooming thú lớn tuổi|189000
Sensitive Grooming|Grooming nhẹ nhàng|199000
De-shedding|Loại lông rụng chuyên sâu|199000
De-matting|Gỡ rối chuyên sâu|249000
Premium Grooming|Grooming cao cấp|299000
Luxury Grooming|Grooming + dưỡng|349000
VIP Grooming|Full grooming|399000
Ultimate Grooming|Full grooming chuyên sâu|499000
""",
)

HYGIENE_SERVICES: tuple[ServicePackage, ...] = _build_services(
    "HYGIENE",
    "SVC-HYGIENE",
    """
Ear Clean|Vệ sinh tai|39000
Eye Clean|Vệ sinh mắt|39000
Dental Clean|Vệ sinh răng|49000
Nail Cut|Cắt móng|39000
Nail Grind|Cắt + mài|59000
Paw Clean|Vệ sinh chân|39000
Face Clean|Vệ sinh mặt|49000
Ear + Eye|Tai + mắt|59000
Ear + Nail|Tai + móng|59000
Eye + Nail|Mắt + móng|59000
Ear + Dental|Tai + răng|69000
Ear + Paw|Tai + chân|59000
Eye + Paw|Mắt + chân|59000
Dental + Nail|Răng + móng|69000
Dental + Paw|Răng + chân|69000
Face + Ear|Mặt + tai|69000
Face + Eye|Mặt + mắt|69000
Face + Paw|Mặt + chân|69000
Ear Basic|Tai + làm sạch|59000
Dental Basic|Răng + miệng|69000
Hygiene Basic|Tai + mắt + móng|89000
Hygiene Plus|Tai + mắt + chân|89000
Dental Plus|Răng + tai + móng|99000
Face Plus|Mặt + mắt + tai|99000
Paw Plus|Chân + móng + dưỡng|99000
Clean 4|Tai + mắt + răng + móng|119000
Clean 5|Tai + mắt + răng + móng + chân|139000
Clean 6|Full vệ sinh + mặt|159000
Puppy Hygiene|Vệ sinh puppy|89000
Kitten Hygiene|Vệ sinh kitten|89000
Senior Hygiene|Vệ sinh senior|109000
Sensitive Hygiene|Vệ sinh nhạy cảm|109000
Long Hair Hygiene|Vệ sinh lông dài|129000
Deep Hygiene|Vệ sinh chuyên sâu|159000
Dental Premium|Chăm sóc răng nâng cao|129000
Ear Premium|Chăm sóc tai nâng cao|119000
Paw Premium|Chăm sóc chân nâng cao|119000
Full Hygiene Premium|Full vệ sinh|189000
VIP Hygiene|Vệ sinh VIP|249000
Ultimate Hygiene|Vệ sinh toàn diện|299000
""",
)

PET_CARE_SERVICES: tuple[ServicePackage, ...] = _build_services(
    "PET_CARE",
    "SVC-PETCARE",
    """
Puppy Care Basic|Tắm + sấy|79000
Puppy Care Plus|Tắm + tai + móng|119000
Puppy Full Care|Tắm + vệ sinh + grooming|159000
Kitten Care Basic|Tắm + sấy|79000
Kitten Care Plus|Tắm + tai + móng|119000
Kitten Full Care|Tắm + vệ sinh + grooming|159000
Adult Dog Care|Tắm + chải|129000
Adult Cat Care|Tắm + chải|129000
Senior Dog Care|Chăm sóc nhẹ|159000
Senior Cat Care|Chăm sóc nhẹ|159000
Sensitive Care|Tắm dịu nhẹ + dưỡng|149000
Skin Care|Tắm + dưỡng da|169000
Coat Care|Tắm + dưỡng lông|169000
Long Hair Care|Tắm + chải + dưỡng|199000
Short Hair Care|Tắm + chải|139000
Double Coat Care|Tắm + chải chuyên sâu|219000
Curly Coat Care|Tắm + grooming|219000
De-shedding Care|Tắm + giảm lông rụng|219000
De-matting Care|Tắm + gỡ rối|259000
Dental Care|Tắm + chăm sóc răng|179000
Ear Care|Tắm + chăm sóc tai|159000
Paw Care|Tắm + chăm sóc chân|159000
Face Care|Tắm + chăm sóc mặt|169000
Full Care Basic|Tắm + vệ sinh|179000
Full Care Plus|Tắm + grooming + vệ sinh|229000
Full Care Premium|Full chăm sóc|279000
Wellness Care|Tắm + dưỡng + thư giãn|249000
Relax Care|Tắm + massage|269000
Spa Care|Tắm + dưỡng + massage|329000
Pet Spa Plus|Spa + grooming|399000
Pet Beauty|Tắm + grooming + dưỡng|349000
Pet Fresh|Tắm + khử mùi + vệ sinh|229000
Pet Clean|Tắm + full vệ sinh|249000
Pet Health Care|Tắm + vệ sinh + chăm sóc cơ bản|299000
Pet Comfort|Chăm sóc + thư giãn|299000
Pet Luxury|Chăm sóc cao cấp|399000
Pet Royal|Full dịch vụ|499000
Pet VIP|Full care VIP|599000
Pet Diamond|Full care + spa|699000
Ultimate Pet Care|Chăm sóc toàn diện|799000
""",
)

PREMIUM_SERVICES: tuple[ServicePackage, ...] = _build_services(
    "PREMIUM",
    "SVC-PREMIUM",
    """
Premium Bath|Tắm cao cấp|179000
Premium Clean|Vệ sinh cao cấp|179000
Premium Groom|Grooming cao cấp|249000
Premium Care|Full chăm sóc|299000
Premium Coat|Dưỡng lông|249000
Premium Skin|Dưỡng da|249000
Premium Dental|Chăm sóc răng|199000
Premium Paw|Chăm sóc chân|199000
Premium Ear|Chăm sóc tai|199000
Premium Face|Chăm sóc mặt|199000
Spa Basic|Tắm + dưỡng|249000
Spa Plus|Tắm + grooming|299000
Spa Care|Tắm + dưỡng + vệ sinh|329000
Spa Relax|Tắm + massage|329000
Spa Coat|Dưỡng lông chuyên sâu|349000
Spa Skin|Dưỡng da chuyên sâu|349000
Spa Beauty|Grooming + dưỡng|399000
Spa Deluxe|Full spa|449000
Spa Luxury|Full spa cao cấp|499000
Spa Royal|Spa toàn diện|599000
VIP Bath|Tắm VIP|299000
VIP Groom|Grooming VIP|399000
VIP Hygiene|Vệ sinh VIP|299000
VIP Care|Full care VIP|499000
VIP Spa|Full spa VIP|599000
VIP Beauty|Làm đẹp VIP|549000
VIP Relax|Thư giãn VIP|499000
VIP Coat|Dưỡng lông VIP|449000
VIP Skin|Chăm sóc da VIP|449000
VIP Dental|Chăm sóc răng VIP|299000
Royal Care|Chăm sóc toàn diện|599000
Royal Spa|Spa toàn diện|699000
Royal Groom|Grooming toàn diện|599000
Royal Beauty|Làm đẹp toàn diện|699000
Diamond Care|Full service|799000
Diamond Spa|Spa + grooming|899000
Diamond Beauty|Làm đẹp + dưỡng|899000
Diamond VIP|Full dịch vụ|999000
Elite Pet Care|Full care cao cấp|1199000
Ultimate Pet Spa|Full spa + grooming + care|1499000
""",
)

SERVICE_PACKAGES: tuple[ServicePackage, ...] = (
    BATH_SERVICES
    + BATH_HYGIENE_SERVICES
    + GROOMING_SERVICES
    + HYGIENE_SERVICES
    + PET_CARE_SERVICES
    + PREMIUM_SERVICES
)


def _membership(
    index: int,
    name: str,
    description: str,
    price: int,
    duration_days: int,
    billing_mode: str,
    included_visits: int,
    discount_percent: int,
    max_pets: int,
    service_category: str,
) -> MembershipPackage:
    return {
        "code": f"SVC-MEM-{index:03d}",
        "name": name,
        "description": description,
        "price": price,
        "duration_days": duration_days,
        "billing_mode": billing_mode,
        "included_visits": included_visits,
        "discount_percent": discount_percent,
        "max_pets": max_pets,
        "service_category": service_category,
    }


MEMBERSHIP_PACKAGES: tuple[MembershipPackage, ...] = (
    _membership(1, "Monthly Basic", "2 lần tắm", 149000, 30, "PREPAID_VISITS", 2, 0, 1, "BATH"),
    _membership(2, "Monthly Clean", "2 lần tắm + vệ sinh", 199000, 30, "PREPAID_VISITS", 2, 0, 1, "BATH_HYGIENE"),
    _membership(3, "Monthly Groom", "2 lần grooming", 249000, 30, "PREPAID_VISITS", 2, 0, 1, "GROOMING"),
    _membership(4, "Monthly Care", "2 lần full care", 299000, 30, "PREPAID_VISITS", 2, 0, 1, "PET_CARE"),
    _membership(5, "Monthly Premium", "4 lần tắm", 349000, 30, "PREPAID_VISITS", 4, 0, 1, "BATH"),
    _membership(6, "Monthly Groom Plus", "4 lần grooming", 449000, 30, "PREPAID_VISITS", 4, 0, 1, "GROOMING"),
    _membership(7, "Monthly Care Plus", "4 lần care", 499000, 30, "PREPAID_VISITS", 4, 0, 1, "PET_CARE"),
    _membership(8, "Monthly Spa", "4 lần spa", 599000, 30, "PREPAID_VISITS", 4, 0, 1, "PREMIUM"),
    _membership(9, "Puppy Monthly", "4 lần puppy care", 399000, 30, "PREPAID_VISITS", 4, 0, 1, "PET_CARE"),
    _membership(10, "Kitten Monthly", "4 lần kitten care", 399000, 30, "PREPAID_VISITS", 4, 0, 1, "PET_CARE"),
    _membership(11, "Dog Basic 3M", "6 lần/3 tháng", 449000, 90, "PREPAID_VISITS", 6, 0, 1, "BATH"),
    _membership(12, "Cat Basic 3M", "6 lần/3 tháng", 449000, 90, "PREPAID_VISITS", 6, 0, 1, "BATH"),
    _membership(13, "Dog Care 3M", "6 lần care", 699000, 90, "PREPAID_VISITS", 6, 0, 1, "PET_CARE"),
    _membership(14, "Cat Care 3M", "6 lần care", 699000, 90, "PREPAID_VISITS", 6, 0, 1, "PET_CARE"),
    _membership(15, "Premium 3M", "12 lần dịch vụ", 999000, 90, "PREPAID_VISITS", 12, 0, 1, "PREMIUM"),
    _membership(16, "Spa 3M", "12 lần spa", 1299000, 90, "PREPAID_VISITS", 12, 0, 1, "PREMIUM"),
    _membership(17, "Dog Premium 3M", "Care + grooming", 1199000, 90, "MEMBER_DISCOUNT", 0, 10, 1, ""),
    _membership(18, "Cat Premium 3M", "Care + grooming", 1199000, 90, "MEMBER_DISCOUNT", 0, 10, 1, ""),
    _membership(19, "Family Pet", "2 thú cưng", 799000, 30, "RECURRING", 0, 0, 2, ""),
    _membership(20, "Family Premium", "2 thú cưng premium", 1199000, 30, "RECURRING", 0, 0, 2, ""),
    _membership(21, "Duo Pet", "2 thú cưng/tháng", 499000, 30, "RECURRING", 0, 0, 2, ""),
    _membership(22, "Trio Pet", "3 thú cưng/tháng", 699000, 30, "RECURRING", 0, 0, 3, ""),
    _membership(23, "Multi Pet", "4 thú cưng/tháng", 899000, 30, "RECURRING", 0, 0, 4, ""),
    _membership(24, "VIP Monthly", "Full care", 799000, 30, "RECURRING", 0, 0, 1, ""),
    _membership(25, "VIP 3M", "Full care 3 tháng", 1999000, 90, "RECURRING", 0, 0, 1, ""),
    _membership(26, "VIP 6M", "Full care 6 tháng", 3499000, 180, "RECURRING", 0, 0, 1, ""),
    _membership(27, "VIP Annual", "Full care năm", 5999000, 365, "RECURRING", 0, 0, 1, ""),
    _membership(28, "Diamond Monthly", "Full spa", 999000, 30, "RECURRING", 0, 0, 1, ""),
    _membership(29, "Diamond 3M", "Full spa 3 tháng", 2499000, 90, "RECURRING", 0, 0, 1, ""),
    _membership(30, "Diamond 6M", "Full spa 6 tháng", 4499000, 180, "RECURRING", 0, 0, 1, ""),
    _membership(31, "Diamond Annual", "Full spa năm", 7999000, 365, "RECURRING", 0, 0, 1, ""),
    _membership(32, "Grooming Monthly", "Grooming định kỳ", 499000, 30, "RECURRING", 0, 0, 1, ""),
    _membership(33, "Grooming 3M", "Grooming 3 tháng", 1299000, 90, "RECURRING", 0, 0, 1, ""),
    _membership(34, "Grooming 6M", "Grooming 6 tháng", 2299000, 180, "RECURRING", 0, 0, 1, ""),
    _membership(35, "Spa Monthly", "Spa định kỳ", 699000, 30, "RECURRING", 0, 0, 1, ""),
    _membership(36, "Spa 3M", "Spa 3 tháng", 1799000, 90, "RECURRING", 0, 0, 1, ""),
    _membership(37, "Spa 6M", "Spa 6 tháng", 3199000, 180, "RECURRING", 0, 0, 1, ""),
    _membership(38, "Senior Care", "Chăm sóc thú lớn tuổi", 599000, 30, "RECURRING", 0, 0, 1, "PET_CARE"),
    _membership(39, "Sensitive Care", "Chăm sóc da nhạy cảm", 599000, 30, "RECURRING", 0, 0, 1, "PET_CARE"),
    _membership(40, "Ultimate Membership", "Toàn bộ quyền lợi", 9999000, 365, "RECURRING", 0, 0, 1, ""),
)
