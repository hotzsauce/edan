
# always create the data/warehouse directory
import pathlib
warehouse = pathlib.Path(__file__).parent / 'warehouse'
if not warehouse.exists():
	warehouse.mkdir()
