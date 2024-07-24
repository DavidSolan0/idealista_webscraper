import os

import pandas as pd


def save_df_to_parquet(
    dataframe_to_save: pd.DataFrame, dest_path: str, name: str, replace: bool = False
) -> None:
    """
    Guarda un DataFrame en formato Parquet en la ruta especificada.

    Parameters
    ----------
    dataframe_to_save : pd.DataFrame
        El DataFrame a guardar.
    dest_path : str
        La ruta del directorio donde se guardará el archivo.
    name : str
        El nombre del archivo Parquet (incluyendo la extensión .parquet).
    replace : bool, optional
        Si es True y el archivo ya existe, concatena el nuevo DataFrame
        con el existente y guarda el resultado. Si es False, sobrescribe
        el archivo existente. Por defecto es False.

    Returns
    -------
    None
    """

    # Verificar si la extensión está específicada en el nombre
    if ".parquet" not in name:
        name = name + ".parquet"

    # Definir el path de DataFrame a guardar
    file_path = os.path.join(dest_path, name)

    # Verificar si el path existe
    if os.path.exists(file_path):
        if replace:
            # Si existe y el flag replace es True. Cargar los datos que están y
            # concatenarlos con el dataframe a guardar. Guardar el nuevo DataFrame
            # con las filas actualizadas
            existing_df = pd.read_parquet(file_path)
            updated_df = pd.concat([existing_df, dataframe_to_save])
            updated_df.to_parquet(file_path)
        else:
            # Si existe y el flag replace se reescribe el DataFrame
            dataframe_to_save.to_parquet(file_path)
    else:
        # Si no existe, se crea la carpeta dest_path si no existe y se guarda
        # el DataFrame ahí
        os.makedirs(dest_path, exist_ok=True)
        dataframe_to_save.to_parquet(file_path)
