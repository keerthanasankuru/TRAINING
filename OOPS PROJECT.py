from abc import ABC, abstractmethod


class Users(ABC):
    def __init__(self, id, name, email, phone):
        self.id = id
        self.name = name
        self.email = email
        self.phone = phone

    @abstractmethod
    def login(self):
        pass


class Customer(Users):
    def __init__(self, id, name, email, phone):
        super().__init__(id, name, email, phone)
        self.cart = []

    def login(self):
        print(f"Customer {self.name} Login Successful")

    def add_to_cart(self, restaurant, item_id, quantity):
        item = restaurant.find_item(item_id)
        if item is None:
            print("Item not found in menu")
            return
        if not item.isAvailable:
            print("Item is not available")
            return
        if quantity <= 0:
            print("Invalid quantity")
            return
        self.cart.append(OrderItem(item, quantity))
        print(item.name, "added to cart")

    def remove_from_cart(self, item_id):
        for order_item in self.cart:
            if order_item.food_item.itemId == item_id:
                self.cart.remove(order_item)
                print("Item removed from cart")
                return
        print("Item not found in cart")

    def display_cart(self):
        for order_item in self.cart:
            print(order_item.food_item.name, "-", order_item.quantity, "x", order_item.food_item.price)


class RestaurantOwner(Users):
    def __init__(self, id, name, email, phone):
        super().__init__(id, name, email, phone)

    def login(self):
        print(f"Restaurant Owner {self.name} Login Successful")

    def add_food_item(self, restaurant, food_item):
        restaurant.add_food_item(food_item)

    def remove_food_item(self, restaurant, item_id):
        restaurant.remove_food_item(item_id)

    def update_food_item(self, restaurant, item_id, name=None, price=None, category=None):
        restaurant.update_food_item(item_id, name, price, category)

    def update_stock(self, restaurant, item_id, quantity):
        restaurant.update_stock(item_id, quantity)


class DeliveryChargeStrategy(ABC):
    @abstractmethod
    def calculate(self, distance_km):
        pass


class BikeCharge(DeliveryChargeStrategy):
    def calculate(self, distance_km):
        return 20 + distance_km * 5


class ScooterCharge(DeliveryChargeStrategy):
    def calculate(self, distance_km):
        return 15 + distance_km * 4


class CycleCharge(DeliveryChargeStrategy):
    def calculate(self, distance_km):
        return 10 + distance_km * 2


VEHICLE_CHARGE_STRATEGIES = {
    "Bike": BikeCharge(),
    "Scooter": ScooterCharge(),
    "Cycle": CycleCharge(),
}


class DeliveryPartner(Users):
    def __init__(self, id, name, email, phone, vehicle):
        super().__init__(id, name, email, phone)
        self.vehicle = vehicle
        self._availability_status = True
        self._current_order = None

    @property
    def availability_status(self):
        return self._availability_status

    @property
    def current_order(self):
        return self._current_order

    def login(self):
        print(f"Delivery Partner {self.name} Login Successful")

    def calculate_delivery_charge(self, distance_km):
        strategy = VEHICLE_CHARGE_STRATEGIES.get(self.vehicle, BikeCharge())
        return strategy.calculate(distance_km)

    def accept_order(self, order):
        if not self._availability_status:
            print(f"{self.name} is not available")
            return
        self._current_order = order
        self._availability_status = False
        order.assign_delivery_partner(self)
        print("Order accepted by", self.name)

    def complete_delivery(self):
        if self._current_order:
            self._current_order.update_status(OrderStatus.DELIVERED)
            self._current_order = None
            self._availability_status = True


class Admin(Users):
    def __init__(self, id, name, email, phone):
        super().__init__(id, name, email, phone)

    def login(self):
        print(f"Admin {self.name} Login Successful")


class FoodItem:
    def __init__(self, itemId, name, price, category, quantity):
        self.itemId = itemId
        self.name = name
        self.price = price
        self.category = category
        self.quantity = quantity

    @property
    def isAvailable(self):
        return self.quantity > 0


class OrderItem:
    def __init__(self, food_item, quantity):
        self.food_item = food_item
        self.quantity = quantity

    @property
    def line_total(self):
        return self.food_item.price * self.quantity


class Restaurant:
    def __init__(self, restaurantid, name, location, owner, cuisine="General"):
        self.restaurantid = restaurantid
        self.name = name
        self.location = location
        self.cuisine = cuisine
        self.owner = owner
        self.menu = []

    def find_item(self, item_id):
        for item in self.menu:
            if item.itemId == item_id:
                return item
        return None

    def add_food_item(self, food_item):
        self.menu.append(food_item)

    def remove_food_item(self, item_id):
        item = self.find_item(item_id)
        if item:
            self.menu.remove(item)

    def update_food_item(self, item_id, name=None, price=None, category=None):
        item = self.find_item(item_id)
        if not item:
            return
        if name is not None:
            item.name = name
        if price is not None:
            item.price = price
        if category is not None:
            item.category = category

    def update_stock(self, item_id, quantity):
        item = self.find_item(item_id)
        if item:
            item.quantity = max(0, item.quantity + quantity)

    def display_menu(self):
        for item in self.menu:
            print(item.itemId, item.name, "-", item.price, "-", item.quantity, "available")


class RestaurantDirectory:
    def __init__(self, restaurants):
        self.restaurants = restaurants

    def search_restaurant(self, name, location=None, cuisine=None):
        results = [r for r in self.restaurants if name.lower() in r.name.lower()]
        if location is not None:
            results = [r for r in results if r.location.lower() == location.lower()]
        if cuisine is not None:
            results = [r for r in results if r.cuisine.lower() == cuisine.lower()]
        return results


class OrderStatus:
    PLACED = "PLACED"
    CONFIRMED = "CONFIRMED"
    PREPARING = "PREPARING"
    OUT_FOR_DELIVERY = "OUT_FOR_DELIVERY"
    DELIVERED = "DELIVERED"
    CANCELLED = "CANCELLED"
    _FLOW = [PLACED, CONFIRMED, PREPARING, OUT_FOR_DELIVERY, DELIVERED]


class Discount(ABC):
    @abstractmethod
    def apply_discount(self, amount):
        pass


class PercentageDiscount(Discount):
    def __init__(self, percentage):
        self.percentage = percentage

    def apply_discount(self, amount):
        return amount - (amount * self.percentage / 100)


class FlatDiscount(Discount):
    def __init__(self, amount):
        self.amount = amount

    def apply_discount(self, amount):
        return max(0, amount - self.amount)


class NoDiscount(Discount):
    def apply_discount(self, amount):
        return amount


class Orders:
    def __init__(self, orderid, customer, restaurant, delivery_charge, tax, discount):
        self.orderid = orderid
        self.customer = customer
        self.restaurant = restaurant
        self.items = list(customer.cart)
        self.delivery_charge = delivery_charge
        self.tax = tax
        self.discount = discount
        self._total_amount = 0
        self._order_status = OrderStatus.PLACED
        self._delivery_partner = None

    @property
    def totalAmount(self):
        return self._total_amount

    @property
    def order_status(self):
        return self._order_status

    @property
    def delivery_partner(self):
        return self._delivery_partner

    def assign_delivery_partner(self, partner):
        self._delivery_partner = partner

    def calculate_total(self):
        item_total = 0
        for order_item in self.items:
            food_item = order_item.food_item
            if food_item.quantity < order_item.quantity:
                raise ValueError(f"Not enough stock for {food_item.name}")
            item_total += order_item.line_total

        discounted_total = self.discount.apply_discount(item_total)
        self._total_amount = discounted_total + self.delivery_charge + self.tax
        return self._total_amount

    def update_status(self, status):
        current_idx = OrderStatus._FLOW.index(self._order_status) if self._order_status in OrderStatus._FLOW else -1
        new_idx = OrderStatus._FLOW.index(status) if status in OrderStatus._FLOW else -1
        if status == OrderStatus.CANCELLED:
            self._order_status = status
            return
        if new_idx != -1 and new_idx < current_idx:
            raise ValueError(f"Cannot move order status backwards from {self._order_status} to {status}")
        self._order_status = status

    def print_items(self):
        for order_item in self.items:
            print(order_item.food_item.name, "-", order_item.quantity, "x", order_item.food_item.price)

    @property
    def subtotal(self):
        return sum(oi.line_total for oi in self.items)

    @property
    def discount_amount(self):
        return self.subtotal - self.discount.apply_discount(self.subtotal)


class Payments(ABC):
    def __init__(self, totalAmount):
        self.totalAmount = totalAmount
        self.status = "PENDING"

    @abstractmethod
    def pay(self):
        pass

    @abstractmethod
    def refund(self):
        pass

    def label(self):
        return self.__class__.__name__


class CreditCard(Payments):
    def pay(self):
        self.status = "SUCCESS"
        print("Payment through Credit Card successful")

    def refund(self):
        print("Refund through Credit Card successful")


class UPI(Payments):
    def pay(self):
        self.status = "SUCCESS"
        print("Payment through UPI successful")

    def refund(self):
        print("Refund through UPI successful")


class CashOnDelivery(Payments):
    def pay(self):
        self.status = "PENDING"
        print("Cash On Delivery selected")

    def refund(self):
        print("Cash On Delivery refund processed")


class Notification(ABC):
    def __init__(self, order):
        self.order = order

    @abstractmethod
    def notify(self):
        pass


class EmailNotification(Notification):
    def notify(self):
        print(f"Email: Order {self.order.orderid} status is {self.order.order_status}")


class SMSNotification(Notification):
    def notify(self):
        print(f"SMS: Order {self.order.orderid} status is {self.order.order_status}")


class PushNotification(Notification):
    def notify(self):
        print(f"Push Notification: Order {self.order.orderid} status is {self.order.order_status}")


def notify_all(order, channels):
    for channel_cls in channels:
        channel_cls(order).notify()


def print_receipt(order, payment, delivery_partner):
    print("\n===== FOOD DELIVERY SYSTEM =====\n")
    print(f"Customer: {order.customer.name}")
    print(f"Restaurant: {order.restaurant.name}\n")
    print(f"Order #{order.orderid}\n")
    print("Items:")
    for oi in order.items:
        print(f"{oi.food_item.name:<12}₹{oi.food_item.price * oi.quantity}")
    print(f"\nSubtotal:        ₹{order.subtotal}")
    print(f"Discount:        ₹{order.discount_amount:.0f}")
    print(f"Delivery:        ₹{order.delivery_charge}")
    print(f"Tax:             ₹{order.tax}")
    print(f"\nFinal Amount:    ₹{order.totalAmount:.0f}")
    print(f"\nPayment Method: {payment.label()}")
    print(f"Payment Status: {payment.status}")
    print(f"\nOrder Status: {order.order_status}")
    print(f"\nDelivery Partner: {delivery_partner.name}")
    print(f"Vehicle: {delivery_partner.vehicle}")
    print(f"\nNotification: Your order #{order.orderid} has been delivered!")


if __name__ == "__main__":
    c1 = Customer(101, "Rahul", "rahul@gmail.com", "9876543210")
    resowner1 = RestaurantOwner(201, "Priya", "priya@gmail.com", "9123456780")
    d1 = DeliveryPartner(301, "Arjun", "arjun@gmail.com", "9988776655", "Bike")
    a1 = Admin(401, "Anu", "anu@gmail.com", "9000000000")

    r1 = Restaurant(501, "Pizza Palace", "Hyderabad", resowner1, cuisine="Italian")

    pizza = FoodItem(1, "Pizza", 400, "Italian", 10)
    burger = FoodItem(2, "Burger", 200, "Fast Food", 15)
    coke = FoodItem(3, "Coke", 80, "Beverages", 20)

    resowner1.add_food_item(r1, pizza)
    resowner1.add_food_item(r1, burger)
    resowner1.add_food_item(r1, coke)

    c1.login()

    directory = RestaurantDirectory([r1])
    print("\nSearch 'Pizza':", [r.name for r in directory.search_restaurant("Pizza")])
    print("Search 'Pizza', 'Hyderabad':", [r.name for r in directory.search_restaurant("Pizza", "Hyderabad")])
    print("Search 'Pizza', 'Hyderabad', 'Italian':",
          [r.name for r in directory.search_restaurant("Pizza", "Hyderabad", "Italian")])

    print()
    r1.display_menu()

    print()
    c1.add_to_cart(r1, 1, 2)
    c1.add_to_cart(r1, 2, 1)

    discount = PercentageDiscount(10)
    delivery_charge = d1.calculate_delivery_charge(distance_km=6)
    order1 = Orders(1001, c1, r1, delivery_charge, 30, discount)
    order1.calculate_total()

    order1.update_status(OrderStatus.CONFIRMED)
    order1.update_status(OrderStatus.PREPARING)

    d1.accept_order(order1)
    order1.update_status(OrderStatus.OUT_FOR_DELIVERY)
    notify_all(order1, [EmailNotification, SMSNotification])

    payment = UPI(order1.totalAmount)
    payment.pay()

    d1.complete_delivery()
    notify_all(order1, [PushNotification])

    print_receipt(order1, payment, d1)