from __future__ import annotations

from typing import Any


# Suggested sample prices from the project brief; not verified retail quotations.
PRODUCT_GROUPS: tuple[dict[str, Any], ...] = (
    {
        "code": "DOG-FOOD",
        "name": "Thức ăn cho chó",
        "stock_category": "FOOD",
        "species": "Chó",
        "products": """
Hạt chó Puppy Basic|1 kg|85000
Hạt chó Adult Basic|1 kg|89000
Hạt chó Adult Chicken|1.5 kg|125000
Hạt chó Puppy Chicken|1.5 kg|139000
Hạt chó Small Breed|1.5 kg|149000
Hạt chó Medium Breed|2 kg|169000
Hạt chó Large Breed|2 kg|179000
Hạt chó Sensitive|1.5 kg|185000
Hạt chó Skin & Coat|1.5 kg|195000
Hạt chó Weight Control|1.5 kg|199000
Hạt chó Premium Adult|3 kg|299000
Hạt chó Premium Puppy|3 kg|319000
Hạt chó Performance|3 kg|339000
Hạt chó Senior|3 kg|329000
Hạt chó Large Adult|5 kg|499000
""",
    },
    {
        "code": "CAT-FOOD",
        "name": "Thức ăn cho mèo",
        "stock_category": "FOOD",
        "species": "Mèo",
        "products": """
Hạt mèo Basic|350 g|29000
Hạt mèo Adult|1.2 kg|119000
Hạt mèo Kitten|1.2 kg|125000
Hạt mèo Indoor|1.2 kg|135000
Hạt mèo Hairball|1.2 kg|145000
Hạt mèo Sensitive|1.2 kg|149000
Hạt mèo Sterilised|1.2 kg|159000
Hạt mèo Urinary Care|1.2 kg|169000
Hạt mèo Skin & Coat|1.2 kg|179000
Hạt mèo Premium|2 kg|229000
Hạt mèo Kitten Premium|2 kg|239000
Hạt mèo Sterilised Premium|2 kg|249000
Hạt mèo Indoor Premium|2 kg|239000
Hạt mèo Grain Free|1.5 kg|269000
Hạt mèo Natural Premium|2 kg|299000
""",
    },
    {
        "code": "WET-FOOD",
        "name": "Pate & thức ăn ướt",
        "stock_category": "FOOD",
        "species": "Chó, Mèo",
        "products": """
Pate gà cho mèo|80 g|12000
Pate cá ngừ|80 g|13000
Pate cá hồi|80 g|15000
Pate gà & cá|80 g|14000
Pate kitten|80 g|16000
Pate senior|80 g|17000
Pate urinary|80 g|19000
Pate premium|85 g|22000
Pate chó vị bò|400 g|39000
Pate chó vị gà|400 g|39000
Pate chó puppy|400 g|45000
Pate cá ngừ 12 lon|12 x 80 g|159000
""",
    },
    {
        "code": "TREATS",
        "name": "Snack & bánh thưởng",
        "stock_category": "FOOD",
        "species": "Chó, Mèo",
        "products": """
Bánh thưởng mềm cho chó|100 g|29000
Snack vị gà|100 g|32000
Snack vị bò|100 g|35000
Snack cá cho mèo|50 g|29000
Cá sấy khô|50 g|39000
Thịt gà sấy|100 g|49000
Thịt bò sấy|100 g|59000
Que thưởng cho chó|10 que|45000
Bánh thưởng training|200 g|59000
Creamy treat cho mèo|5 x 15 g|39000
Catnip snack|50 g|45000
Dental stick|7 que|49000
""",
    },
    {
        "code": "BATH",
        "name": "Sữa tắm & chăm sóc",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Sữa tắm Puppy|250 ml|59000
Sữa tắm Sensitive|250 ml|69000
Sữa tắm dưỡng lông|500 ml|99000
Sữa tắm trị mùi|500 ml|109000
Sữa tắm da nhạy cảm|500 ml|119000
Sữa tắm trắng lông|500 ml|129000
Dầu xả thú cưng|300 ml|89000
Xịt dưỡng lông|250 ml|79000
Xịt khử mùi|250 ml|69000
Nước hoa thú cưng|50 ml|99000
""",
    },
    {
        "code": "HYGIENE",
        "name": "Vệ sinh thú cưng",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Túi nhặt phân|8 cuộn|29000
Túi nhặt phân phân hủy|8 cuộn|39000
Khăn lau chân|1 gói|35000
Khăn ướt thú cưng|80 tờ|39000
Nước lau sàn pet|1 L|69000
Xịt khử mùi chuồng|500 ml|79000
Xịt vệ sinh đồ dùng|500 ml|75000
Dung dịch vệ sinh tai|100 ml|59000
Dung dịch vệ sinh mắt|100 ml|59000
Nước vệ sinh răng miệng|250 ml|89000
""",
    },
    {
        "code": "CAT-LITTER",
        "name": "Cát vệ sinh mèo",
        "stock_category": "SUPPLIES",
        "species": "Mèo",
        "products": """
Cát bentonite Basic|5 L|49000
Cát bentonite Premium|8 L|79000
Cát than hoạt tính|8 L|89000
Cát khử mùi|8 L|99000
Cát đậu nành|6 L|109000
Cát tofu|6 L|119000
Cát tofu than hoạt tính|6 L|129000
Cát gỗ|10 L|119000
Cát giấy|10 L|139000
Cát premium ít bụi|10 L|159000
""",
    },
    {
        "code": "TOYS",
        "name": "Đồ chơi",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Bóng cao su|Cái|25000
Bóng phát âm thanh|Cái|35000
Dây kéo co|Cái|39000
Xương cao su|Cái|45000
Đồ chơi gặm|Cái|49000
Bóng nhồi thức ăn|Cái|59000
Frisbee cho chó|Cái|69000
Chuột bông cho mèo|Cái|25000
Cần câu mèo|Cái|29000
Bóng catnip|Cái|35000
Đường hầm mèo|Cái|99000
Đồ chơi tương tác|Cái|129000
Đồ chơi puzzle|Cái|159000
""",
    },
    {
        "code": "LEASH",
        "name": "Dây dắt & vòng cổ",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Vòng cổ Basic|Cái|39000
Vòng cổ phản quang|Cái|59000
Vòng cổ chuông mèo|Cái|39000
Dây dắt Basic|Cái|59000
Dây dắt phản quang|Cái|79000
Dây dắt chống rối|Cái|99000
Dây dắt Premium|Cái|149000
Bộ dây + vòng cổ|Bộ|129000
Harness Basic|Cái|99000
Harness Premium|Cái|179000
Dây dắt đôi|Cái|159000
""",
    },
    {
        "code": "BOWLS",
        "name": "Bát & dụng cụ ăn uống",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Bát nhựa Basic|Cái|25000
Bát inox nhỏ|Cái|39000
Bát inox lớn|Cái|59000
Bát chống trượt|Cái|69000
Bát chống ăn nhanh|Cái|79000
Bát đôi|Cái|89000
Bình nước di động|Cái|69000
Bình nước treo chuồng|Cái|59000
Máy cho ăn tự động|Cái|499000
Máy uống nước tự động|Cái|399000
""",
    },
    {
        "code": "BEDS",
        "name": "Ổ nằm & nhà thú cưng",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Thảm nằm Basic|Cái|69000
Đệm tròn nhỏ|Cái|99000
Đệm vuông|Cái|129000
Ổ cotton mềm|Cái|159000
Ổ mùa đông|Cái|179000
Đệm memory foam|Cái|299000
Nhà vải cho mèo|Cái|149000
Nhà carton mèo|Cái|79000
Nhà gỗ nhỏ|Cái|299000
Sofa thú cưng|Cái|399000
""",
    },
    {
        "code": "CARRIERS",
        "name": "Balo & túi vận chuyển",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Túi vận chuyển Basic|Cái|129000
Túi lưới thoáng khí|Cái|159000
Balo mèo Basic|Cái|199000
Balo kính trong|Cái|249000
Balo chống nước|Cái|279000
Balo Premium|Cái|349000
Túi vận chuyển máy bay|Cái|399000
Lồng vận chuyển nhựa|Cái|299000
Lồng vận chuyển lớn|Cái|499000
""",
    },
    {
        "code": "CLOTHES",
        "name": "Quần áo thú cưng",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Áo thun Basic|Cái|59000
Áo mùa hè|Cái|69000
Áo hoodie|Cái|99000
Áo len|Cái|109000
Áo khoác|Cái|129000
Áo mưa|Cái|89000
Váy thú cưng|Cái|99000
Bộ cosplay|Bộ|149000
Áo phản quang|Cái|119000
Bộ quần áo Premium|Bộ|199000
""",
    },
    {
        "code": "GROOMING",
        "name": "Grooming & chăm sóc lông",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Lược chải lông Basic|Cái|39000
Lược gỡ rối|Cái|59000
Lược massage|Cái|49000
Bàn chải hai mặt|Cái|79000
Kéo cắt lông|Cái|99000
Kềm cắt móng|Cái|59000
Máy mài móng|Cái|199000
Máy sấy thú cưng|Cái|399000
Bộ grooming 5 món|Bộ|199000
Bộ grooming Premium|Bộ|349000
""",
    },
    {
        "code": "SUPPLEMENTS",
        "name": "Vitamin & dinh dưỡng",
        "stock_category": "SUPPLIES",
        "species": "Chó, Mèo",
        "products": """
Vitamin tổng hợp|Hộp|99000
Omega 3|Hộp|119000
Dầu cá|Chai|129000
Canxi|Hộp|109000
Men tiêu hóa|Hộp|89000
Probiotic|Hộp|129000
Vitamin lông da|Hộp|139000
Gel dinh dưỡng|Tuýp|99000
Gel bổ sung năng lượng|Tuýp|109000
Sữa bổ sung cho puppy|Hộp|159000
Sữa bổ sung cho kitten|Hộp|159000
""",
    },
    {
        "code": "SMALL-PETS",
        "name": "Hamster & thỏ",
        "stock_category": "FOOD",
        "species": "Hamster, Thỏ",
        "products": """
Thức ăn hamster|Gói|59000
Hạt mix hamster|Gói|69000
Snack hamster|Gói|39000
Cát tắm hamster|Gói|49000
Nhà hamster|Cái|79000
Bánh xe hamster|Cái|89000
Bình nước hamster|Cái|39000
Thức ăn thỏ|Gói|79000
Cỏ khô Timothy|Gói|99000
Đồ chơi thỏ|Cái|59000
""",
    },
    {
        "code": "AQUARIUM",
        "name": "Cá cảnh",
        "stock_category": "SUPPLIES",
        "species": "Cá",
        "products": """
Thức ăn cá hạt nhỏ|Gói|29000
Thức ăn cá nhiệt đới|Gói|39000
Thức ăn cá Betta|Gói|35000
Thức ăn cá vàng|Gói|39000
Thức ăn cá Koi|Gói|79000
Vi sinh hồ cá|Chai|69000
Dung dịch xử lý nước|Chai|59000
Muối hồ cá|Gói|39000
Máy sủi oxy|Cái|99000
Máy lọc mini|Cái|149000
Đèn LED hồ cá|Cái|129000
""",
    },
    {
        "code": "BIRDS",
        "name": "Chim cảnh",
        "stock_category": "FOOD",
        "species": "Chim",
        "products": """
Thức ăn hạt cho vẹt|Gói|59000
Thức ăn yến phụng|Gói|39000
Thức ăn chim chào mào|Gói|49000
Thức ăn chim họa mi|Gói|49000
Thức ăn chim finch|Gói|45000
Thức ăn chim cảnh tổng hợp|Gói|39000
Kê vàng cho chim|Gói|29000
Kê đỏ cho chim|Gói|29000
Hạt hướng dương cho vẹt|Gói|39000
Thức ăn mềm cho chim|Gói|35000
Đồ chơi treo lồng chim|Cái|39000
Cầu đậu cho chim|Cái|29000
Bình nước gắn lồng|Cái|25000
Máng ăn gắn lồng|Cái|25000
Lồng chim cỡ nhỏ|Cái|199000
""",
    },
    {
        "code": "RODENTS",
        "name": "Chuột cảnh",
        "stock_category": "FOOD",
        "species": "Chuột cảnh",
        "products": """
Thức ăn chuột hamster|Gói|59000
Thức ăn chuột lang|Gói|79000
Thức ăn chuột fancy rat|Gói|69000
Hạt mix chuột cảnh|Gói|69000
Snack rau củ sấy cho chuột|Gói|39000
Cỏ khô cho chuột lang|Gói|89000
Viên nén thức ăn chuột lang|Gói|79000
Đồ chơi gặm gỗ cho chuột|Cái|29000
Bánh xe hamster cỡ nhỏ|Cái|69000
Bình nước bi lăn|Cái|39000
Nhà ngủ chuột cảnh|Cái|59000
Hang trú chuột cảnh|Cái|49000
Lót chuồng giấy|Gói|59000
Lót chuồng gỗ nén|Gói|69000
Lồng chuột cảnh cơ bản|Cái|249000
""",
    },
    {
        "code": "REPTILES",
        "name": "Bò sát cảnh",
        "stock_category": "SUPPLIES",
        "species": "Bò sát",
        "products": """
Thức ăn viên cho rùa cảnh|Gói|49000
Thức ăn khô cho rùa nước|Gói|59000
Thức ăn cho rùa cạn|Gói|69000
Đá phơi nắng cho rùa|Cái|79000
Đèn LED chuồng bò sát|Cái|129000
Đèn sưởi chuồng bò sát|Cái|99000
Nhiệt kế chuồng bò sát|Cái|59000
Ẩm kế chuồng bò sát|Cái|59000
Hang trú bò sát|Cái|89000
Khay nước bò sát|Cái|49000
Tấm lót chuồng bò sát|Tấm|39000
Giá thể xơ dừa bò sát|Gói|59000
Kẹp gắp thức ăn bò sát|Cái|39000
Bình phun sương chuồng|Cái|59000
Bể nuôi bò sát mini|Cái|299000
""",
    },
)

ADDITIONAL_PRODUCTS: dict[str, str] = {
    "DOG-FOOD": """
Hạt chó Puppy Premium|2 kg|219000
Hạt chó Adult Premium|2 kg|229000
Hạt chó Senior|2 kg|239000
Hạt chó Digestive Care|1.5 kg|209000
Hạt chó Joint Care|1.5 kg|219000
Hạt chó Puppy Premium Plus|3 kg|319000
Hạt chó Adult Premium Plus|3 kg|329000
Hạt chó Small Breed Premium|3 kg|349000
Hạt chó Medium Breed Premium|3 kg|359000
Hạt chó Puppy Large Breed|5 kg|519000
Hạt chó Grain Free|2 kg|279000
Hạt chó Salmon|2 kg|289000
Hạt chó Lamb|2 kg|279000
Hạt chó Beef|2 kg|269000
Hạt chó Chicken & Rice|3 kg|319000
Hạt chó Natural|3 kg|349000
Hạt chó Holistic|3 kg|399000
Hạt chó Ultra Premium|5 kg|599000
Hạt chó Duck & Rice|2 kg|289000
Hạt chó Puppy Small Breed|1.5 kg|159000
""",
    "CAT-FOOD": """
Hạt mèo Digestive Care|1.2 kg|179000
Hạt mèo Hairball Premium|2 kg|259000
Hạt mèo Urinary Premium|2 kg|269000
Hạt mèo Salmon|1.5 kg|279000
Hạt mèo Chicken|2 kg|249000
Hạt mèo Tuna|1.5 kg|259000
Hạt mèo Holistic|2 kg|329000
Hạt mèo Senior|2 kg|259000
Hạt mèo Weight Control|2 kg|269000
Hạt mèo Long Hair|2 kg|279000
Hạt mèo Persian|2 kg|289000
Hạt mèo British Shorthair|2 kg|299000
Hạt mèo Maine Coon|2 kg|319000
Hạt mèo Premium Plus|3 kg|399000
Hạt mèo Ultra Premium|4 kg|499000
""",
    "WET-FOOD": """
Pate bò|80 g|15000
Pate hairball|80 g|19000
Pate sensitive|80 g|20000
Pate premium gà|85 g|22000
Pate premium cá|85 g|23000
Pate salmon|85 g|24000
Pate tuna|85 g|22000
Pate shrimp|85 g|25000
Pate chó adult|400 g|45000
Pate chó senior|400 g|49000
Pate cá ngừ 6 lon|6 x 80 g|85000
Pate mix 12 lon|12 x 80 g|169000
Pate premium 12 lon|12 x 85 g|229000
Soup mèo cá ngừ|4 x 15 g|35000
Soup mèo cá hồi|4 x 15 g|39000
Soup mèo gà|4 x 15 g|35000
Soup mèo premium|4 x 15 g|49000
Wet food kitten|85 g|24000
Wet food adult|85 g|23000
Soup mèo gà & cá|4 x 15 g|39000
Pate chó vị cừu|400 g|49000
""",
    "TREATS": """
Snack cá hồi|100 g|39000
Thịt heo sấy|100 g|49000
Gan sấy|100 g|45000
Tôm sấy|50 g|49000
Dental bone|3 chiếc|39000
Creamy treat cá|5 gói|42000
Creamy treat gà|5 gói|39000
Catnip ball|2 viên|35000
Freeze dried chicken|50 g|69000
Freeze dried salmon|50 g|79000
Freeze dried beef|50 g|75000
Mix snack chó|250 g|89000
Mix snack mèo|200 g|79000
Snack puppy|100 g|39000
Snack kitten|50 g|35000
Snack senior|100 g|45000
Snack training premium|200 g|79000
Snack premium mix|300 g|119000
""",
    "BATH": """
Sữa tắm Kitten|250 ml|59000
Sữa tắm khử mùi|500 ml|109000
Sữa tắm lông dài|500 ml|129000
Sữa tắm lông ngắn|500 ml|109000
Sữa tắm Aloe Vera|500 ml|119000
Sữa tắm Oatmeal|500 ml|139000
Dầu xả thú cưng|300 ml|89000
Xịt dưỡng lông|250 ml|79000
Xịt khử mùi|250 ml|69000
Nước hoa Puppy|50 ml|89000
Dầu gội khô|200 ml|79000
Foam tắm khô|200 ml|89000
Dung dịch vệ sinh tai|100 ml|59000
Dung dịch vệ sinh mắt|100 ml|59000
Gel đánh răng|70 g|69000
Kem dưỡng chân|50 g|79000
Kem dưỡng mũi|30 g|69000
Bộ chăm sóc lông|Combo|199000
""",
    "HYGIENE": """
Túi nhặt phân Premium|8 cuộn|49000
Khăn ướt thú cưng|40 tờ|25000
Khăn lau mặt|1 gói|29000
Xịt khử mùi sofa|500 ml|89000
Gel đánh răng|70 g|69000
Bàn chải răng ngón tay|Bộ|29000
Bàn chải răng 2 đầu|Cái|39000
Găng tay vệ sinh|Đôi|35000
Tấm lót vệ sinh|10 miếng|59000
Tấm lót vệ sinh|30 miếng|129000
Tấm lót vệ sinh|50 miếng|199000
Túi rác pet|Cuộn|39000
Bình xịt vệ sinh|Cái|29000
Bộ vệ sinh chuồng|Bộ|99000
Bộ vệ sinh Premium|Bộ|159000
""",
    "CAT-LITTER": """
Bentonite hương hoa|8 L|99000
Bentonite hương táo|8 L|99000
Tofu Basic|6 L|109000
Tofu Premium|6 L|119000
Tofu đậu nành|6 L|119000
Tofu mix|6 L|129000
Cát ngô|6 L|129000
Cát đậu xanh|6 L|129000
Cát ít bụi|8 L|139000
Cát siêu vón|8 L|149000
Cát khử mùi Premium|10 L|159000
Cát tofu Premium|10 L|179000
Cát đậu nành Premium|10 L|179000
Cát gỗ Premium|10 L|169000
Cát giấy Premium|10 L|189000
Cát Multi-Cat|10 L|199000
Cát Ultra Premium|10 L|229000
Combo cát 2 túi|2 x 8 L|169000
""",
    "TOYS": """
Bóng tennis|Cái|29000
Xương phát âm thanh|Cái|55000
Đĩa bay Premium|Cái|99000
Chuột catnip|Cái|39000
Đồ chơi lông vũ|Cái|35000
Tunnel Premium|Cái|159000
Bóng tương tác|Cái|89000
Đồ chơi IQ|Cái|179000
Tháp bóng mèo|Cái|129000
Cây lăn bóng|Cái|99000
Đồ chơi tự động|Cái|299000
Laser mèo|Cái|59000
Đồ chơi phát sáng|Cái|69000
Đồ chơi cao su Premium|Cái|89000
Bộ 3 đồ chơi mèo|Bộ|79000
Bộ 5 đồ chơi mèo|Bộ|119000
Bộ đồ chơi chó|Bộ|129000
Bộ đồ chơi Premium|Bộ|199000
""",
}

FILLER_PRODUCTS: dict[str, tuple[str, ...]] = {
    "BATH": ("Sữa tắm dịu nhẹ", "Bộ chăm sóc thú cưng cơ bản"),
    "HYGIENE": ("Khăn vệ sinh mini", "Túi nhặt phân tiện dụng", "Tấm lót vệ sinh size nhỏ", "Bộ khăn vệ sinh", "Dung dịch vệ sinh vật dụng"),
    "CAT-LITTER": ("Cát tofu ít bụi", "Cát bentonite tiết kiệm"),
    "LEASH": ("Size XS", "Size S", "Size M", "Size L", "Size XL", "Màu đỏ", "Màu xanh", "Màu đen", "Màu hồng", "Màu be", "Bản rộng", "Bản mềm", "Có đệm", "Chống nước", "Phản quang", "Dành cho chó nhỏ", "Dành cho chó lớn", "Dành cho mèo", "Bộ đôi"),
    "BOWLS": ("Size mini", "Size nhỏ", "Size vừa", "Size lớn", "Inox 2 ngăn", "Gốm mini", "Gốm lớn", "Silicone gấp gọn", "Có nắp", "Đế cao", "Màu xanh", "Màu hồng", "Màu xám", "Chống trượt premium", "Chống ăn nhanh chậm", "Bình du lịch", "Bộ ăn du lịch", "Máng ăn treo", "Máng đôi", "Khay hứng nước"),
    "BEDS": ("Size XS", "Size S", "Size M", "Size L", "Size XL", "Màu xám", "Màu xanh", "Màu hồng", "Vải cotton", "Vải chống nước", "Đệm làm mát", "Đệm nâng đỡ", "Có thể giặt", "Đệm lót thay thế", "Ổ có mái che", "Nhà gấp gọn", "Thảm chống trượt", "Đệm du lịch", "Ổ tròn premium", "Đệm vuông premium"),
    "CARRIERS": ("Size nhỏ", "Size vừa", "Size lớn", "Màu đen", "Màu xám", "Màu xanh", "Dạng đeo vai", "Dạng đeo trước", "Đáy cứng", "Đệm lót tháo rời", "Lưới thoáng khí premium", "Có bánh xe", "Túi gấp gọn", "Khóa an toàn", "Dây đeo ô tô", "Lồng cabin mini", "Lồng cabin vừa", "Lồng cabin lớn", "Balo trợ lực", "Túi chống thấm", "Túi cho thú nhỏ"),
    "CLOTHES": ("Size XS", "Size S", "Size M", "Size L", "Size XL", "Màu đỏ", "Màu xanh", "Màu hồng", "Màu vàng", "Màu xám", "Áo cotton", "Áo thoáng khí", "Áo chống nắng", "Áo len mềm", "Áo khoác có mũ", "Áo mưa trong", "Áo mưa có phản quang", "Bộ đồ mặc nhà", "Khăn choàng", "Nơ cổ"),
    "GROOMING": ("Lược răng thưa", "Lược răng dày", "Lược inox", "Lược gỡ lông rụng", "Găng tay chải lông", "Bàn chải lông mềm", "Bàn chải lông dài", "Kềm móng size nhỏ", "Kềm móng size lớn", "Dũa móng", "Kéo bo tròn", "Kéo tỉa lông", "Tông đơ mini", "Đầu tông đơ thay thế", "Máy sấy mini", "Khăn microfiber", "Bàn grooming mini", "Bộ vệ sinh lược", "Lược grooming premium", "Bộ chăm sóc móng"),
    "SUPPLEMENTS": ("Men vi sinh cho chó", "Men vi sinh cho mèo", "Dầu cá cho chó", "Dầu cá cho mèo", "Gel dinh dưỡng vị gà", "Gel dinh dưỡng vị cá", "Sữa bột cho chó con", "Sữa bột cho mèo con", "Bột bổ sung dinh dưỡng", "Snack bổ sung chất xơ", "Vitamin tổng hợp dạng viên", "Vitamin tổng hợp dạng gel", "Bột hỗ trợ tiêu hóa", "Dầu cá chai nhỏ", "Dầu cá chai lớn", "Bộ thìa đong", "Hộp bảo quản supplement", "Thức ăn bổ sung cho hamster", "Bổ sung dinh dưỡng cho thỏ"),
    "SMALL-PETS": ("Thức ăn hamster premium", "Thức ăn thỏ viên", "Thức ăn chuột lang premium", "Cỏ orchard cho thỏ", "Cỏ alfalfa cho thỏ", "Cỏ khô cho hamster", "Snack cỏ cho thỏ", "Snack trái cây sấy", "Đồ chơi gặm cành", "Đồ chơi gặm cầu", "Bánh xe hamster size vừa", "Bánh xe hamster size lớn", "Nhà gỗ hamster", "Nhà trú thỏ", "Bình nước chuột lang", "Bát sứ thú nhỏ", "Khay vệ sinh hamster", "Cát tắm hamster premium", "Lót chuồng giấy premium", "Lồng thỏ mini"),
    "AQUARIUM": ("Thức ăn cá bảy màu", "Thức ăn cá dĩa", "Thức ăn cá neon", "Thức ăn cá đáy", "Thức ăn cá viên nổi", "Thức ăn cá viên chìm", "Thức ăn tép cảnh", "Thức ăn rùa thủy sinh", "Bông lọc hồ cá", "Vật liệu lọc ceramic", "Ống hút cặn hồ cá", "Vợt cá mini", "Nhiệt kế hồ cá", "Sưởi hồ cá mini", "Sưởi hồ cá 100W", "Máy lọc treo", "Máy lọc thác", "Đá trang trí hồ cá", "Cây thủy sinh giả", "Cây thủy sinh dễ trồng", "Sỏi nền hồ cá", "Cát nền hồ cá", "Ống dẫn khí", "Van chia khí", "Bộ vệ sinh hồ cá", "Bộ test nước cơ bản", "Đèn hồ cá mini", "Nắp hồ cá", "Máy cho cá ăn tự động"),
    "BIRDS": ("Thức ăn vẹt premium", "Thức ăn cockatiel", "Thức ăn lovebird", "Thức ăn chim non", "Hạt kê mix", "Hạt yến mạch cho chim", "Hạt lanh cho chim", "Bánh thưởng cho vẹt", "Snack trái cây cho chim", "Khoáng đá cho chim", "Mai mực cho chim", "Đồ chơi gặm cho vẹt", "Xích đu treo lồng", "Thang dây cho chim", "Cầu đậu gỗ", "Cầu đậu tự nhiên", "Máng ăn inox", "Máng uống tự động", "Khay lót đáy lồng", "Lồng chim cỡ vừa", "Lồng chim cỡ lớn", "Áo phủ lồng chim", "Túi vận chuyển chim", "Bình phun sương chim", "Bộ vệ sinh lồng chim"),
    "RODENTS": ("Thức ăn hamster premium", "Thức ăn chuột lang premium", "Thức ăn gerbil", "Thức ăn chinchilla", "Cỏ timothy cho chuột lang", "Cỏ orchard cho chuột lang", "Snack cỏ nén", "Snack rau củ", "Snack táo sấy", "Đá mài răng", "Cầu gỗ gặm", "Hầm chơi chuột", "Ống chui chuột", "Bánh xe chạy silent", "Bánh xe hamster size lớn", "Bát ăn sứ", "Bình nước treo", "Khay vệ sinh", "Cát tắm chinchilla", "Lót chuồng giấy", "Lót chuồng hemp", "Nhà gỗ chuột lang", "Nhà trú gerbil", "Lồng chuột lang", "Rào quây thú nhỏ"),
    "REPTILES": ("Thức ăn viên cho rùa cạn", "Thức ăn cho thằn lằn cảnh", "Thức ăn khô cho gecko", "Thức ăn cho rồng úc dạng viên", "Khay ăn bò sát", "Khay nước cỡ lớn", "Hang trú size nhỏ", "Hang trú size lớn", "Cành leo chuồng bò sát", "Nền chuồng bò sát", "Giá thể vỏ dừa", "Giá thể rêu sphagnum", "Thảm sưởi chuồng", "Bộ điều nhiệt thảm sưởi", "Đèn UVB chuồng bò sát", "Đui đèn sưởi", "Kẹp bóng đèn", "Nhiệt ẩm kế điện tử", "Bình phun sương tự động", "Kẹp gắp đầu cong", "Khay ngâm rùa", "Tấm chắn nhiệt", "Lưới thông gió chuồng", "Hộp vận chuyển bò sát", "Bể nuôi bò sát cỡ lớn"),
}

COMBO_DEFINITIONS: tuple[dict[str, Any], ...] = (
    {
        "code": "COMBO-PUPPY",
        "name": "Combo Puppy",
        "description": "Hạt + pate + snack. Thành phần exact SKU do shop chọn khi nhập hàng.",
        "price": 199000,
        "species": "Chó",
    },
    {
        "code": "COMBO-KITTEN",
        "name": "Combo Kitten",
        "description": "Hạt + pate + snack. Thành phần exact SKU do shop chọn khi nhập hàng.",
        "price": 189000,
        "species": "Mèo",
    },
    {
        "code": "COMBO-NEW-CAT",
        "name": "Combo Mèo mới nuôi",
        "description": "Hạt + pate + cát + bát; cấu hình SKU cụ thể tại cửa hàng.",
        "price": 299000,
        "species": "Mèo",
    },
    {
        "code": "COMBO-NEW-DOG",
        "name": "Combo Chó mới nuôi",
        "description": "Hạt + snack + bát + dây dắt; cấu hình SKU cụ thể tại cửa hàng.",
        "price": 299000,
        "species": "Chó",
    },
    {
        "code": "COMBO-GROOM",
        "name": "Combo Grooming",
        "description": "Sữa tắm + lược + kềm móng; cấu hình SKU cụ thể tại cửa hàng.",
        "price": 199000,
        "species": "Chó, Mèo",
    },
    {
        "code": "COMBO-CAT-CLEAN",
        "name": "Combo Vệ sinh mèo",
        "description": "Cát + túi rác + khăn; cấu hình SKU cụ thể tại cửa hàng.",
        "price": 179000,
        "species": "Mèo",
    },
    {
        "code": "COMBO-PREMIUM-DOG",
        "name": "Combo Premium Dog",
        "description": "Hạt premium + snack + vitamin; cấu hình SKU cụ thể tại cửa hàng.",
        "price": 499000,
        "species": "Chó",
    },
    {
        "code": "COMBO-PREMIUM-CAT",
        "name": "Combo Premium Cat",
        "description": "Hạt premium + pate + snack; cấu hình SKU cụ thể tại cửa hàng.",
        "price": 449000,
        "species": "Mèo",
    },
)

COMBO_COMPONENTS: dict[str, tuple[tuple[str, int], ...]] = {
    "COMBO-PUPPY": (
        ("DEMO-DOG-FOOD-001", 1),
        ("DEMO-WET-FOOD-011", 1),
        ("DEMO-TREATS-001", 1),
    ),
    "COMBO-KITTEN": (
        ("DEMO-CAT-FOOD-003", 1),
        ("DEMO-WET-FOOD-005", 1),
        ("DEMO-TREATS-010", 1),
    ),
    "COMBO-NEW-CAT": (
        ("DEMO-CAT-FOOD-002", 1),
        ("DEMO-WET-FOOD-001", 1),
        ("DEMO-CAT-LITTER-001", 1),
        ("DEMO-BOWLS-001", 1),
    ),
    "COMBO-NEW-DOG": (
        ("DEMO-DOG-FOOD-002", 1),
        ("DEMO-TREATS-001", 1),
        ("DEMO-BOWLS-001", 1),
        ("DEMO-LEASH-004", 1),
    ),
    "COMBO-GROOM": (
        ("DEMO-BATH-001", 1),
        ("DEMO-GROOMING-001", 1),
        ("DEMO-GROOMING-006", 1),
    ),
    "COMBO-CAT-CLEAN": (
        ("DEMO-CAT-LITTER-001", 1),
        ("DEMO-HYGIENE-001", 1),
        ("DEMO-HYGIENE-003", 1),
    ),
    "COMBO-PREMIUM-DOG": (
        ("DEMO-DOG-FOOD-011", 1),
        ("DEMO-TREATS-007", 1),
        ("DEMO-SUPPLEMENTS-001", 1),
    ),
    "COMBO-PREMIUM-CAT": (
        ("DEMO-CAT-FOOD-015", 1),
        ("DEMO-WET-FOOD-003", 1),
        ("DEMO-TREATS-010", 1),
    ),
}


def catalog_products() -> list[dict[str, Any]]:
    products: list[dict[str, Any]] = []
    for group in PRODUCT_GROUPS:
        lines = group["products"].strip().splitlines()
        lines.extend(ADDITIONAL_PRODUCTS.get(group["code"], "").strip().splitlines())
        if len(lines) < 30:
            variants = FILLER_PRODUCTS.get(group["code"], ())
            if not variants:
                raise ValueError(
                    f"Thiếu tên biến thể để mở rộng catalog {group['code']}."
                )
            base_lines = [line.split("|") for line in lines]
            base_prices = [
                int(parts[2].strip())
                for parts in base_lines
                if len(parts) == 3
            ]
            base_unit = next(
                (parts[1].strip() for parts in base_lines if len(parts) == 3),
                "Cái",
            )
            default_price = base_prices[-1] if base_prices else 49000
            for index in range(len(lines), 30):
                variant = variants[(index - len(base_lines)) % len(variants)]
                lines.append(
                    f"{variant}|{base_unit}|{default_price + ((index % 5) * 5000)}"
                )
        for index, line in enumerate(lines, start=1):
            name, pack_size, price = (part.strip() for part in line.split("|"))
            normalized_name = name.casefold()
            age_group = (
                "Puppy / kitten"
                if "puppy" in normalized_name or "kitten" in normalized_name
                else "Senior"
                if "senior" in normalized_name
                else "Adult"
                if "adult" in normalized_name
                else "Mọi lứa tuổi"
            )
            unit = "cái"
            pack_lower = pack_size.casefold()
            if "combo" in pack_lower or "bộ" in pack_lower or "bộ " in normalized_name:
                unit = "bộ"
            elif "lon" in pack_lower or "lon" in normalized_name:
                unit = "lon"
            elif "hộp" in pack_lower or "hộp " in normalized_name:
                unit = "hộp"
            elif "chai" in pack_lower:
                unit = "chai"
            elif "tuýp" in pack_lower:
                unit = "tuýp"
            elif "cuộn" in pack_lower:
                unit = "cuộn"
            elif "tấm" in pack_lower:
                unit = "tấm"
            elif group["stock_category"] == "FOOD" or any(
                token in normalized_name
                for token in ("pate", "soup", "wet food", "cát", "lót chuồng")
            ):
                unit = "gói"
            products.append(
                {
                    "item_code": f"DEMO-{group['code']}-{index:03d}",
                    "name": name,
                    "stock_category": group["stock_category"],
                    "catalog_category": group["name"],
                    "target_species": group["species"],
                    "age_group": age_group,
                    "pack_size": pack_size,
                    "brand": "Demo / chưa xác định thương hiệu",
                    "barcode": "",
                    "retail_price": int(price),
                    "member_price": None,
                    "promotion_percent": 0,
                    "promotion_note": "",
                    "ingredients": "",
                    "image_path": "",
                    "is_demo": True,
                    "unit": unit,
                    "description": (
                        "Giá đề xuất demo, cần cửa hàng xác minh trước khi sử dụng. "
                        "Chưa có tồn kho cho tới khi nhập lô thực tế."
                    ),
                }
            )
    return products
