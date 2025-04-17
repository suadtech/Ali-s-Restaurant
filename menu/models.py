from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# Create your models here.
class Category(models.Model):
    """Model representing a menu category"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    order = models.IntegerField(default=0)  # For controlling display order
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['order', 'name']

class MenuItem(models.Model):
    """Model representing a menu item"""
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=8, decimal_places=2, validators=[MinValueValidator(0.01)])
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='menu_items')
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    is_vegetarian = models.BooleanField(default=False)
    is_vegan = models.BooleanField(default=False)
    is_gluten_free = models.BooleanField(default=False)
    spice_level = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(5)],
        help_text="Spice level from 0 (not spicy) to 5 (very spicy)"
    )
    is_available = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['category', 'name']
        indexes = [
            models.Index(fields=['category', 'is_available']),
            models.Index(fields=['is_featured']),
        ]

class Allergen(models.Model):
    """Model representing food allergens"""
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']

class MenuItemAllergen(models.Model):
    """Model representing the many-to-many relationship between menu items and allergens"""
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE, related_name='allergens')
    allergen = models.ForeignKey(Allergen, on_delete=models.CASCADE, related_name='menu_items')
    
    def __str__(self):
        return f"{self.menu_item.name} - {self.allergen.name}"
    
    class Meta:
        unique_together = ('menu_item', 'allergen')
