import folium
from folium import plugins
import geopandas as gpd
import pandas as pd
import branca.colormap as cm
from typing import Optional, Dict, List, Tuple
import numpy as np

from strategies.base_strategy import BaseStrategy


class MapRenderer:    
    def __init__(
        self,
        center: Tuple[float, float] = (-0.1807, -78.4678),
        zoom_start: int = 11
    ):
        self.center = center
        self.zoom_start = zoom_start
    
    def create_base_map(
        self,
        tiles: str = 'OpenStreetMap',
        **kwargs
    ) -> folium.Map:
        m = folium.Map(
            location=self.center,
            zoom_start=self.zoom_start,
            tiles=tiles,
            **kwargs
        )
        
        return m
    
    def render_districts_choropleth(
        self,
        m: folium.Map,
        districts_gdf: gpd.GeoDataFrame,
        scores_df: pd.DataFrame,
        strategy: BaseStrategy,
        show_labels: bool = True,
        layer_name: str = "Scores por Distrito"
    ) -> folium.Map:
        """        
        Args:
            m: Mapa base de Folium
            districts_gdf: GeoDataFrame con geometrías de distritos
            scores_df: DataFrame con scores (debe tener columnas: district_name, score)
            strategy: Estrategia usada (para obtener color scheme)
            show_labels: Si True, muestra etiquetas de nombres
            layer_name: Nombre de la capa
        
        Returns:
            Mapa de Folium con choropleth
        """
        # Asegurar que están en el mismo CRS
        if districts_gdf.crs != 'EPSG:4326':
            districts_gdf = districts_gdf.to_crs('EPSG:4326')
        
        # Merge de geometrías con scores        
        merged = districts_gdf.copy()
        
        # Intentar hacer merge por display_name
        if 'display_name' in merged.columns:
            merged = merged.merge(
                scores_df[['district_name', 'score', 'rank', 'safety', 'transport', 'green', 'services']],
                left_on='display_name',
                right_on='district_name',
                how='left'
            )
        else:
            # Fallback: asumir que están en el mismo orden
            merged['score'] = scores_df['score'].values
            merged['rank'] = scores_df['rank'].values
            merged['district_name'] = scores_df['district_name'].values
            merged['safety'] = scores_df['safety'].values
            merged['transport'] = scores_df['transport'].values
            merged['green'] = scores_df['green'].values
            merged['services'] = scores_df['services'].values
        
        # Manejar NaN en scores (distritos sin score)
        merged['score'] = merged['score'].fillna(0)
        
        # Obtener esquema de colores
        color_scheme = strategy.get_color_scheme()
        
        # Crear colormap
        min_score = merged['score'].min()
        max_score = merged['score'].max()
        
        # Evitar división por cero
        if max_score == min_score:
            max_score = min_score + 0.1
        
        # Crear escala de colores
        colormap = self._create_colormap(color_scheme, min_score, max_score)
        
        # Crear FeatureGroup para la capa
        feature_group = folium.FeatureGroup(name=layer_name)
        
        # Agregar polígonos coloreados
        for idx, row in merged.iterrows():
            # Obtener color según score
            score = row['score']
            color = colormap(score)
            
            # Crear tooltip
            tooltip_html = self._create_custom_tooltip(row, strategy)
            
            # Crear polígono
            folium.GeoJson(
                row['geometry'],
                style_function=lambda x, color=color: {
                    'fillColor': color,
                    'color': 'black',
                    'weight': 2,
                    'fillOpacity': 0.7
                },
                highlight_function=lambda x: {
                    'weight': 4,
                    'fillOpacity': 0.9
                },
                tooltip=folium.Tooltip(tooltip_html, sticky=True)
            ).add_to(feature_group)
            
            # Agregar etiqueta si se solicita
            if show_labels and 'district_name' in row:
                # Obtener centroide
                centroid = row['geometry'].centroid
                
                folium.Marker(
                    location=[centroid.y, centroid.x],
                    icon=folium.DivIcon(
                        html=f'''
                        <div style="
                            font-size: 10px;
                            font-weight: bold;
                            color: black;
                            text-align: center;
                            white-space: nowrap;
                            text-shadow: 1px 1px 2px white, -1px -1px 2px white;
                        ">
                            {row['district_name'][:20]}
                        </div>
                        '''
                    )
                ).add_to(feature_group)
        
        # Agregar FeatureGroup al mapa
        feature_group.add_to(m)
        
        # Agregar leyenda
        colormap.caption = f"Score - {strategy.get_name()}"
        colormap.add_to(m)
        
        return m
    
    def _create_colormap(
        self,
        color_scheme: str,
        vmin: float,
        vmax: float,
        n_colors: int = 6
    ) -> cm.LinearColormap:
        """
        Crea un colormap de Branca.
        
        Args:
            color_scheme: Nombre del esquema ('YlGn', 'RdYlGn', etc.)
            vmin: Valor mínimo
            vmax: Valor máximo
            n_colors: Número de colores en la escala
        
        Returns:
            LinearColormap de Branca
        """
        # Mapeo de esquemas a paletas
        color_palettes = {
            'YlGn': ['#ffffe5', '#fff7bc', '#d9f0a3', '#addd8e', '#78c679', '#41ab5d', '#238443'],
            'YlOrRd': ['#ffffb2', '#fecc5c', '#fd8d3c', '#f03b20', '#bd0026'],
            'PuBu': ['#f1eef6', '#d0d1e6', '#a6bddb', '#74a9cf', '#3690c0', '#0570b0', '#034e7b'],
            'RdYlGn': ['#d73027', '#fc8d59', '#fee08b', '#d9ef8b', '#91cf60', '#1a9850'],
            'Spectral': ['#d53e4f', '#fc8d59', '#fee08b', '#e6f598', '#99d594', '#3288bd']
        }
        
        # Obtener paleta o usar default
        colors = color_palettes.get(color_scheme, color_palettes['YlGn'])
        
        # Crear colormap
        colormap = cm.LinearColormap(
            colors=colors,
            vmin=vmin,
            vmax=vmax,
            caption='Score'
        )
        
        return colormap
    
    def _create_custom_tooltip(
        self,
        district_data: pd.Series,
        strategy: BaseStrategy
    ) -> str:
        """
        Crea HTML para tooltip personalizado.
        
        Args:
            district_data: Serie con datos del distrito
            strategy: Estrategia usada
        
        Returns:
            HTML del tooltip
        """
        name = district_data.get('district_name', 'N/A')
        score = district_data.get('score', 0)
        rank = district_data.get('rank', '-')
        
        # Métricas
        safety = district_data.get('safety', 0)
        transport = district_data.get('transport', 0)
        green = district_data.get('green', 0)
        services = district_data.get('services', 0)
        
        # Crear estrellas para visualización
        def score_to_stars(value, max_stars=5):
            filled = int(value * max_stars)
            return '★' * filled + '☆' * (max_stars - filled)
        
        # Interpretación del score
        if score >= 0.8:
            interpretation = "Excelente"
            color = "#1a9850"
        elif score >= 0.6:
            interpretation = "Bueno"
            color = "#91cf60"
        elif score >= 0.4:
            interpretation = "Moderado"
            color = "#fee08b"
        else:
            interpretation = "Bajo"
            color = "#fc8d59"
        
        html = f"""
        <div style="
            font-family: Arial, sans-serif;
            font-size: 12px;
            min-width: 200px;
            padding: 10px;
        ">
            <h4 style="margin: 0 0 10px 0; color: #333;">
                {name}
            </h4>
            
            <div style="
                background-color: {color};
                color: white;
                padding: 5px;
                border-radius: 3px;
                margin-bottom: 10px;
                text-align: center;
            ">
                <strong>Score: {score:.2f}</strong> ({interpretation})
                <br>
                <small>Ranking: #{int(rank)}</small>
            </div>
            
            <div style="margin-top: 10px;">
                <strong>Estrategia:</strong> {strategy.get_name()}
            </div>
            
            <hr style="margin: 10px 0;">
            
            <div style="line-height: 1.6;">
                <div>
                    <strong>Seguridad:</strong><br>
                    {score_to_stars(safety)} {safety:.2f}
                </div>
                <div>
                    <strong>Transporte:</strong><br>
                    {score_to_stars(transport)} {transport:.2f}
                </div>
                <div>
                    <strong>Espacios Verdes:</strong><br>
                    {score_to_stars(green)} {green:.2f}
                </div>
                <div>
                    <strong>Servicios:</strong><br>
                    {score_to_stars(services)} {services:.2f}
                </div>
            </div>
        </div>
        """
        
        return html
    
    def add_district_labels(
        self,
        m: folium.Map,
        districts_gdf: gpd.GeoDataFrame,
        label_field: str = 'display_name'
    ) -> folium.Map:
        """
        Agrega etiquetas de nombres a los distritos.
        
        Args:
            m: Mapa de Folium
            districts_gdf: GeoDataFrame con distritos
            label_field: Campo con el nombre a mostrar
        
        Returns:
            Mapa con etiquetas
        """
        for idx, row in districts_gdf.iterrows():
            if label_field in row and pd.notna(row[label_field]):
                centroid = row.geometry.centroid
                
                folium.Marker(
                    location=[centroid.y, centroid.x],
                    icon=folium.DivIcon(
                        html=f'''
                        <div style="
                            font-size: 11px;
                            font-weight: bold;
                            color: #333;
                            background-color: rgba(255, 255, 255, 0.8);
                            padding: 2px 5px;
                            border-radius: 3px;
                            border: 1px solid #999;
                        ">
                            {row[label_field][:25]}
                        </div>
                        '''
                    )
                ).add_to(m)
        
        return m
    
    def add_fullscreen_control(self, m: folium.Map) -> folium.Map:
        plugins.Fullscreen(
            position='topleft',
            title='Pantalla completa',
            title_cancel='Salir de pantalla completa',
            force_separate_button=True
        ).add_to(m)
        
        return m
    
    def add_minimap(self, m: folium.Map) -> folium.Map:
        minimap = plugins.MiniMap(
            tile_layer='OpenStreetMap',
            position='bottomright',
            width=150,
            height=150,
            collapsed_width=25,
            collapsed_height=25
        )
        m.add_child(minimap)
        
        return m
    
    def add_city_layers(
        self,
        m: folium.Map,
        city_graph,
        layers_config: Dict[str, bool]
    ) -> folium.Map:
        """
        Agrega capas adicionales del CityGraph al mapa.
        
        Args:
            m: Mapa de Folium
            city_graph: Instancia de CityGraph
            layers_config: Dict con configuración de capas visibles
                          Ej: {'crimes': True, 'metro': False, ...}
        
        Returns:
            Mapa con capas adicionales
        """
        from factories.parks_layer_factory import ParksLayerFactory
        from factories.tourist_place_layer_factory import TouristPlaceLayerFactory
        from factories.crimes_layer_factory import CrimesLayerFactory
        from folium_integration.metro.metro_factory import MetroFactory
        from folium_integration.bus.bus_factory import BusFactory
        from folium_integration.city_integration import CityTransportIntegration
        from settings import settings
        
        # Parques
        if layers_config.get('parks', False):
            try:
                park_factory = ParksLayerFactory()
                park_layers = park_factory.create_feature_group(city_graph)
                park_layers.add_to(m)
            except Exception as e:
                print(f" Error agregando capa de parques: {e}")
        
        # Lugares turísticos
        if layers_config.get('tourist_places', False):
            try:
                tourism_factory = TouristPlaceLayerFactory()
                tourism_layers = tourism_factory.create_feature_group(city_graph)
                tourism_layers.add_to(m)
            except Exception as e:
                print(f" Error agregando lugares turísticos: {e}")
        
        # Crímenes
        if layers_config.get('crimes', False):
            try:
                crime_factory = CrimesLayerFactory(
                    shapefile_path=settings.SHP_CRIMES,
                    layer_type='colored_polygons',
                    color_field='color'
                )
                crime_layers = crime_factory.create_layer()
                for layer in crime_layers:
                    layer.add_to(m)
            except Exception as e:
                print(f" Error agregando capa de crímenes: {e}")
        
        # Sistema de transporte
        if layers_config.get('metro', False) or layers_config.get('bus_routes', False) or layers_config.get('bus_stops', False):
            try:
                transport_integration = CityTransportIntegration()
                
                # Metro
                if layers_config.get('metro', False):
                    metro_factory = MetroFactory(
                        settings.SHP_METRO,
                        settings.SHP_METRO_STATIONS,
                        system_name="Metro de Quito"
                    )
                    transport_integration.add_transport_system(metro_factory)
                
                # Buses
                if layers_config.get('bus_routes', False) or layers_config.get('bus_stops', False):
                    # Determinar qué mostrar
                    show_routes = layers_config.get('bus_routes', False)
                    show_stops = layers_config.get('bus_stops', False)
                    
                    bus_factory = BusFactory(
                        settings.SHP_BUS_ROUTES,
                        settings.SHP_BUS_STOPS,
                        system_name="Buses Urbanos",
                        max_routes=50 if show_routes else 0,
                        max_stops=1000 if show_stops else 0
                    )
                    transport_integration.add_transport_system(bus_factory)
                
                # Agregar al mapa
                transport_integration.add_layers_to_map(m)
                
            except Exception as e:
                print(f" Error agregando capas de transporte: {e}")
        
        return m