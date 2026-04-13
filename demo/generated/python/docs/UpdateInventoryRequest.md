# UpdateInventoryRequest


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**quantity_on_hand** | **int** |  | [optional] 
**quantity_reserved** | **int** |  | [optional] 
**reorder_point** | **int** |  | [optional] 

## Example

```python
from logistics_client.models.update_inventory_request import UpdateInventoryRequest

# TODO update the JSON string below
json = "{}"
# create an instance of UpdateInventoryRequest from a JSON string
update_inventory_request_instance = UpdateInventoryRequest.from_json(json)
# print the JSON string representation of the object
print(UpdateInventoryRequest.to_json())

# convert the object into a dict
update_inventory_request_dict = update_inventory_request_instance.to_dict()
# create an instance of UpdateInventoryRequest from a dict
update_inventory_request_from_dict = UpdateInventoryRequest.from_dict(update_inventory_request_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


