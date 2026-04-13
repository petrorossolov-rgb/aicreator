# Warehouse


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**warehouse_id** | **str** |  | 
**name** | **str** |  | 
**address** | [**Address**](Address.md) |  | 
**latitude** | **float** |  | [optional] 
**longitude** | **float** |  | [optional] 
**inventory** | [**List[InventoryItem]**](InventoryItem.md) |  | [optional] 
**created_at** | **datetime** |  | [optional] 
**updated_at** | **datetime** |  | [optional] 

## Example

```python
from logistics_client.models.warehouse import Warehouse

# TODO update the JSON string below
json = "{}"
# create an instance of Warehouse from a JSON string
warehouse_instance = Warehouse.from_json(json)
# print the JSON string representation of the object
print(Warehouse.to_json())

# convert the object into a dict
warehouse_dict = warehouse_instance.to_dict()
# create an instance of Warehouse from a dict
warehouse_from_dict = Warehouse.from_dict(warehouse_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


