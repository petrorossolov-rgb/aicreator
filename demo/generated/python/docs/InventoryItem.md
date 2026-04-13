# InventoryItem


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**sku** | **str** |  | 
**name** | **str** |  | 
**quantity_on_hand** | **int** |  | 
**quantity_reserved** | **int** |  | [optional] 
**reorder_point** | **int** |  | [optional] 

## Example

```python
from logistics_client.models.inventory_item import InventoryItem

# TODO update the JSON string below
json = "{}"
# create an instance of InventoryItem from a JSON string
inventory_item_instance = InventoryItem.from_json(json)
# print the JSON string representation of the object
print(InventoryItem.to_json())

# convert the object into a dict
inventory_item_dict = inventory_item_instance.to_dict()
# create an instance of InventoryItem from a dict
inventory_item_from_dict = InventoryItem.from_dict(inventory_item_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


