# # # # # if __name__=='__main__':
# # # # #     print("hello fast api ")
# # # # # from fastapi import FastAPI

# # # # # app=FastAPI()

# # # # # @app.get("/")
# # # # # def read_root():
# # # # #     return {"Hello api "}
   
# # # # from fastapi import FastAPI
# # # # from pydantic import BaseModel
# # # # from typing import Optional
# # # # app=FastAPI()
# # # # class Item(BaseModel):
# # # #     name:str
# # # #     price:str
# # # #     tax:Optional[float]=None


# # # # @app.get("/message")
# # # # async def read_root():
# # # #     return {"message":"hello get api"}
# # # # @app.get("/item/{item_name}")
# # # # async def get_item(item_name:str,q:str|None):
# # # #     return {"item_name":item_name,"q":q}
    
# # # # @app.get("/item/")
# # # # async def all_item(skip:int=1,limit:int=10):
# # # #     dummy_data=[
# # # #         {"name":"lapi","price":100},
# # # #         {"name":"lapi","price":100,"tax":10.10},
# # # #         {"name":"lapi","price":200},
# # # #     ]
# # # #     dummy_data= dummy_data[skip:skip+limit]
# # # #     return Item(**dummy_data)


# # # # days4 
# # # from fastapi import FastAPI
# # # from typing import Annotated
# # # from pydantic import BaseModel, StringConstraints,validate_call, validate_call, ValidationError ,StringConstraints,Field

# # # app=FastAPI()


# # # class Item(BaseModel):
# # #     name:str=Field(...,min_length=3,max_length=50)
# # #     description:str|None=None
# # #     price:float
# # # # @validate_call
# # # # def validate_name(name:Annotated[str, StringConstraints(min_length=3, max_length=50)]):
# # # #     if name=="lapi":
# # # #         raise ValueError("name cannot be lapi")
# # # #     return name

# # # # try:
# # # #     # name=validate_name(name="Ali")
# # # #     product=Item(name="Alis",description="this is a laptop",price=1000)
# # # #     product_without_price=product.model_dump(exclude={"price"})
# # # #     print("Name is Valid and " , product_without_price )
# # # # except ValidationError as e:
# # # #     print(f"name is invalid{e}")
# # # @app.post("/item")
# # # async def create_item(item:Item):
# # #     return item

# # #     # day5


# # from fastapi import FastAPI, HTTPException, Body
# # from pydantic import BaseModel
# # app = FastAPI()
# # # @app.post("/item")
# # # async def create_item(name:str=Body(...,min_length=3,max_length=50), price:float=Body(...,gt=0),description:str|None=Body(None) ,offer:float|None=Body(None,gt=0)):
# # #   item={"name":name,"price":price,"description":description,"offer":offer}
# # #   if description:
# # #     item["description"]=description
# # #   if offer:
# # #     item["offer"]=offer
# # #   return item
# # # ow with hydrid mode with pydantic + body
# # # from typing import Annotated
# # # class Item(BaseModel):
# # #     name:str=Body(...,min_length=3,max_length=50)
# # #     price:float=Body(...,gt=0)
# # #     description:str|None=Body(None) 
  
# # # class offer(BaseModel):
# # #     offer:float=Body(...,gt=0)
# # # @app.post("/item")
# # # async def create_item(item:Item,offer:offer,flower:Annotated[str, Body(...,min_length=3,max_length=50)]):
# # #     return {"item":item,"offer":offer,"flower":flower}



# # # concept of data injection in details
# # from fastapi import FastAPI, Depends, Header, Path, HTTPException, status
# # from typing import Annotated
# # from pydantic import BaseModel

# # app = FastAPI()

# # async def get_db_session():
# #     print("DB session > start")
# #     session = {"data": {1: {"name": "Item one"}, 2: {"name": "Item two"}}}
# #     try:
# #         yield session
# #     finally:
# #         print("DB session < teardown")

# # DBsession = Annotated[dict, Depends(get_db_session)]

# # async def get_user(token: Annotated[str| None, Header()]=None):
# #     print("Checking auth..")
# #     user = {"username": "test_user"}
# #     return user

# # CurrentUser = Annotated[dict, Depends(get_user)]

# # class ItemCreate(BaseModel):
# #     name: str
# #     price: float | None = None

# # @app.post("/item")
# # async def create_item(
# #     item: ItemCreate,
# #     db: DBsession,
# #     user: CurrentUser):
# #     print(f"User {user['username']} creating item")
# #     new_id = max(db["data"].keys() or [0]) + 1
# #     db["data"][new_id] = item.model_dump()
# #     return {"id": new_id, **item.model_dump()}

# # @app.get("/item/{item_id}")
# # async def read_item(
# #     item_id: Annotated[int, Path(ge=1)],
# #     db: DBsession
# #     ):
# #     print("reading Items")
# #     if item_id not in db["data"]:
# #         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail= "Item is not present")
# #     return {"id": item_id, **db["data"][item_id]}            

# # day 6


# # dynamic pydanctice create model 


# from fastapi import FastAPI, Depends, HTTPException, status
# from pydantic import create_model, BaseModel, Field
# from typing import Any, Dict, Type, List, Literal
# from datetime import date

# app = FastAPI()

# # In a real ERP, this comes from your database (e.g., a ProductCategory table)
# CATEGORY_DEFINITIONS = {
#     1: {"name": "Laptop",
#         "fields": {"cpu_type": (str, ...), "ram_gb": (int, ...)}},
#     2: {"name": "T-Shirt",
#         "fields": {"color": (str, ...), "size": (Literal['S','M','L','XL'], ...)}},
#     3: {"name": "Equipment",
#         "fields": {"voltage": (int, 220), "warranty_expires_on": (date, ...)}}
# }

# # create method which can generate dynamic model
# def get_product_model_for_category(category_id: int) -> Type[BaseModel]:
#     """Dependency: Creates a dynamic Pydantic model based on the category."""
#     category = CATEGORY_DEFINITIONS.get(category_id)
#     if not category:
#         raise HTTPException(status_code=404, detail=f"Product category {category_id} not found.")

#     # Base fields common to ALL products
#     base_fields = {
#         'sku': (str, ...),
#         'price': (float, Field(..., gt=0))
#     }
#     # Add category-specific fields
#     all_fields = {**base_fields, **category["fields"]}

#     # Use create_model to build the class
#     ProductModel = create_model(
#         f'Dynamic{category["name"]}Model',
#         **all_fields
#     )
#     return ProductModel

# # post request
# @app.post("/products/{category_id}")
# async def create_dynamic_product(
#         category_id: int,
#         request_body: Dict[str, Any]
# ):
#     Model = get_product_model_for_category(category_id)
#     try:
#         validate_product = Model(**request_body)
#     except Exception as error:
#         raise HTTPException(status_code=422, detail=error)
#     return {
#         "message" : "Product created successfully",
#         "product": validate_product.model_dump()
#         }

# PRODUCT_DATABASE = {
#     101: {"category_id": 1, "sku": "DELL-XPS-15", "price": 1899.99, "attributes": {"cpu_type": "Intel i9", "ram_gb": 32}},
#     202: {"category_id": 2, "sku": "PLAIN-WHITE-T", "price": 15.50, "attributes": {"color": "White", "size": "L"}},
#     303: {"category_id": 3, "sku": "CNC-MILL-01", "price": 75000.00, "attributes": {"voltage": 220, "warranty_expires_on": "2027-12-31"}}
# }

# @app.get("/products/{product_id}")
# async def get_product(product_id):
#     product_data = PRODUCT_DATABASE[int(product_id)]
#     if not product_data:
#         raise HTTPException(status_code=404, detail="Product does not exist")
#     category_id = product_data["category_id"]
#     ResponseModel = get_product_model_for_category(category_id)
#     response_data = {
#         "sku": product_data["sku"],
#         "price": product_data["price"],
#         **product_data["attributes"]
#     }
#     try:
#         return ResponseModel(**response_data)
#     except Exception as error:
#         raise HTTPException(status_code=422, detail=f"{error}")

# @app.get("/products", response_model=List[Dict[str, Any]])
# async def get_all_products():
#     """
#     Retrieves all products from the database.
#     Note: This endpoint returns the raw database entries without dynamic validation.
#     """
#     return list(PRODUCT_DATABASE.values())








# day 7








