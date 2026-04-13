# WarehouseList


## Properties

Name | Type | Description | Notes
------------ | ------------- | ------------- | -------------
**items** | [**List[Warehouse]**](Warehouse.md) |  | [optional] 
**total** | **int** |  | [optional] 

## Example

```python
from logistics_client.models.warehouse_list import WarehouseList

# TODO update the JSON string below
json = "{}"
# create an instance of WarehouseList from a JSON string
warehouse_list_instance = WarehouseList.from_json(json)
# print the JSON string representation of the object
print(WarehouseList.to_json())

# convert the object into a dict
warehouse_list_dict = warehouse_list_instance.to_dict()
# create an instance of WarehouseList from a dict
warehouse_list_from_dict = WarehouseList.from_dict(warehouse_list_dict)
```
[[Back to Model list]](../README.md#documentation-for-models) [[Back to API list]](../README.md#documentation-for-api-endpoints) [[Back to README]](../README.md)


