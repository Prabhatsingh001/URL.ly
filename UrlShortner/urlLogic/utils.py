import uuid

BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class SlugGenerator:
    def uuid_to_number(self, id):
        # f6f4d690-fd2d-445b-bf9d-14f1726f6ccc
        return id.int

    def encode_url(self, id):
        id = self.uuid_to_number(id)
        if id == 0:
            return BASE62[0]
        result = ""
        while id > 0:
            result = (BASE62[id % 62]) + result
            id //= 62

        return result

    def decode_url(self, slug: str):
        id = 0
        for char in slug:
            id = id * 62 + BASE62.index(char)
        return uuid.UUID(int=id)


class QrCode:
    def generate_qr_code(self, short_url):
        pass

    def download_qr_code(self, qr_code):
        pass

    def get_qr_code(self):
        pass

    def delete_qr_code(self):
        pass
