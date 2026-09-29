"""Demo food-catalog profiles and age-stage rules.

All entries are illustrative product-matching data, not veterinary advice.
Demo products and every feeding choice must be checked against the actual
product label and species-specific veterinary guidance before use.
"""

from __future__ import annotations

from typing import TypedDict


class FoodProfile(TypedDict):
    code: str
    match_terms: tuple[str, ...]
    species: str
    subspecies: str
    age_min_months: float | None
    age_max_months: float | None
    age_unit: str
    life_stage: str
    food_category: str
    food_type: str
    food_subtype: str
    breed_size: str
    suitable_weight_min: float | None
    suitable_weight_max: float | None
    feeding_frequency: str
    feeding_time: str
    serving_size: str
    protein_source: str
    nutrition_type: str
    purpose: str
    vitamin_c_content: str
    water_level: str
    diet_type: str


class AgeRule(TypedDict):
    code: str
    species: str
    subspecies: str
    breed_size: str
    life_stage: str
    age_min_months: float | None
    age_max_months: float | None
    age_unit: str
    food_category: str
    food_type: str
    status: str
    note: str


_FOOD_GROUPS: dict[
    str, tuple[tuple[str, str, str, str, tuple[str, ...]], ...]
] = {
    "Chó": (
        (
            "COMPLETE",
            "DRY",
            "Hạt hoàn chỉnh",
            "YOUNG",
            (
                "Sữa thay thế puppy",
                "Puppy starter",
                "Pate puppy starter",
                "Mousse puppy",
                "Hạt puppy ngâm mềm",
                "Hạt Puppy Toy",
                "Hạt Puppy Small",
                "Hạt Puppy Medium",
                "Hạt Puppy Large",
                "Hạt Puppy Giant",
            ),
        ),
        (
            "COMPLETE",
            "WET",
            "Thức ăn ướt hoàn chỉnh",
            "YOUNG",
            (
                "Pate puppy",
                "Mousse puppy meal",
                "Wet puppy meal",
                "Puppy growth dry",
                "Puppy high-protein dry",
                "Adult Small dry",
                "Adult Medium dry",
                "Adult Large dry",
                "Adult Giant dry",
                "Adult indoor dry",
            ),
        ),
        (
            "COMPLETE",
            "DRY",
            "Hạt theo giai đoạn / công thức",
            "ADULT",
            (
                "Adult active dry",
                "Working dog dry",
                "Sterilized dog dry",
                "Weight control dog dry",
                "Sensitive dog dry",
                "Digestive formula dog food",
                "Skin and coat dog food",
                "Adult dental-shape dog food",
                "Senior dog dry",
                "Senior dog weight-control dry",
            ),
        ),
        (
            "COMPLETE",
            "WET",
            "Thức ăn ướt theo giai đoạn",
            "ADULT",
            (
                "Pate adult",
                "Mousse adult dog",
                "Gravy adult dog food",
                "Soup-style dog food",
                "Freeze-dried chicken dog food",
                "Freeze-dried beef dog food",
                "Freeze-dried fish dog food",
                "Freeze-dried organ dog food",
                "Senior dog wet food",
                "Senior dog pate",
            ),
        ),
        (
            "COMPLEMENTARY",
            "TREAT",
            "Snack / thức ăn bổ sung",
            "ADULT",
            (
                "Jerky dog snack",
                "Soft dog treat",
                "Dog biscuit",
                "Meat dog snack",
                "Fish dog snack",
                "Dental-shape dog chew",
                "Firm dog chew",
                "Skin and coat dog treat",
                "Digestive-formula dog treat",
                "Joint-formula dog treat",
            ),
        ),
        (
            "COMPLETE",
            "WET",
            "Thức ăn mềm / senior",
            "SENIOR",
            (
                "Senior dog soft food",
                "Senior small-breed food",
                "Senior large-breed food",
                "Senior dog wet pate",
                "Senior dog mousse",
                "Senior dog dry food",
                "Senior dog dental-shape food",
                "Senior dog joint-formula food",
                "Senior dog weight-control food",
                "Adult small-breed wet food",
            ),
        ),
    ),
    "Mèo": (
        (
            "COMPLETE",
            "WET",
            "Thức ăn mềm cho mèo con",
            "YOUNG",
            (
                "Sữa thay thế kitten",
                "Sữa bột kitten",
                "Kitten starter",
                "Kitten mousse starter",
                "Kitten pate starter",
                "Kitten wet starter",
                "Kitten dry ngâm mềm",
                "Kitten dry",
                "Kitten growth dry",
                "Kitten high-energy dry",
            ),
        ),
        (
            "COMPLETE",
            "WET",
            "Thức ăn ướt kitten",
            "YOUNG",
            (
                "Kitten pate",
                "Kitten mousse",
                "Kitten gravy",
                "Kitten soup",
                "Kitten chicken complete food",
                "Kitten fish complete food",
                "Kitten indoor dry",
                "Kitten sensitive dry",
                "Kitten complete wet food",
                "Kitten growth wet food",
            ),
        ),
        (
            "COMPLEMENTARY",
            "TREAT",
            "Snack cho mèo",
            "ADULT",
            (
                "Kitten treat",
                "Kitten creamy treat",
                "Kitten freeze-dried treat",
                "Kitten training treat",
                "Adult freeze-dried chicken treat",
                "Adult freeze-dried beef treat",
                "Adult freeze-dried fish treat",
                "Chicken cat treat",
                "Fish cat treat",
                "Tuna cat treat",
            ),
        ),
        (
            "COMPLETE",
            "DRY",
            "Hạt theo nhu cầu / công thức",
            "ADULT",
            (
                "Adult cat dry food",
                "Adult cat wet food",
                "Indoor cat dry food",
                "Indoor cat wet food",
                "Sterilized cat dry food",
                "Sterilized cat wet food",
                "Weight-control cat food",
                "Hairball-formula cat food",
                "Sensitive cat food",
                "Digestive-formula cat food",
            ),
        ),
        (
            "COMPLETE",
            "WET",
            "Pate / thức ăn ướt",
            "ADULT",
            (
                "Adult dental-shape cat food",
                "Adult skin and coat cat food",
                "Pate gà cho mèo",
                "Pate bò cho mèo",
                "Pate cá cho mèo",
                "Pate cá ngừ cho mèo",
                "Pate cá hồi cho mèo",
                "Pate vịt cho mèo",
                "Pate thỏ cho mèo",
                "Mousse adult cat food",
            ),
        ),
        (
            "COMPLETE",
            "WET",
            "Senior / nhiều kết cấu",
            "SENIOR",
            (
                "Jelly cat food",
                "Gravy cat food",
                "Soup cat food",
                "Broth cat food",
                "Chunk in gravy cat food",
                "Senior cat dry food",
                "Senior cat wet food",
                "Senior cat mousse",
                "Senior cat pate",
                "Adult creamy cat treat",
            ),
        ),
    ),
    "Thỏ": (
        (
            "COMPLETE",
            "WET",
            "Thức ăn sơ sinh / cai sữa",
            "YOUNG",
            (
                "Sữa thay thế cho thỏ",
                "Thức ăn cai sữa cho thỏ",
                "Pellet junior rabbit",
                "Pellet thỏ con",
                "Pellet thỏ non",
                "Pellet thỏ trưởng thành",
                "Pellet thỏ senior",
                "Cỏ Timothy cho thỏ",
                "Cỏ Orchard cho thỏ",
                "Cỏ Meadow cho thỏ",
            ),
        ),
        (
            "FORAGE",
            "HAY",
            "Cỏ khô / forage",
            "ALL",
            (
                "Cỏ Oat cho thỏ",
                "Cỏ Alfalfa cho thỏ non",
                "Cỏ Botanical cho thỏ",
                "Hỗn hợp cỏ khô cho thỏ",
                "Hay cube cho thỏ",
                "Hay stick cho thỏ",
                "Hay ball cho thỏ",
                "Cỏ sấy cho thỏ",
                "Forage mix cho thỏ",
                "Botanical mix cho thỏ",
            ),
        ),
        (
            "COMPLEMENTARY",
            "HERB",
            "Rau thơm / forage",
            "ALL",
            (
                "Dandelion khô cho thỏ",
                "Plantain khô cho thỏ",
                "Chamomile khô cho thỏ",
                "Mint khô cho thỏ",
                "Basil khô cho thỏ",
                "Parsley khô cho thỏ",
                "Coriander khô cho thỏ",
                "Carrot khô cho thỏ",
                "Apple khô cho thỏ",
                "Banana khô cho thỏ",
            ),
        ),
        (
            "COMPLEMENTARY",
            "VEGETABLE",
            "Rau / hỗn hợp rau",
            "ALL",
            (
                "Strawberry khô cho thỏ",
                "Vegetable mix cho thỏ",
                "Herb mix cho thỏ",
                "Leafy green mix cho thỏ",
                "Dried forage mix cho thỏ",
                "Botanical forage cho thỏ",
                "Vegetable treat cho thỏ",
                "Carrot treat cho thỏ",
                "Apple treat cho thỏ",
                "Berry treat cho thỏ",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Pellet / thức ăn hoàn chỉnh",
            "ADULT",
            (
                "Timothy pellet cho thỏ",
                "Alfalfa pellet cho thỏ non",
                "High-fiber pellet cho thỏ trưởng thành",
                "Junior high-fiber pellet cho thỏ",
                "Adult high-fiber pellet cho thỏ",
                "Senior fiber food cho thỏ",
                "Fiber snack cho thỏ",
                "Herbal treat cho thỏ",
                "Hay treat cho thỏ",
                "Dental hay cho thỏ",
            ),
        ),
        (
            "COMPLEMENTARY",
            "TREAT",
            "Snack / forage theo nhãn",
            "ADULT",
            (
                "Dental chew cho thỏ",
                "Hay biscuit cho thỏ",
                "Forage biscuit cho thỏ",
                "Herb biscuit cho thỏ",
                "Premium forage cho thỏ",
                "Organic hay cho thỏ",
                "Natural forage cho thỏ",
                "Weight-control pellet cho thỏ",
                "Digestive-formula food cho thỏ",
                "Complete rabbit food",
            ),
        ),
    ),
    "Hamster": (
        (
            "COMPLETE",
            "MIX",
            "Hamster mix / pellet",
            "ALL",
            (
                "Hamster mother milk replacer",
                "Hamster weaning soft mix",
                "Hamster juvenile small-seed mix",
                "Hamster junior pellet",
                "Hamster young-adult complete mix",
                "Hamster adult seed mix",
                "Hamster adult pellet",
                "Hamster senior soft mix",
                "Hamster senior pellet",
                "Hamster complete food",
            ),
        ),
        (
            "COMPLETE",
            "SEED",
            "Hạt / ngũ cốc",
            "ALL",
            (
                "Hamster seed mix",
                "Hamster grain mix",
                "Hamster sunflower seed blend",
                "Hamster pumpkin seed blend",
                "Hamster millet blend",
                "Hamster oat blend",
                "Hamster barley blend",
                "Hamster wheat blend",
                "Hamster rice blend",
                "Hamster flax and sesame blend",
            ),
        ),
        (
            "COMPLEMENTARY",
            "SEED",
            "Hạt bổ sung theo nhãn",
            "ALL",
            (
                "Hamster chia seed treat",
                "Hamster mealworm treat",
                "Hamster cricket treat",
                "Hamster dried shrimp treat",
                "Hamster egg-protein food",
                "Hamster dried carrot",
                "Hamster broccoli snack",
                "Hamster pea snack",
                "Hamster corn snack",
                "Hamster fruit mix",
            ),
        ),
        (
            "COMPLEMENTARY",
            "MIX",
            "Trái cây / rau / forage",
            "ALL",
            (
                "Hamster apple snack",
                "Hamster banana snack",
                "Hamster strawberry snack",
                "Hamster papaya snack",
                "Hamster blueberry snack",
                "Hamster herb mix",
                "Hamster vegetable mix",
                "Hamster forage mix",
                "Hamster seed stick",
                "Hamster biscuit",
            ),
        ),
        (
            "COMPLEMENTARY",
            "TREAT",
            "Snack / protein theo nhãn",
            "ALL",
            (
                "Hamster protein treat",
                "Hamster fiber snack",
                "Hamster dental-shape treat",
                "Hamster dried insect mix",
                "Hamster oat treat",
                "Hamster natural seed treat",
                "Hamster vegetable treat",
                "Hamster fruit treat",
                "Hamster soft treat",
                "Hamster crunchy treat",
            ),
        ),
        (
            "COMPLETE",
            "MIX",
            "Complete food theo giai đoạn",
            "ALL",
            (
                "Hamster junior complete mix",
                "Hamster young complete pellet",
                "Hamster adult complete mix",
                "Hamster adult extruded food",
                "Hamster senior easy-eat mix",
                "Hamster senior energy-control mix",
                "Hamster dwarf-type food",
                "Hamster Syrian-type food",
                "Hamster species-specific mix",
                "Hamster label-guided complete diet",
            ),
        ),
    ),
    "Chim": (
        (
            "COMPLETE",
            "FORMULA",
            "Thức ăn theo loài / giai đoạn",
            "SPECIES_DEPENDENT",
            (
                "Hand-feeding formula for pet birds",
                "Bird weaning formula",
                "Bird baby soft food",
                "Bird juvenile food",
                "Bird seed mix",
                "Premium bird seed mix",
                "Species-specific bird seed",
                "Bird pellet",
                "Bird soft food",
                "Bird egg food",
            ),
        ),
        (
            "COMPLETE",
            "MIX",
            "Hỗn hợp theo loài",
            "SPECIES_DEPENDENT",
            (
                "Bird breeding food",
                "Bird molt-stage food",
                "Bird fruit mix",
                "Bird vegetable mix",
                "Bird herb mix",
                "Bird millet",
                "Bird sunflower seed",
                "Bird pumpkin seed",
                "Bird safflower seed",
                "Bird flax seed",
            ),
        ),
        (
            "COMPLEMENTARY",
            "SEED",
            "Hạt / ngũ cốc theo loài",
            "SPECIES_DEPENDENT",
            (
                "Bird oat food",
                "Bird sesame seed",
                "Bird mineral food",
                "Bird calcium food",
                "Bird grit product",
                "Bird fruit treat",
                "Bird vegetable treat",
                "Bird seed stick",
                "Bird biscuit",
                "Bird training treat",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Pellet / công thức theo loài",
            "SPECIES_DEPENDENT",
            (
                "Budgerigar seed-and-pellet food",
                "Cockatiel seed-and-pellet food",
                "Finch seed food",
                "Canary seed food",
                "Lovebird pellet food",
                "Conure pellet food",
                "African grey pellet food",
                "Macaw pellet food",
                "Parrot species-specific food",
                "Small-bird complete pellet",
            ),
        ),
        (
            "COMPLEMENTARY",
            "MIX",
            "Thức ăn bổ sung theo loài",
            "SPECIES_DEPENDENT",
            (
                "Bird soft egg mix",
                "Bird sprouted seed mix",
                "Bird dried fruit mix",
                "Bird leafy-green mix",
                "Bird herb-and-seed mix",
                "Bird millet spray",
                "Bird safflower blend",
                "Bird oat-and-seed blend",
                "Bird forage blend",
                "Bird species-specific treat",
            ),
        ),
        (
            "COMPLEMENTARY",
            "TREAT",
            "Snack theo nhãn loài",
            "SPECIES_DEPENDENT",
            (
                "Bird soft training treat",
                "Bird crunchy seed treat",
                "Bird fruit chew",
                "Bird vegetable chew",
                "Bird seed biscuit",
                "Bird egg treat",
                "Bird pellet treat",
                "Bird forage treat",
                "Bird small-parrot snack",
                "Bird large-parrot snack",
            ),
        ),
    ),
    "Cá": (
        (
            "COMPLETE",
            "POWDER",
            "Thức ăn fry / hạt mịn",
            "SPECIES_DEPENDENT",
            (
                "Fish fry powder food",
                "Fish micro food",
                "Fish infusoria-type food",
                "Artemia nauplii fish food",
                "Fish micro pellet",
                "Fish juvenile micro pellet",
                "Small granule fish food",
                "Baby pellet fish food",
                "Fish species-specific fry food",
                "Fry food for freshwater fish",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Hạt / pellet theo tầng nước",
            "SPECIES_DEPENDENT",
            (
                "Fish floating pellet",
                "Fish slow-sinking pellet",
                "Fish sinking pellet",
                "Fish flake food",
                "Fish granule food",
                "Fish algae wafer",
                "Fish spirulina food",
                "Fish krill food",
                "Fish color-formula food",
                "Fish growth-formula food",
            ),
        ),
        (
            "COMPLEMENTARY",
            "FROZEN",
            "Thức ăn đông lạnh / đông khô",
            "SPECIES_DEPENDENT",
            (
                "Frozen Artemia fish food",
                "Frozen bloodworm fish food",
                "Frozen Daphnia fish food",
                "Frozen Tubifex fish food",
                "Frozen Mysis fish food",
                "Freeze-dried Artemia fish food",
                "Freeze-dried bloodworm fish food",
                "Freeze-dried Daphnia fish food",
                "Fish live-food product",
                "Fish herbivore food",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Công thức theo khẩu phần",
            "SPECIES_DEPENDENT",
            (
                "Fish carnivore complete food",
                "Fish omnivore complete food",
                "Fish bottom-feeder pellet",
                "Fish mid-water pellet",
                "Fish surface-feeder flake",
                "Goldfish species-specific food",
                "Betta species-specific food",
                "Tropical fish community food",
                "Marine fish complete food",
                "Freshwater fish complete food",
            ),
        ),
        (
            "COMPLEMENTARY",
            "MIX",
            "Thức ăn bổ sung theo loài",
            "SPECIES_DEPENDENT",
            (
                "Fish breeding-stage food",
                "Fish vacation food",
                "Fish algae wafer treat",
                "Fish spirulina supplement food",
                "Fish vegetable wafer",
                "Fish krill treat",
                "Fish Artemia treat",
                "Fish Daphnia treat",
                "Fish frozen-food mix",
                "Fish freeze-dried-food mix",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Pellet theo kích cỡ / tầng nước",
            "SPECIES_DEPENDENT",
            (
                "Nano fish micro granule",
                "Small fish floating granule",
                "Medium fish floating pellet",
                "Large fish floating pellet",
                "Small fish sinking pellet",
                "Medium fish sinking pellet",
                "Bottom fish sinking wafer",
                "Herbivorous fish algae pellet",
                "Carnivorous fish protein pellet",
                "Species-specific aquarium fish diet",
            ),
        ),
    ),
    "Bò sát": (
        (
            "COMPLETE",
            "PELLET",
            "Thức ăn theo loài / giai đoạn",
            "SPECIES_DEPENDENT",
            (
                "Turtle species-specific pellet",
                "Aquatic turtle juvenile food",
                "Aquatic turtle adult food",
                "Tortoise species-specific pellet",
                "Tortoise juvenile food",
                "Tortoise adult food",
                "Turtle species-specific complete food",
                "Turtle soft food",
                "Turtle complete pellet",
                "Turtle label-guided food",
            ),
        ),
        (
            "COMPLEMENTARY",
            "DRIED",
            "Thức ăn bổ sung theo loài",
            "SPECIES_DEPENDENT",
            (
                "Dried insect turtle food",
                "Dried shrimp turtle food",
                "Dried mealworm turtle food",
                "Dried cricket turtle food",
                "Turtle herb mix",
                "Tortoise forage mix",
                "Turtle plant-food mix",
                "Turtle fruit mix",
                "Turtle vegetable mix",
                "Turtle species-specific treat",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Pellet / granule theo nhãn",
            "SPECIES_DEPENDENT",
            (
                "Small aquatic turtle pellet",
                "Large aquatic turtle pellet",
                "Turtle floating pellet",
                "Turtle sinking pellet",
                "Tortoise herbivore pellet",
                "Tortoise grass pellet",
                "Turtle insectivore pellet",
                "Turtle omnivore pellet",
                "Turtle carnivore pellet",
                "Turtle juvenile-formula food",
            ),
        ),
        (
            "COMPLEMENTARY",
            "INSECT",
            "Côn trùng / đạm bổ sung",
            "SPECIES_DEPENDENT",
            (
                "Live cricket turtle food",
                "Live mealworm turtle food",
                "Dried cricket turtle treat",
                "Dried mealworm turtle treat",
                "Aquatic turtle dried insect mix",
                "Turtle insect mix",
                "Turtle frozen insect food",
                "Turtle freeze-dried insect food",
                "Turtle shrimp treat",
                "Turtle insect treat",
            ),
        ),
        (
            "COMPLEMENTARY",
            "VEGETABLE",
            "Rau / forage theo loài",
            "SPECIES_DEPENDENT",
            (
                "Tortoise leafy-green food",
                "Tortoise dried-grass food",
                "Tortoise forage biscuit",
                "Tortoise dried-flower mix",
                "Turtle aquatic-plant food",
                "Turtle vegetable food",
                "Turtle leafy-green mix",
                "Turtle botanical mix",
                "Turtle forage snack",
                "Turtle vegetable treat",
            ),
        ),
        (
            "COMPLETE",
            "PELLET",
            "Thức ăn hoàn chỉnh theo loài",
            "SPECIES_DEPENDENT",
            (
                "Box turtle complete food",
                "Red-eared slider species food",
                "Land tortoise complete food",
                "Aquatic turtle complete food",
                "Herbivorous turtle complete food",
                "Insectivorous turtle complete food",
                "Omnivorous turtle complete food",
                "Small-turtle complete pellet",
                "Large-turtle complete pellet",
                "Species-dependent turtle diet",
            ),
        ),
    ),
    "Nhím": (
        (
            "COMPLETE",
            "DRY",
            "Thức ăn hoàn chỉnh theo loài",
            "SPECIES_DEPENDENT",
            (
                "Hedgehog species-specific complete food",
                "Hedgehog insectivore-formula food",
                "Hedgehog adult dry food",
                "Hedgehog juvenile dry food",
                "Hedgehog small-kibble food",
                "Hedgehog complete pellet",
                "Hedgehog label-guided food",
                "Hedgehog mixed complete food",
                "Hedgehog soft complete food",
                "Hedgehog keeper-formula food",
            ),
        ),
        (
            "COMPLEMENTARY",
            "INSECT",
            "Thức ăn bổ sung theo loài",
            "SPECIES_DEPENDENT",
            (
                "Hedgehog dried insect treat",
                "Hedgehog mealworm treat",
                "Hedgehog cricket treat",
                "Hedgehog insect mix",
                "Hedgehog freeze-dried insect food",
                "Hedgehog cooked egg treat",
                "Hedgehog meat-based treat",
                "Hedgehog forage snack",
                "Hedgehog species-specific snack",
                "Hedgehog label-guided treat",
            ),
        ),
    ),
}


def _food_category_label(value: str) -> str:
    return {
        "COMPLETE": "Thức ăn hoàn chỉnh",
        "COMPLEMENTARY": "Thức ăn bổ sung",
        "FORAGE": "Cỏ và forage",
    }.get(value, value)


def _food_type_label(value: str) -> str:
    return {
        "DRY": "Hạt khô",
        "WET": "Thức ăn ướt",
        "TREAT": "Snack",
        "HAY": "Cỏ khô",
        "PELLET": "Pellet",
        "HERB": "Thảo mộc",
        "VEGETABLE": "Rau củ",
        "MIX": "Hỗn hợp",
        "SEED": "Hạt giống",
        "FORMULA": "Công thức",
        "POWDER": "Dạng bột",
        "FROZEN": "Đông lạnh",
        "INSECT": "Côn trùng",
        "DRIED": "Sấy khô",
        "SPECIES_DEPENDENT": "Theo loài",
    }.get(value, value)


def _age_for_profile(
    species: str, product_name: str, life_stage: str
) -> tuple[float | None, float | None, str]:
    name = product_name.casefold()
    if species == "Chó":
        if "senior" in name:
            return 84, None, "SENIOR"
        if "puppy" in name:
            return 2, 6, "YOUNG"
        if "adult small" in name or "adult toy" in name:
            return 10, None, "ADULT"
        if "adult medium" in name:
            return 12, None, "ADULT"
        if "adult large" in name:
            return 15, None, "ADULT"
        if "adult giant" in name:
            return 18, None, "ADULT"
        if "adult" in name or life_stage == "ADULT":
            return 18, None, "ADULT"
    elif species == "Mèo":
        if "senior" in name:
            return 84, None, "SENIOR"
        if "kitten" in name:
            if "starter" in name or "ngâm mềm" in name:
                return 0.75, 2, "WEANING"
            return 2, 12, "YOUNG"
        if "adult" in name or life_stage == "ADULT":
            return 8, None, "ADULT"
    elif species == "Thỏ":
        if "sữa thay thế" in name:
            return 0, 0.75, "NEONATAL"
        if "cai sữa" in name:
            return 0.75, 2, "WEANING"
        if "thỏ non" in name or "junior" in name or "thỏ con" in name:
            return 2, 6, "YOUNG"
        if "senior" in name:
            return None, None, "SENIOR"
        if "trưởng thành" in name or life_stage == "ADULT":
            return 6, None, "ADULT"
    elif species == "Hamster":
        if "senior" in name:
            return 12, None, "SENIOR"
        if "mother milk" in name:
            return 0, 0.75, "NEONATAL"
        if "weaning" in name:
            return 0.75, 1, "WEANING"
        if "juvenile" in name or "junior" in name:
            return 1, 2, "YOUNG"
        if "young" in name:
            return 2, 6, "YOUNG"
        if "adult" in name or life_stage == "ADULT":
            return 6, 12, "ADULT"
    return None, None, ""


def _build_food_profiles() -> tuple[FoodProfile, ...]:
    profiles: list[FoodProfile] = []
    for species, groups in _FOOD_GROUPS.items():
        prefix = {
            "Chó": "DOG",
            "Mèo": "CAT",
            "Thỏ": "RABBIT",
            "Hamster": "HAMSTER",
            "Chim": "BIRD",
            "Cá": "FISH",
            "Bò sát": "REPTILE",
            "Nhím": "HEDGEHOG",
        }[species]
        for food_category, food_type, food_subtype, group_stage, products in groups:
            for product_name in products:
                code = f"{prefix}-FOOD-{len(profiles) + 1:03d}"
                age_min, age_max, age_stage = _age_for_profile(
                    species, product_name, group_stage
                )
                stage = age_stage or group_stage
                size = ""
                if species == "Chó":
                    for size_name in ("Toy", "Small", "Medium", "Large", "Giant"):
                        if size_name.casefold() in product_name.casefold():
                            size = size_name.upper()
                            break
                terms = (product_name.casefold(),)
                protein = ""
                for source in ("chicken", "beef", "fish", "tuna", "salmon", "duck", "rabbit"):
                    if source in product_name.casefold():
                        protein = source.capitalize()
                        break
                profiles.append(
                    {
                        "code": code,
                        "species": species,
                        "match_terms": terms,
                        "food_category": _food_category_label(food_category),
                        "food_type": _food_type_label(food_type),
                        "food_subtype": food_subtype,
                        "subspecies": "",
                        "age_min_months": age_min,
                        "age_max_months": age_max,
                        "age_unit": "MONTH",
                        "life_stage": stage,
                        "breed_size": size,
                        "suitable_weight_min": None,
                        "suitable_weight_max": None,
                        "feeding_frequency": "Theo nhãn sản phẩm",
                        "feeding_time": "",
                        "serving_size": "",
                        "protein_source": protein,
                        "nutrition_type": (
                            "Complete"
                            if food_category == "COMPLETE"
                            else "Complementary"
                        ),
                        "purpose": "Phân loại theo công thức và hướng dẫn trên nhãn",
                        "vitamin_c_content": "",
                        "water_level": "",
                        "diet_type": "",
                    }
                )
    return tuple(profiles)


FOOD_PROFILES: tuple[FoodProfile, ...] = _build_food_profiles()


def _rule(
    code: str,
    species: str,
    life_stage: str,
    age_min: float | None,
    age_max: float | None,
    food_category: str,
    food_type: str,
    note: str,
    breed_size: str = "",
    subspecies: str = "",
) -> AgeRule:
    return {
        "code": code,
        "species": species,
        "subspecies": subspecies,
        "breed_size": breed_size,
        "life_stage": life_stage,
        "age_min_months": age_min,
        "age_max_months": age_max,
        "age_unit": "MONTH",
        "food_category": _food_category_label(food_category),
        "food_type": _food_type_label(food_type),
        "status": "ACTIVE",
        "note": note,
    }


_DOG_SIZE_TRANSITIONS = (
    ("TOY", 10, 12),
    ("SMALL", 10, 12),
    ("MEDIUM", 12, 18),
    ("LARGE", 15, 18),
    ("GIANT", 18, 24),
)

_rules: list[AgeRule] = []
for size, puppy_end, young_end in _DOG_SIZE_TRANSITIONS:
    _rules.extend(
        (
            _rule(
                f"DOG-{size}-NEONATAL",
                "Chó",
                "NEONATAL",
                0,
                0.75,
                "COMPLETE",
                "WET",
                "Mốc sơ sinh theo đề xuất; làm theo tư vấn thú y và nhãn sữa thay thế.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-WEANING",
                "Chó",
                "WEANING",
                0.75,
                2,
                "COMPLETE",
                "WET",
                "Mốc cai sữa theo đề xuất; chuyển đổi phù hợp từng cá thể.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-PUPPY",
                "Chó",
                "PUPPY",
                2,
                6,
                "COMPLETE",
                "DRY",
                "Puppy theo đề xuất; giống lớn/khổng lồ có thể cần công thức puppy lâu hơn. Kiểm tra nhãn.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-LATE-PUPPY",
                "Chó",
                "LATE_PUPPY",
                6,
                puppy_end,
                "COMPLETE",
                "DRY",
                "Khoảng puppy cuối kỳ minh họa theo kích cỡ; kiểm tra nhãn sản phẩm.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-YOUNG-ADULT",
                "Chó",
                "YOUNG_ADULT",
                puppy_end,
                young_end,
                "COMPLETE",
                "DRY",
                "Khoảng chuyển tiếp theo ví dụ phân cỡ trong đề xuất; không thay thế nhãn sản phẩm.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-ADULT",
                "Chó",
                "ADULT",
                young_end,
                84,
                "COMPLETE",
                "DRY",
                "Khoảng phân loại demo; mốc trưởng thành phụ thuộc giống và cá thể.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-MATURE",
                "Chó",
                "MATURE",
                84,
                108,
                "COMPLETE",
                "DRY",
                "Giai đoạn tham khảo trong đề xuất; cần xét kích thước và nhãn.",
                breed_size=size,
            ),
            _rule(
                f"DOG-{size}-SENIOR",
                "Chó",
                "SENIOR",
                108,
                None,
                "COMPLETE",
                "DRY",
                "Giai đoạn tham khảo trong đề xuất; cần xét kích thước và nhãn.",
                breed_size=size,
            ),
        )
    )
_rules.extend(
    (
        _rule("CAT-NEONATAL", "Mèo", "NEONATAL", 0, 0.75, "COMPLETE", "WET", "Theo đề xuất; theo dõi hướng dẫn nhãn và tư vấn thú y."),
        _rule("CAT-WEANING", "Mèo", "WEANING", 0.75, 2, "COMPLETE", "WET", "Theo đề xuất; chuyển thức ăn phù hợp từng cá thể."),
        _rule("CAT-KITTEN", "Mèo", "KITTEN", 2, 4, "COMPLETE", "DRY", "Giai đoạn kitten theo đề xuất; kiểm tra tuổi ghi trên nhãn."),
        _rule("CAT-KITTEN-GROWTH", "Mèo", "KITTEN_GROWTH", 4, 6, "COMPLETE", "DRY", "Giai đoạn tăng trưởng theo đề xuất; kiểm tra tuổi ghi trên nhãn."),
        _rule("CAT-LATE-KITTEN", "Mèo", "LATE_KITTEN", 6, 8, "COMPLETE", "DRY", "Giai đoạn kitten cuối theo đề xuất; kiểm tra tuổi ghi trên nhãn."),
        _rule("CAT-TRANSITION", "Mèo", "TRANSITION", 8, 12, "COMPLETE", "DRY", "Khoảng chuyển tiếp theo đề xuất; sản phẩm có thể ghi mốc khác."),
        _rule("CAT-ADULT", "Mèo", "ADULT", 12, 84, "COMPLETE", "DRY", "Khoảng adult theo đề xuất; kiểm tra tuổi trên nhãn."),
        _rule("CAT-SENIOR", "Mèo", "SENIOR", 84, None, "COMPLETE", "DRY", "Từ khoảng 7 năm theo đề xuất; tuổi senior tùy sản phẩm và cá thể."),
        _rule("RABBIT-NEONATAL", "Thỏ", "NEONATAL", 0, 0.75, "COMPLETE", "WET", "Ví dụ trong đề xuất; không dùng thay tư vấn chăm sóc thỏ sơ sinh."),
        _rule("RABBIT-WEANING", "Thỏ", "WEANING", 0.75, 2, "COMPLETE", "WET", "Khoảng cai sữa minh họa từ đề xuất; xác minh theo loài, cá thể và nhãn."),
        _rule("RABBIT-JUNIOR", "Thỏ", "YOUNG", 2, 6, "COMPLETE", "PELLET", "Đề xuất nêu pellet con non khoảng 2–3 tháng; khoảng này chỉ là phân loại demo."),
        _rule("RABBIT-ADULT", "Thỏ", "ADULT", 6, None, "COMPLETE", "PELLET", "Đề xuất nêu pellet trưởng thành khoảng 6–12 tháng trở đi; xác minh nhãn và hướng dẫn thú y."),
        _rule("RABBIT-HAY", "Thỏ", "SPECIES_DEPENDENT", None, None, "FORAGE", "HAY", "Cỏ khô được phân loại riêng; xác minh loại cỏ, nhãn và hướng dẫn chăm sóc."),
        _rule("HAMSTER-NEONATAL", "Hamster", "NEONATAL", 0, 0.75, "COMPLETE", "MIX", "Các mốc trong đề xuất là ví dụ tổng quát; phân loài hamster có thể khác."),
        _rule("HAMSTER-WEANING", "Hamster", "WEANING", 0.75, 1, "COMPLETE", "MIX", "Các mốc trong đề xuất là ví dụ tổng quát; phân loài hamster có thể khác."),
        _rule("HAMSTER-JUVENILE", "Hamster", "JUVENILE", 1, 2, "COMPLETE", "MIX", "Các mốc trong đề xuất là ví dụ tổng quát; phân loài hamster có thể khác."),
        _rule("HAMSTER-YOUNG-ADULT", "Hamster", "YOUNG_ADULT", 2, 6, "COMPLETE", "MIX", "Các mốc trong đề xuất là ví dụ tổng quát; phân loài hamster có thể khác."),
        _rule("HAMSTER-ADULT", "Hamster", "ADULT", 6, 12, "COMPLETE", "MIX", "Các mốc trong đề xuất là ví dụ tổng quát; phân loài hamster có thể khác."),
        _rule("HAMSTER-SENIOR", "Hamster", "SENIOR", 12, None, "COMPLETE", "MIX", "Mốc senior trong đề xuất; phân loài hamster và sản phẩm có thể khác."),
    )
)
for species, common_name in (
    ("Chim", "Loài chim cảnh cụ thể"),
    ("Cá", "Loài cá và tầng nước cụ thể"),
    ("Bò sát", "Loài bò sát cụ thể"),
    ("Nhím", "Loài nhím nuôi cụ thể"),
):
    prefix = {
        "Chim": "BIRD",
        "Cá": "FISH",
        "Bò sát": "REPTILE",
        "Nhím": "HEDGEHOG",
    }[species]
    for stage in ("JUVENILE", "ADULT", "BREEDING"):
        _rules.append(
            _rule(
                f"{prefix}-{stage}-SPECIES-DEPENDENT",
                species,
                stage,
                None,
                None,
                "COMPLETE",
                "SPECIES_DEPENDENT",
                f"Không có mốc tuổi chung an toàn; phụ thuộc {common_name}, công thức và nhãn sản phẩm. "
                "Tuổi để trống có chủ đích.",
                subspecies=common_name,
            )
        )

AGE_RULES: tuple[AgeRule, ...] = tuple(_rules)


def _validate_seed_data() -> None:
    codes = [profile["code"] for profile in FOOD_PROFILES]
    rule_codes = [rule["code"] for rule in AGE_RULES]
    if len(codes) != len(set(codes)):
        raise ValueError("FOOD_PROFILES contains duplicate codes")
    if len(rule_codes) != len(set(rule_codes)):
        raise ValueError("AGE_RULES contains duplicate codes")
    expected_counts = {
        "Chó": 60,
        "Mèo": 60,
        "Thỏ": 60,
        "Hamster": 60,
        "Chim": 60,
        "Cá": 60,
        "Bò sát": 60,
    }
    counts = {species: 0 for species in expected_counts}
    counts["Nhím"] = 0
    for profile in FOOD_PROFILES:
        counts[profile["species"]] += 1
        if profile["age_unit"] != "MONTH":
            raise ValueError(f"Unexpected age unit in {profile['code']}")
    if any(counts[species] != expected for species, expected in expected_counts.items()):
        raise ValueError(f"Unexpected food profile counts: {counts}")
    if counts["Nhím"] < 8:
        raise ValueError("Expected at least eight hedgehog demo profiles")
    for rule in AGE_RULES:
        if rule["age_unit"] != "MONTH":
            raise ValueError(f"Unexpected age unit in {rule['code']}")
        minimum, maximum = rule["age_min_months"], rule["age_max_months"]
        if minimum is not None and maximum is not None and minimum > maximum:
            raise ValueError(f"Invalid age range in {rule['code']}")


_validate_seed_data()
