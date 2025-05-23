BASE62 = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"


class SlugGenerator:
    def encode_url(self, id: int):
        if id == 0:
            return BASE62[0]
        result = []
        while id > 0:
            result.append(BASE62[id % 62])
            id //= 62

        return "".join(reversed(result))

    def decode_url(self, slug: str):
        id = 0
        for char in slug:
            id = id * 62 + BASE62.index(char)
        return id
