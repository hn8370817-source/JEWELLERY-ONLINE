from app import app, db
from models import Category, Product, ProductImage

categories_list = [
    "Necklace", "Artificial sets", "Ear rings", "Rings",
    "Bangles and Bracelets", "Tikka", "Jewellery Accesories",
    "Anklets", "Jewellery Organizers"
]

products_data = {
    "Necklace": [
        ("Golden Pearl Necklace", "Elegant pearl set", 1299, 5),
        ("Silver Choker", "Modern choker", 899, 0),   # out of stock example
        ("Kundan Necklace", "Traditional kundan", 1599, 10),
        ("Diamond Necklace", "American diamond", 2199, 3),
        ("Beaded Necklace", "Colourful beads", 749, 8),
    ],
    "Artificial sets": [
        ("Meenakari Set", "Rajasthani art", 1899, 4),
        ("Temple Set", "Antique gold finish", 1499, 6),
        ("Pearl Choker Set", "Includes earrings", 999, 0),
        ("Kundan Set", "Full bridal set", 2499, 2),
        ("Pink Stone Set", "Party wear", 1199, 7),
    ],
    "Ear rings": [
        ("Jhumka Earrings", "Classic gold", 599, 12),
        ("Chandbali Earrings", "Filigree work", 799, 5),
        ("Stud Earrings", "Diamond studs", 499, 0),
        ("Dangler Earrings", "Long danglers", 699, 9),
        ("Pearl Drop Earrings", "Elegant drops", 899, 3),
    ],
    "Rings": [
        ("Solitaire Ring", "Cubic zirconia", 399, 15),
        ("Gold Band", "Classic band", 299, 20),
        ("Cocktail Ring", "Big stone ring", 499, 4),
        ("Silver Ring", "Oxidized silver", 249, 0),
        ("Adjustable Ring", "Boho style", 179, 18),
    ],
    "Bangles and Bracelets": [
        ("Kada Bangles", "Heavy kadas", 1299, 5),
        ("Choora Set", "Traditional red", 999, 7),
        ("Chain Bracelet", "Modern bracelet", 799, 10),
        ("Beaded Bracelet", "Colourful beads", 349, 0),
        ("Cuff Bracelet", "Silver cuff", 599, 6),
    ],
    "Tikka": [
        ("Maang Tikka", "Kundan maang tikka", 699, 8),
        ("Matha Patti", "Side matha patti", 1199, 3),
        ("Passa Tikka", "One side passa", 899, 0),
        ("Round Tikka", "Simple round", 449, 12),
        ("Gold Plated Tikka", "Gold finish", 549, 9),
    ],
    "Jewellery Accesories": [
        ("Nose Pin", "Diamond nose pin", 199, 30),
        ("Hair Clip", "Stone work", 299, 15),
        ("Waistband", "Kamarbandh", 1499, 2),
        ("Armlet", "Bajuband", 899, 5),
        ("Payal", "Silver payal", 499, 0),
    ],
    "Anklets": [
        ("Silver Anklet", "Lightweight", 399, 10),
        ("Beaded Anklet", "Multi-colour", 249, 20),
        ("Gold Anklet", "Gold plated", 599, 0),
        ("Charm Anklet", "With bells", 349, 12),
        ("Adjustable Anklet", "Elastic style", 199, 25),
    ],
    "Jewellery Organizers": [
        ("Velvet Box", "Single necklace box", 299, 8),
        ("Jewellery Tray", "Compartment tray", 499, 5),
        ("Hanging Organizer", "30 pockets", 399, 0),
        ("Travel Pouch", "Roll-up pouch", 249, 15),
        ("Earring Stand", "Wooden stand", 599, 4),
    ],
}

# Generate 3 placeholder image URLs per product
def generate_images(product_name):
    base = "https://via.placeholder.com/400x400.png?text="
    return [
        f"{base}{product_name}+Angle1",
        f"{base}{product_name}+Angle2",
        f"{base}{product_name}+Angle3"
    ]

with app.app_context():
    db.drop_all()
    db.create_all()

    for cat_name in categories_list:
        cat = Category(name=cat_name)
        db.session.add(cat)
        db.session.flush()
        for prod in products_data[cat_name]:
            name, desc, price, stock = prod
            p = Product(name=name, description=desc, price=price, stock=stock, category_id=cat.id)
            db.session.add(p)
            db.session.flush()
            # add 3 images
            for url in generate_images(name):
                img = ProductImage(url=url, alt_text=name, product_id=p.id)
                db.session.add(img)

    db.session.commit()
    print("Database seeded with 3 images per product!")
