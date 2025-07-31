from django.core.management.base import BaseCommand
from pizza_shop.models import Pizza
from django.contrib.auth.models import User
from decimal import Decimal

class Command(BaseCommand):
    help = 'Loads sample data into the database'

    def handle(self, *args, **kwargs):
        # Create sample pizzas
        pizzas_data = [
            {
                'name': 'Margherita',
                'description': 'Classic Italian pizza with tomato sauce, mozzarella, and basil',
                'price': Decimal('12.99'),
                'size': 'M',
                'is_available': True,
                'toppings': 'Tomato Sauce, Mozzarella, Fresh Basil'
            },
            {
                'name': 'Pepperoni',
                'description': 'Traditional pizza topped with spicy pepperoni slices',
                'price': Decimal('14.99'),
                'size': 'M',
                'is_available': True,
                'toppings': 'Tomato Sauce, Mozzarella, Pepperoni'
            },
            {
                'name': 'Supreme',
                'description': 'Loaded with vegetables and meats',
                'price': Decimal('16.99'),
                'size': 'L',
                'is_available': True,
                'toppings': 'Tomato Sauce, Mozzarella, Pepperoni, Sausage, Bell Peppers, Onions, Olives, Mushrooms'
            },
            {
                'name': 'Vegetarian',
                'description': 'Fresh vegetables on a crispy crust',
                'price': Decimal('13.99'),
                'size': 'M',
                'is_available': True,
                'toppings': 'Tomato Sauce, Mozzarella, Bell Peppers, Onions, Olives, Mushrooms, Tomatoes'
            },
        ]

        for pizza_data in pizzas_data:
            Pizza.objects.get_or_create(**pizza_data)

        self.stdout.write(self.style.SUCCESS('Successfully loaded sample data'))
