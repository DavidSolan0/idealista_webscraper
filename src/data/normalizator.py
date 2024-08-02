import re

import numpy as np
import pandas as pd


class NormalizarDataFrame:
    """
    Clase para procesar información de anuncios inmobiliarios, incluyendo
    características del inmueble y certificados energéticos.

    Attributes
    ----------
    dataframe : pd.DataFrame
        DataFrame que contiene la información a normalizar.

    Methods
    -------
    extract_info_features(info)
        Extrae características de información del anuncio inmobiliario.
    filter_energy_data(data)
        Filtra los datos de energía para conservar solo los relevantes.
    extract_certificado_energetico(data)
        Extrae la información del certificado energético del anuncio.
    normalize_dataframe()
        Normaliza el DataFrame aplicando las funciones de extracción y
        crea nuevas columnas con la información extraída.
    """

    def __init__(self, dataframe: pd.DataFrame):
        """
        Inicializa una nueva instancia de RealEstateDataExtractor.

        Parameters
        ----------
        dataframe : pd.DataFrame
            DataFrame que contiene la información a normalizar.
        """
        self.dataframe = dataframe

    def extract_info_features(self, info: list) -> dict:
        """
        Extrae características de información del anuncio inmobiliario.

        Parameters
        ----------
        info : list
            Lista de información del anuncio.

        Returns
        -------
        dict
            Diccionario con las características extraídas.
        """
        # Como la info se recibe en forma de lista, se genera un único texto.
        info = " ".join(info)

        # Convertir a lowercase
        info = info.lower()

        # Definir los patrones de extracción
        superficie_pattern = re.compile(r"(\d+)\s*m²")
        habitaciones_pattern = re.compile(r"(\d+)\s*hab")
        garaje_incluido_pattern = re.compile(r"garaje incluido")
        con_garaje_pattern = re.compile(r"con garaje")
        planta_pattern = re.compile(r"planta (\d+)")
        con_ascensor_pattern = re.compile(r"con ascensor")
        sin_ascensor_pattern = re.compile(r"sin ascensor")

        # Extraer la información
        superficie = superficie_pattern.search(info)
        habitaciones = habitaciones_pattern.search(info)
        garaje = (
            True
            if garaje_incluido_pattern.search(info) or con_garaje_pattern.search(info)
            else False
        )
        planta = planta_pattern.search(info)

        if con_ascensor_pattern.search(info):
            ascensor = True
        elif sin_ascensor_pattern.search(info):
            ascensor = False
        else:
            ascensor = None

        return {
            "superficie_m2": int(superficie.group(1)) if superficie else None,
            "habitaciones": int(habitaciones.group(1)) if habitaciones else None,
            "garaje": garaje,
            "planta": int(planta.group(1)) if planta else None,
            "ascensor": ascensor,
        }

    def filter_energy_data(self, data: list) -> list:
        """
        Filtra los datos de energía para conservar solo los relevantes.

        Parameters
        ----------
        data : list
            Lista de diccionarios con la información energética.

        Returns
        -------
        list
            Lista de diccionarios filtrados con la información energética relevante.
        """
        filtered_data = []
        for item in data:
            filtered_item = {
                key: value
                for key, value in item.items()
                if key in ["Consumo:", "Emisiones:"] and value is not None
            }
            filtered_data.append(filtered_item)
        return filtered_data

    def extract_certificado_energetico(self, data: list) -> dict:
        """
        Extrae la información del certificado energético del anuncio.

        Parameters
        ----------
        data : list
            Lista de diccionarios con la información energética.

        Returns
        -------
        dict
            Diccionario con la información del certificado energético.
        """
        # Inicializar valores por defecto
        consumo_valor, consumo_icono, emisiones_valor, emisiones_icono = (
            None,
            None,
            None,
            None,
        )

        # Filtrar la información necesaria
        certificado = self.filter_energy_data(data)

        # Verificar y extraer la información de la lista de diccionarios
        for item in certificado:
            if "Consumo:" in item and item["Consumo:"] is not None:
                consumo = item["Consumo:"]
                if isinstance(consumo, np.ndarray):
                    if consumo[0]:  # Verificar si el primer elemento no está vacío
                        consumo_valor = consumo[0]
                    if consumo[1]:  # Verificar si el segundo elemento no está vacío
                        consumo_icono = consumo[1]

            if "Emisiones:" in item and item["Emisiones:"] is not None:
                emisiones = item["Emisiones:"]
                if isinstance(emisiones, np.ndarray):
                    if emisiones[0]:  # Verificar si el primer elemento no está vacío
                        emisiones_valor = emisiones[0]
                    if emisiones[1]:  # Verificar si el segundo elemento no está vacío
                        emisiones_icono = emisiones[1]

        return {
            "consumo_energetico_valor": consumo_valor,
            "consumo_energetico_icono": consumo_icono,
            "emisiones_valor": emisiones_valor,
            "emisiones_icono": emisiones_icono,
        }

    def extract_caracteristicas_basicas(self, caracteristicas_basicas: list) -> dict:
        """
        Extrae las características básicas de una propiedad desde
        una lista de descripciones.

        Parameters
        ----------
        caracteristicas_basicas : list
            Lista de características básicas.

        Returns
        -------
        dict
            Diccionario con las características extraídas.
        """
        caracteristicas_basicas = " ".join(caracteristicas_basicas).lower()

        # Patrones de búsqueda
        superficie_pattern = re.compile(r"(\d+)\s*m² construidos")
        superficie_util_pattern = re.compile(r"(\d+)\s*m² útiles")
        habitaciones_pattern = re.compile(r"(\d+)\s*habitaci?")
        banos_pattern = re.compile(r"(\d+)\s*baños?")
        parcela_pattern = re.compile(r"parcela de (\d+)\s*m²")
        terraza_pattern = re.compile(r"terraza")
        balcon_pattern = re.compile(r"balcón")
        garaje_pattern = re.compile(r"plaza de garaje incluida en el precio")
        estado_pattern = re.compile(r"segunda mano/buen estado")
        armarios_pattern = re.compile(r"armarios empotrados")
        orientacion_pattern = re.compile(r"orientación (\w+(?:, \w+)*)")
        cocina_pattern = re.compile(r"cocina equipada")
        casas_amueblada_pattern = re.compile(r"casa sin amueblar")
        amueblado_pattern = re.compile(r"amueblado")
        calefaccion_pattern = re.compile(r"calefacción\s*([\w\s:]+)")
        trastero_pattern = re.compile(r"trastero")
        construccion_pattern = re.compile(r"construido en (\d{4})")
        plantas_pattern = re.compile(r"(\d+)\s*plantas")

        # Extracción de datos
        superficie = superficie_pattern.search(caracteristicas_basicas)
        superficie_util = superficie_util_pattern.search(caracteristicas_basicas)
        habitaciones = habitaciones_pattern.search(caracteristicas_basicas)
        banos = banos_pattern.search(caracteristicas_basicas)
        parcela = parcela_pattern.search(caracteristicas_basicas)
        terraza = bool(terraza_pattern.search(caracteristicas_basicas))
        balcon = bool(balcon_pattern.search(caracteristicas_basicas))
        garaje = bool(garaje_pattern.search(caracteristicas_basicas))
        estado = bool(estado_pattern.search(caracteristicas_basicas))
        armarios = bool(armarios_pattern.search(caracteristicas_basicas))
        orientacion = orientacion_pattern.search(caracteristicas_basicas)
        cocina = bool(cocina_pattern.search(caracteristicas_basicas))
        amueblada = bool(
            casas_amueblada_pattern.search(caracteristicas_basicas)
        ) or bool(amueblado_pattern.search(caracteristicas_basicas))
        calefaccion = calefaccion_pattern.search(caracteristicas_basicas)
        trastero = bool(trastero_pattern.search(caracteristicas_basicas))
        construccion = construccion_pattern.search(caracteristicas_basicas)
        plantas = plantas_pattern.search(caracteristicas_basicas)

        return {
            "caracteristicas_basicas_superficie_m2": (
                int(superficie.group(1)) if superficie else None
            ),
            "superficie_util_m2": (
                int(superficie_util.group(1)) if superficie_util else None
            ),
            "caracteristicas_basicas_habitaciones": (
                int(habitaciones.group(1)) if habitaciones else None
            ),
            "caracteristicas_basicas_banos": int(banos.group(1)) if banos else None,
            "parcela_m2": int(parcela.group(1)) if parcela else None,
            "terraza": terraza,
            "balcon": balcon,
            "garaje_incluido": garaje,
            "segunda_mano_buen_estado": estado,
            "armarios_empotrados": armarios,
            "orientacion": orientacion.group(1) if orientacion else None,
            "cocina_equipada": cocina,
            "amueblada": amueblada,
            "calefaccion": calefaccion.group(1).strip() if calefaccion else None,
            "trastero": trastero,
            "construccion": int(construccion.group(1)) if construccion else None,
            "plantas": int(plantas.group(1)) if plantas else None,
        }

    def normalizar_precios(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Normaliza las columnas de precios en el DataFrame.

        Esta función procesa el DataFrame dado para normalizar las
        columnas de precios mediante:
        - Eliminar los puntos de la columna 'precio_inmueble' y
            convertirla a un entero.
        - Multiplicar la columna 'price' por 1000.
        - Reemplazar comas por puntos en la columna 'precio_m2' y
          convertirla a un flotante.

        Parameters
        ----------
        df :p d.DataFrame
            El DataFrame de entrada con información de precios.

        Returns
        -------
        pd.DataFrame: El DataFrame con las columnas de precios normalizadas.
        """
        return df.assign(
            precio_inmueble=lambda x: x["precio_inmueble"]
            .str.replace(".", "", regex=False)
            .str.extract(r"(\d+)")
            .astype("int64"),
            price=lambda x: x["price"].astype("float64") * 1000,
            precio_m2=lambda x: x["precio_m2"]
            .str.replace(",", ".", regex=False)
            .str.extract(r"(\d+\.?\d*)")
            .astype("float64"),
        )

    def normalize_dataframe(self) -> pd.DataFrame:
        """
        Normaliza el DataFrame aplicando las funciones de extracción y crea nuevas
        columnas con la información extraída.

        Returns
        -------
        pd.DataFrame
            DataFrame normalizado con las nuevas columnas de información extraída.
        """
        df_info_features = self.dataframe["info_features"].apply(
            lambda x: pd.Series(self.extract_info_features(x))
        )
        df_certificado_energetico = self.dataframe["certificado_energetico"].apply(
            lambda x: pd.Series(self.extract_certificado_energetico(x))
        )
        df_caracteristicas_basicas = self.dataframe["caracteristicas_basicas"].apply(
            lambda x: pd.Series(self.extract_caracteristicas_basicas(x))
        )

        dataframe_normalizado = pd.concat(
            [
                self.dataframe.drop(
                    columns=[
                        "info_features",
                        "certificado_energetico",
                        "caracteristicas_basicas",
                    ]
                ),
                df_info_features,
                df_certificado_energetico,
                df_caracteristicas_basicas,
            ],
            axis=1,
        )

        dataframe_normalizado.rename(
            columns={
                "Precio del inmueble:": "precio_inmueble",
                "Precio por m²:": "precio_m2",
            },
            inplace=True,
        )

        dataframe_normalizado = self.normalizar_precios(dataframe_normalizado)

        return dataframe_normalizado
