import graphene
import requests

# Define UserType, ProductType, OrderType, etc.
class UserType(graphene.ObjectType):
    username = graphene.String()
    email = graphene.String()
    # Do not expose the password in the UserType

# Product Type without id
class ProductType(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()
    price = graphene.Float()
    stock = graphene.Int()

# Order Item Type
class ProductDetailsType(graphene.ObjectType):
    name = graphene.String()
    description = graphene.String()

# Modify Order Item Type to include product_details
class OrderItemType(graphene.ObjectType):
    product_id = graphene.ID()
    quantity = graphene.Int()
    price = graphene.Float()
    product_details = graphene.Field(ProductDetailsType)  # Add this field

# Define Order Type
class OrderType(graphene.ObjectType):
    id = graphene.ID()  # Add the ID field
    user_id = graphene.ID()
    created_at = graphene.String()
    updated_at = graphene.String()
    status = graphene.String()
    total = graphene.Float()  # Include total if needed
    items = graphene.List(OrderItemType)  # Ensure items are defined correctly

# Input Types
class RegisterInput(graphene.InputObjectType):
    username = graphene.String(required=True)
    email = graphene.String(required=True)
    password = graphene.String(required=True)

class ProductInput(graphene.InputObjectType):
    name = graphene.String(required=True)
    description = graphene.String(required=True)
    price = graphene.Float(required=True)
    stock = graphene.Int(required=True)

class OrderItemInput(graphene.InputObjectType):
    product_id = graphene.ID(required=True)
    quantity = graphene.Int(required=True)

class OrderInput(graphene.InputObjectType):
    user_id = graphene.ID(required=True)
    items = graphene.List(OrderItemInput, required=True)  # Input should use InputObjectType

class Query(graphene.ObjectType):
    users = graphene.List(UserType)
    user = graphene.Field(UserType, id=graphene.ID(required=True))
    products = graphene.List(ProductType, token=graphene.String(required=True))
    product = graphene.Field(ProductType, id=graphene.ID(required=True), token=graphene.String(required=True))
    orders = graphene.List(OrderType, token=graphene.String(required=True))
    order = graphene.Field(OrderType, id=graphene.ID(required=True), token=graphene.String(required=True))

    def resolve_users(self, info):
        response = requests.get('http://127.0.0.1:8000/api/user/')
        if response.status_code == 200:
            return [UserType(**user) for user in response.json()]
        return []

    def resolve_user(self, info, id):
        response = requests.get(f'http://127.0.0.1:8000/api/user/{id}/')
        if response.status_code == 200:
            return UserType(**response.json())
        return None

    def resolve_products(self, info, token):
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get('http://127.0.0.1:8000/api/products/', headers=headers)
        if response.status_code == 200:
            # Explicitly construct ProductType without the 'id' field
            return [
                ProductType(
                    name=product['name'],
                    description=product['description'],
                    price=product['price'],
                    stock=product['stock']
                )
                for product in response.json()
            ]
        return []

    def resolve_product(self, info, id, token):
        headers = {
        "Authorization": f"Bearer {token}"
    }
        response = requests.get(f'http://127.0.0.1:8000/api/products/{id}/', headers=headers)
        if response.status_code == 200:
            return ProductType(
                    name=response.json().get('name'),
                    description=response.json().get('description'),
                    price=response.json().get('price'),
                    stock=response.json().get('stock')
                )  # Return a single ProductType instance
        return None 

    def resolve_orders(self, info, token):
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get('http://127.0.0.1:8000/api/orders/', headers=headers)
        if response.status_code == 200:
            return [OrderType(**order) for order in response.json()]
        return []

    def resolve_order(self, info, id, token):

        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.get(f'http://127.0.0.1:8000/api/orders/{id}/', headers=headers)
        if response.status_code == 200:
            order_data = response.json()

        # Extracting order items
            order_items = [
                OrderItemType(
                    product_id=item.get('product_id'),
                    quantity=item.get('quantity'),
                    price=float(item.get('price')),  # Ensure price is a float
                    product_details=ProductDetailsType(
                        name=item['product_details'].get('name'),
                        description=item['product_details'].get('description')
                    )
                )
                for item in order_data.get('items', [])
            ]

            # Return the OrderType instance
            return OrderType(
                    id=order_data.get('id'),  # Set ID from response
                    user_id=order_data.get('user_id'),
                    created_at=order_data.get('created_at'),
                    updated_at=order_data.get('updated_at'),
                    status=order_data.get('status'),
                    total=order_data.get('total'),
                    items=order_items,
                )
      # Handle error case
        return None 

class Mutation(graphene.ObjectType):
    register_user = graphene.Field(UserType, input=RegisterInput(required=True))
    create_product = graphene.Field(ProductType, input=ProductInput(required=True), token=graphene.String(required=True))
    place_order = graphene.Field(OrderType, input=OrderInput(required=True), token=graphene.String(required=True))

    def resolve_register_user(self, info, input):
        response = requests.post('http://127.0.0.1:8000/api/user/signup/', json=input)
        if response.status_code == 201:
            return UserType(**response.json())
        return None

    def resolve_create_product(self, info, input, token):
        headers = {
            "Authorization": f"Bearer {token}"
        }
        response = requests.post('http://127.0.0.1:8000/api/products/', json={
            'name': input.name,
            'description': input.description,
            'price': input.price,
            'stock': input.stock
        }, headers=headers)

        if response.status_code == 201:
            return ProductType(**response.json())
        else:
            raise Exception(response.json().get('detail', 'Product creation failed'))

    def resolve_place_order(self, info, input, token):
        order_items = [{"product_id": item.product_id, "quantity": item.quantity} for item in input.items]
        input_dict = {**input, "items": order_items}
        
        headers = {
            "Authorization": f"Bearer {token}"
        }
        
        response = requests.post('http://127.0.0.1:8000/api/orders/', json=input_dict, headers=headers)
        if response.status_code == 201:
            return OrderType(**response.json())
        return None

schema = graphene.Schema(query=Query, mutation=Mutation)
