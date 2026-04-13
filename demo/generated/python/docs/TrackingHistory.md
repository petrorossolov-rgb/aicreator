# TrackingHistory


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**shipment_id** | **str** |  | [optional] 
**locations** | [**List[Location]**](Location.md) |  | [optional] 

## Example

```python
from logistics_client.models.tracking_history import TrackingHistory

# TODO update the JSON string below
json = "{}"
# create an instance of TrackingHistory from a JSON string
tracking_history_instance = TrackingHistory.from_json(json)
# print the JSON string representation of the object
print(TrackingHistory.to_json())

# convert the object into a dict
tracking_history_dict = tracking_history_instance.to_dict()
# create an instance of TrackingHistory from a dict
tracking_history_from_dict = TrackingHistory.from_dict(tracking_history_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


