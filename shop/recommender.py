import redis
from django.conf import settings
from .models import Product

redis = redis.StrictRedis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, db=settings.REDIS_DB)


class Recommender(object):
    def clear_purchases(self):
        for id in Product.objects.values_list('id', flat=True):
            redis.delete(self.get_product_key(id))

    def get_product_key(self, product_id):
        return 'product:{}:purchased_with'.format(product_id)

    def product_bought(self, products):
        product_ids = [product.id for product in products]
        for product_id in product_ids:
            for with_id in product_ids:
                if product_id != with_id:
                    redis.zincrby(self.get_product_key(product_id), value=with_id, amount=1)

    def suggest_product_for(self, products, max_results=6):
        product_ids = [product.id for product in products]
        if len(products) == 1:
            suggestions = redis.zrange(self.get_product_key(product_ids[0]), 0, -1, desc=True)[:max_results]
        else:
            flat_ids = ''.join([str(id) for id in product_ids])
            tmp_key = 'tmp_{}'.format(flat_ids)
            keys = [self.get_product_key(id) for id in product_ids]
            redis.zunionstore(tmp_key, keys)
            redis.zrem(tmp_key, *product_ids)
            suggestions = redis.zrange(tmp_key, 0, -1, desc=True)[:max_results]
            redis.delete(tmp_key)
        suggested_product_ids = [int(id) for id in suggestions]
        suggested_products = list(Product.objects.filter(id__in=suggested_product_ids))
        suggested_products.sort(key=lambda x: suggested_product_ids.index(x.id))
        return suggested_products
