# logistics_client.OrdersApi

All URIs are relative to *http://localhost:8080/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**create_order**](OrdersApi.md#create_order) | **POST** /orders | Create a new order
[**delete_order**](OrdersApi.md#delete_order) | **DELETE** /orders/{orderId} | Delete an order
[**get_order**](OrdersApi.md#get_order) | **GET** /orders/{orderId} | Get order by ID
[**list_orders**](OrdersApi.md#list_orders) | **GET** /orders | List orders with pagination
[**update_order**](OrdersApi.md#update_order) | **PUT** /orders/{orderId} | Update an existing order


# **create_order**
> Order create_order(create_order_request)

Create a new order

### Example


```python
import logistics_client
from logistics_client.models.create_order_request import CreateOrderRequest
from logistics_client.models.order import Order
from logistics_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = logistics_client.Configuration(
    host = "http://localhost:8080/api/v1"
)


# Enter a context with an instance of the API client
with logistics_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logistics_client.OrdersApi(api_client)
    create_order_request = logistics_client.CreateOrderRequest() # CreateOrderRequest | 

    try:
        # Create a new order
        api_response = api_instance.create_order(create_order_request)
        print("The response of OrdersApi->create_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->create_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **create_order_request** | [**CreateOrderRequest**](CreateOrderRequest.md)|  | 

### Return type

[**Order**](Order.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**201** | Order created |  -  |
**400** | Invalid request |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **delete_order**
> delete_order(order_id)

Delete an order

### Example


```python
import logistics_client
from logistics_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = logistics_client.Configuration(
    host = "http://localhost:8080/api/v1"
)


# Enter a context with an instance of the API client
with logistics_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logistics_client.OrdersApi(api_client)
    order_id = 'order_id_example' # str | 

    try:
        # Delete an order
        api_instance.delete_order(order_id)
    except Exception as e:
        print("Exception when calling OrdersApi->delete_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**|  | 

### Return type

void (empty response body)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**204** | Order deleted |  -  |
**404** | Order not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **get_order**
> Order get_order(order_id)

Get order by ID

### Example


```python
import logistics_client
from logistics_client.models.order import Order
from logistics_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = logistics_client.Configuration(
    host = "http://localhost:8080/api/v1"
)


# Enter a context with an instance of the API client
with logistics_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logistics_client.OrdersApi(api_client)
    order_id = 'order_id_example' # str | 

    try:
        # Get order by ID
        api_response = api_instance.get_order(order_id)
        print("The response of OrdersApi->get_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->get_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**|  | 

### Return type

[**Order**](Order.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Order found |  -  |
**404** | Order not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_orders**
> OrderList list_orders(limit=limit, offset=offset)

List orders with pagination

### Example


```python
import logistics_client
from logistics_client.models.order_list import OrderList
from logistics_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = logistics_client.Configuration(
    host = "http://localhost:8080/api/v1"
)


# Enter a context with an instance of the API client
with logistics_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logistics_client.OrdersApi(api_client)
    limit = 20 # int |  (optional) (default to 20)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List orders with pagination
        api_response = api_instance.list_orders(limit=limit, offset=offset)
        print("The response of OrdersApi->list_orders:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->list_orders: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 20]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

[**OrderList**](OrderList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of orders |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_order**
> Order update_order(order_id, update_order_request)

Update an existing order

### Example


```python
import logistics_client
from logistics_client.models.order import Order
from logistics_client.models.update_order_request import UpdateOrderRequest
from logistics_client.rest import ApiException
from pprint import pprint

# Defining the host is optional and defaults to http://localhost:8080/api/v1
# See configuration.py for a list of all supported configuration parameters.
configuration = logistics_client.Configuration(
    host = "http://localhost:8080/api/v1"
)


# Enter a context with an instance of the API client
with logistics_client.ApiClient(configuration) as api_client:
    # Create an instance of the API class
    api_instance = logistics_client.OrdersApi(api_client)
    order_id = 'order_id_example' # str | 
    update_order_request = logistics_client.UpdateOrderRequest() # UpdateOrderRequest | 

    try:
        # Update an existing order
        api_response = api_instance.update_order(order_id, update_order_request)
        print("The response of OrdersApi->update_order:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling OrdersApi->update_order: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **order_id** | **str**|  | 
 **update_order_request** | [**UpdateOrderRequest**](UpdateOrderRequest.md)|  | 

### Return type

[**Order**](Order.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Order updated |  -  |
**404** | Order not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

