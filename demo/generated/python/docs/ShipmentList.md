# ShipmentList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Shipment]**](Shipment.md) |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from logistics_client.models.shipment_list import ShipmentList

# TODO update the JSON string below
json = "{}"
# create an instance of ShipmentList from a JSON string
shipment_list_instance = ShipmentList.from_json(json)
# print the JSON string representation of the object
print(ShipmentList.to_json())

# convert the object into a dict
shipment_list_dict = shipment_list_instance.to_dict()
# create an instance of ShipmentList from a dict
shipment_list_from_dict = ShipmentList.from_dict(shipment_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


