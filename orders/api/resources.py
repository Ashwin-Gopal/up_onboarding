import structlog

from django.urls import path
from tastypie.exceptions import BadRequest
from tastypie.resources import ModelResource

from orders.models import Order
from orders.tasks import process_upstream_order
from utils.generate_order import produce_order

logging = structlog.getLogger('onboarding')


class OrderResource(ModelResource):

    class Meta:
        queryset = Order.objects.all()

    def prepend_urls(self):
        """
        aggregator order processing urls
        :return:
        """
        return [
            path("orders/upstream/", self.wrap_view('process_upstream_order'), name='upstream-order'),
        ]

    def process_upstream_order(self, request, **kwargs):
        """
        Validates aggregator payload and updates system with order details
        :param request:
        :param kwargs:
        :return:
        """
        self.method_check(request, allowed=['post'])
        data = self.deserialize(request, request.body, format=request.META.get(
            'CONTENT_TYPE', 'application/json'))
        data = data if data else produce_order()
        aggregator_id = data.get('aggregatorId')
        aggregator_order_id = data.get('aggregatorOrderId')
        if aggregator_id and aggregator_order_id:
            logging.info("Processing order {id}".format(id=aggregator_order_id))
            process_upstream_order.delay(data)
        else:
            logging.error("Bad Request: Aggregator and aggregator info not sent")
            raise BadRequest("Aggregator and aggregator info not sent")

        return self.create_response(request, {"data": {
            "message": "Your order is getting processed"
        }
        })
