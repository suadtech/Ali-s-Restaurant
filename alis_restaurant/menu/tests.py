from django.test import TestCase
from django.contrib.auth.models import User
from menu.models import Category, MenuItem, Allergen, MenuItemAllergen

# Create your tests here.
class CategoryModelTest(TestCase):
    """Test cases for the Category model"""
    
    def setUp(self):
        """Set up test data"""
        Category.objects.create(name="Appetizers", description="Starters and small plates", order=1, is_active=True)
        Category.objects.create(name="Main Courses", description="Main dishes", order=2, is_active=True)
        Category.objects.create(name="Desserts", description="Sweet treats", order=3, is_active=False)
    
    def test_category_creation(self):
        """Test that categories are created correctly"""
        appetizers = Category.objects.get(name="Appetizers")
        main_courses = Category.objects.get(name="Main Courses")
        desserts = Category.objects.get(name="Desserts")
        
        self.assertEqual(appetizers.order, 1)
        self.assertTrue(appetizers.is_active)
        
        self.assertEqual(main_courses.order, 2)
        self.assertTrue(main_courses.is_active)
        
        self.assertEqual(desserts.order, 3)
        self.assertFalse(desserts.is_active)
    
    def test_category_string_representation(self):
        """Test the string representation of Category objects"""
        category = Category.objects.get(name="Appetizers")
        self.assertEqual(str(category), "Appetizers")

class MenuItemModelTest(TestCase):
    """Test cases for the MenuItem model"""
    
    def setUp(self):
        """Set up test data"""
        # Create categories
        self.appetizers = Category.objects.create(name="Appetizers", description="Starters and small plates", order=1)
        self.main_courses = Category.objects.create(name="Main Courses", description="Main dishes", order=2)
        
        # Create menu items
        self.item1 = MenuItem.objects.create(
            name="Bruschetta",
            description="Toasted bread with tomatoes, garlic, and basil",
            price=8.99,
            category=self.appetizers,
            is_vegetarian=True,
            is_vegan=True,
            is_gluten_free=False,
            spice_level=0,
            is_available=True,
            is_featured=True
        )
        
        self.item2 = MenuItem.objects.create(
            name="Spicy Chicken Curry",
            description="Tender chicken in a spicy curry sauce",
            price=15.99,
            category=self.main_courses,
            is_vegetarian=False,
            is_vegan=False,
            is_gluten_free=True,
            spice_level=3,
            is_available=True,
            is_featured=False
        )
    
    def test_menu_item_creation(self):
        """Test that menu items are created correctly"""
        bruschetta = MenuItem.objects.get(name="Bruschetta")
        chicken_curry = MenuItem.objects.get(name="Spicy Chicken Curry")
        
        self.assertEqual(bruschetta.price, 8.99)
        self.assertEqual(bruschetta.category, self.appetizers)
        self.assertTrue(bruschetta.is_vegetarian)
        self.assertTrue(bruschetta.is_vegan)
        self.assertFalse(bruschetta.is_gluten_free)
        self.assertEqual(bruschetta.spice_level, 0)
        self.assertTrue(bruschetta.is_featured)
        
        self.assertEqual(chicken_curry.price, 15.99)
        self.assertEqual(chicken_curry.category, self.main_courses)
        self.assertFalse(chicken_curry.is_vegetarian)
        self.assertTrue(chicken_curry.is_gluten_free)
        self.assertEqual(chicken_curry.spice_level, 3)
        self.assertFalse(chicken_curry.is_featured)
    
    def test_menu_item_string_representation(self):
        """Test the string representation of MenuItem objects"""
        item = MenuItem.objects.get(name="Bruschetta")
        self.assertEqual(str(item), "Bruschetta")

class AllergenModelTest(TestCase):
    """Test cases for the Allergen model"""
    
    def setUp(self):
        """Set up test data"""
        Allergen.objects.create(name="Gluten", description="Found in wheat and related grains")
        Allergen.objects.create(name="Nuts", description="Tree nuts and peanuts")
        Allergen.objects.create(name="Dairy", description="Milk and milk products")
    
    def test_allergen_creation(self):
        """Test that allergens are created correctly"""
        gluten = Allergen.objects.get(name="Gluten")
        nuts = Allergen.objects.get(name="Nuts")
        dairy = Allergen.objects.get(name="Dairy")
        
        self.assertEqual(gluten.description, "Found in wheat and related grains")
        self.assertEqual(nuts.description, "Tree nuts and peanuts")
        self.assertEqual(dairy.description, "Milk and milk products")
    
    def test_allergen_string_representation(self):
        """Test the string representation of Allergen objects"""
        allergen = Allergen.objects.get(name="Gluten")
        self.assertEqual(str(allergen), "Gluten")

class MenuItemAllergenTest(TestCase):
    """Test cases for the MenuItemAllergen model"""
    
    def setUp(self):
        """Set up test data"""
        # Create category
        self.category = Category.objects.create(name="Desserts", description="Sweet treats", order=3)
        
        # Create menu item
        self.item = MenuItem.objects.create(
            name="Chocolate Cake",
            description="Rich chocolate cake with frosting",
            price=6.99,
            category=self.category,
            is_vegetarian=True,
            is_vegan=False,
            is_gluten_free=False,
            spice_level=0,
            is_available=True
        )
        
        # Create allergens
        self.gluten = Allergen.objects.create(name="Gluten", description="Found in wheat and related grains")
        self.dairy = Allergen.objects.create(name="Dairy", description="Milk and milk products")
        
        # Create menu item allergen relationships
        self.item_allergen1 = MenuItemAllergen.objects.create(menu_item=self.item, allergen=self.gluten)
        self.item_allergen2 = MenuItemAllergen.objects.create(menu_item=self.item, allergen=self.dairy)
    
    def test_menu_item_allergen_creation(self):
        """Test that menu item allergen relationships are created correctly"""
        allergens = MenuItemAllergen.objects.filter(menu_item=self.item)
        
        self.assertEqual(allergens.count(), 2)
        self.assertTrue(allergens.filter(allergen=self.gluten).exists())
        self.assertTrue(allergens.filter(allergen=self.dairy).exists())
    
    def test_menu_item_allergen_string_representation(self):
        """Test the string representation of MenuItemAllergen objects"""
        item_allergen = MenuItemAllergen.objects.get(menu_item=self.item, allergen=self.gluten)
        expected = f"{self.item.name} - {self.gluten.name}"
        self.assertEqual(str(item_allergen), expected)
