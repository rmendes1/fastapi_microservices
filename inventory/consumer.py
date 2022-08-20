import time

from main import redis, Product

key = 'order_completed'
group = 'inventory-group'

try:
    redis.xgroup_create(key, group)
except:
    print('Group already exists!')

while True:
    try:
        results = redis.xreadgroup(group, key, {key: '>'}, None)  # the dict symbol is to get all the events

        if results:
            for result in results:
                obj = result[1][0][1]

                try:
                    product = Product.get(obj['product_id'])
                    product.quantity = product.quantity - int(obj['quantity'])
                    product.save()

                except:  # if the product is not available, it will be sent an event to refund
                    redis.xadd('refund_order', obj, '*')
    except Exception as e:
        print(str(e))
    time.sleep(1)
