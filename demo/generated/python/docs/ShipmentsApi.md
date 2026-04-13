# logistics_client.ShipmentsApi

All URIs are relative to *http://localhost:8080/api/v1*

Method | HTTP request | Description
------------- | ------------- | -------------
[**get_shipment**](ShipmentsApi.md#get_shipment) | **GET** /shipments/{shipmentId} | Get shipment by ID
[**list_shipments**](ShipmentsApi.md#list_shipments) | **GET** /shipments | List shipments with pagination
[**track_shipment**](ShipmentsApi.md#track_shipment) | **GET** /shipments/{shipmentId}/track | Get tracking history for a shipment


# **get_shipment**
> Shipment get_shipment(shipment_id)

Get shipment by ID

### Example


```python
import logistics_client
from logistics_client.models.shipment import Shipment
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
    api_instance = logistics_client.ShipmentsApi(api_client)
    shipment_id = 'shipment_id_example' # str | 

    try:
        # Get shipment by ID
        api_response = api_instance.get_shipment(shipment_id)
        print("The response of ShipmentsApi->get_shipment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShipmentsApi->get_shipment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shipment_id** | **str**|  | 

### Return type

[**Shipment**](Shipment.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Shipment found |  -  |
**404** | Shipment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **list_shipments**
> ShipmentList list_shipments(limit=limit, offset=offset)

List shipments with pagination

### Example


```python
import logistics_client
from logistics_client.models.shipment_list import ShipmentList
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
    api_instance = logistics_client.ShipmentsApi(api_client)
    limit = 20 # int |  (optional) (default to 20)
    offset = 0 # int |  (optional) (default to 0)

    try:
        # List shipments with pagination
        api_response = api_instance.list_shipments(limit=limit, offset=offset)
        print("The response of ShipmentsApi->list_shipments:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShipmentsApi->list_shipments: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **limit** | **int**|  | [optional] [default to 20]
 **offset** | **int**|  | [optional] [default to 0]

### Return type

[**ShipmentList**](ShipmentList.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | List of shipments |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

# **track_shipment**
> TrackingHistory track_shipment(shipment_id)

Get tracking history for a shipment

### Example


```python
import logistics_client
from logistics_client.models.tracking_history import TrackingHistory
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
    api_instance = logistics_client.ShipmentsApi(api_client)
    shipment_id = 'shipment_id_example' # str | 

    try:
        # Get tracking history for a shipment
        api_response = api_instance.track_shipment(shipment_id)
        print("The response of ShipmentsApi->track_shipment:\n")
        pprint(api_response)
    except Exception as e:
        print("Exception when calling ShipmentsApi->track_shipment: %s\n" % e)
```



### Parameters


Name | Type | Description  | Notes
------------- | ------------- | ------------- | -------------
 **shipment_id** | **str**|  | 

### Return type

[**TrackingHistory**](TrackingHistory.md)

### Authorization

No authorization required

### HTTP request headers

 - **Content-Type**: Not defined
 - **Accept**: application/json

### HTTP response details

| Status code | Description | Response headers |
|-------------|-------------|------------------|
**200** | Tracking history |  -  |
**404** | Shipment not found |  -  |

[[Back to top]](#) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to Model list]](../README.md#documentation-for-models) [[Back to README]](../README.md)

