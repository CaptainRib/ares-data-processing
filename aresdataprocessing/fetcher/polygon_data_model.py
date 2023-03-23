class Trade(object):
    def __init__(self, symbol, timestamp, price, quantity):
        self._symbol = symbol
        self._timestamp = timestamp
        self._price = price
        self._quantity = quantity

    def to_dict(self):
        return {
            'symbol': self._symbol,
            'timestamp': self._timestamp,
            'price': self._price,
            'quantity': self._quantity
        }

    @property
    def symbol(self):
        return self._symbol
    
    @property
    def timestamp(self):
        return self._timestamp
    
    @property
    def price(self):
        return self._price
    
    @property
    def quantity(self):
        return self._quantity
    