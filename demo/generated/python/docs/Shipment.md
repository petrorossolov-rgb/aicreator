# Shipment


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**shipment_id** | **str** |  | 
**order_id** | **str** |  | 
**warehouse_id** | **str** |  | 
**origin** | [**Address**](Address.md) |  | 
**destination** | [**Address**](Address.md) |  | 
**items** | [**List[ShipmentItem]**](ShipmentItem.md) |  | 
**status** | [**ShipmentStatus**](ShipmentStatus.md) |  | 
**tracking_history** | [**List[Location]**](Location.md) |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from logistics_client.models.shipment import Shipment

# TODO update the JSON string below
json = "{}"
# create an instance of Shipment from a JSON string
shipment_instance = Shipment.from_json(json)
# print the JSON string representation of the object
print(Shipment.to_json())

# convert the object into a dict
shipment_dict = shipment_instance.to_dict()
# create an instance of Shipment from a dict
shipment_from_dict = Shipment.from_dict(shipment_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


