class BaseItem:
    def __init__(self, name, id, price):
        name = name
        id = id
        price = price


class GetItem(BaseItem):
    def __init__(self, name, id, price, folder, folder_id, published, media):
        super().__init__(name, id, price)
        folder = folder
        folder_id = folder_id
        published = published
        media = media


class PostItem(BaseItem):
    def __init__(self, name, id, price, quantity):
        super().__init__(name, id, price)
        quantity = quantity
