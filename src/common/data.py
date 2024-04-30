import datetime
from pathlib import Path
from typing import Literal

import pandas as pd
from scipy.io import loadmat


def load_data(
    path: Path | str, 
    target_operation: Literal["charge", "discharge"]
) -> pd.DataFrame:
    
    path = Path(path)
    mat = loadmat(path)  # load mat-file
    data = mat[path.stem]["cycle"][0, 0]

    parsed_data = []
    for cycle in data:
        operation_id = 0
        for operation in cycle:
            operation_type = operation["type"][0]
            if operation_type != target_operation:
                continue

            for fields in operation["data"]:
                if operation_type == "charge":
                    operation_data = pd.DataFrame({
                        k: fields[k][0][0]
                        for k in fields.dtype.fields
                    })
                elif operation_type == "discharge":
                    operation_data = pd.DataFrame({
                        k: fields[k][0][0]
                        for k in fields.dtype.fields
                        if k != "Capacity"
                    })
                    operation_data["Capacity"] = fields["Capacity"][0][0, 0]      

            operation_data["operation_id"] = operation_id
            operation_data["temperature"] = operation["ambient_temperature"][0, 0]
            operation_data["type"] = operation_type
            operation_data["start_time"] = datetime.datetime(*(int(t) for t in operation["time"][0]))

            parsed_data.append(operation_data)
            operation_id += 1
    
    return pd.concat(parsed_data, ignore_index=True)