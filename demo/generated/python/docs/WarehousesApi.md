# logistics_client.WarehousesApi

All URIs are relative to *http://localhost:8080/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_warehouse**](WarehousesApi.md#get_warehouse) | **GET** /warehouses/{warehouseId} | Get warehouse by ID
[**list_warehouses**](WarehousesApi.md#list_warehouses) | **GET** /warehouses | List warehouses with pagination
[**update_inventory**](WarehousesApi.md#update_inventory) | **PATCH** /warehouses/{warehouseId}/inventory/{sku} | Update inventory for a specific SKU in a warehouse


# **get_warehouse**
> Warehouse get_warehouse(warehouse_id)

Get warehouse by ID

### Example


```python
import logistics_client
from logistics_client.models.warehouse import Warehouse
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
    api_instance = logistics_client.WarehousesApi(api_client)
    warehouse_id = 'warehouse_id_example' # str | 

    try:
        # Get warehouse by ID
        api_response = api_instance.get_warehouse(warehouse_id)
        print("The response of WarehousesApi->get_warehouse:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WarehousesApi->get_warehouse: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **warehouse_id** | **str**|  | 

### Return type

[**Warehouse**](Warehouse.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Warehouse found |  -  |
**404** | Warehouse not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_warehouses**
> WarehouseList list_warehouses(limit=limit, offset=offset)

List warehouses with pagination

### Example


```python
import logistics_client
from logistics_client.models.warehouse_list import WarehouseList
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
    api_instance = logistics_client.WarehousesApi(api_client)
    limit = 20 # int |  (optional) (default to 20)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List warehouses with pagination
        api_response = api_instance.list_warehouses(limit=limit, offset=offset)
        print("The response of WarehousesApi->list_warehouses:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WarehousesApi->list_warehouses: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 20]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

[**WarehouseList**](WarehouseList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of warehouses |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **update_inventory**
> InventoryItem update_inventory(warehouse_id, sku, update_inventory_request)

Update inventory for a specific SKU in a warehouse

### Example


```python
import logistics_client
from logistics_client.models.inventory_item import InventoryItem
from logistics_client.models.update_inventory_request import UpdateInventoryRequest
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
    api_instance = logistics_client.WarehousesApi(api_client)
    warehouse_id = 'warehouse_id_example' # str | 
    sku = 'sku_example' # str | 
    update_inventory_request = logistics_client.UpdateInventoryRequest() # UpdateInventoryRequest | 

    try:
        # Update inventory for a specific SKU in a warehouse
        api_response = api_instance.update_inventory(warehouse_id, sku, update_inventory_request)
        print("The response of WarehousesApi->update_inventory:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling WarehousesApi->update_inventory: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **warehouse_id** | **str**|  | 
 **sku** | **str**|  | 
 **update_inventory_request** | [**UpdateInventoryRequest**](UpdateInventoryRequest.md)|  | 

### Return type

[**InventoryItem**](InventoryItem.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: application/json
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Inventory updated |  -  |
**404** | Warehouse or SKU not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

