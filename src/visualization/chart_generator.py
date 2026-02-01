import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Optional, List, Dict, Tuple

from strategies.base_strategy import BaseStrategy


class ChartGenerator:    
    def __init__(self):
        self.color_schemes = {
            'quality_of_life': '#2E7D32',
            'tourist': '#D32F2F',
            'convenience': '#1976D2',
            'default': '#424242'
        }
    
    def create_ranking_bar_chart(
        self,
        scores_df: pd.DataFrame,
        strategy: BaseStrategy,
        top_n: int = 10,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Crea gráfico de barras horizontales con ranking de distritos.
        
        Args:
            scores_df: DataFrame con scores (columns: district_name, score, rank)
            strategy: Estrategia usada
            top_n: Número de distritos a mostrar
            title: Título del gráfico (opcional)
        
        Returns:
            Figura de Plotly
        """
        # Tomar top N distritos
        top_districts = scores_df.head(top_n).copy()
        
        # Invertir orden para que el mejor esté arriba
        top_districts = top_districts.iloc[::-1]
        
        # Obtener color según estrategia
        strategy_name = strategy.get_name().lower().replace(' ', '_').replace('/', '_')
        color = self.color_schemes.get(strategy_name, self.color_schemes['default'])
        
        # Crear figura
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            y=top_districts['district_name'],
            x=top_districts['score'],
            orientation='h',
            marker=dict(
                color=top_districts['score'],
                colorscale=[
                    [0, '#fee5d9'],
                    [0.5, color],
                    [1, '#006d2c']
                ],
                showscale=True,
                colorbar=dict(
                    title="Score",
                    thickness=15,
                    len=0.7
                )
            ),
            text=top_districts['score'].apply(lambda x: f'{x:.3f}'),
            textposition='auto',
            hovertemplate='<b>%{y}</b><br>Score: %{x:.3f}<extra></extra>'
        ))
        
        # Título
        if title is None:
            title = f"Top {top_n} Distritos - {strategy.get_name()}"
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=18, color='#333')
            ),
            xaxis=dict(
                title="Score",
                range=[0, 1],
                gridcolor='#e0e0e0'
            ),
            yaxis=dict(
                title="",
                tickfont=dict(size=11)
            ),
            height=400 + (top_n * 20),
            margin=dict(l=150, r=50, t=80, b=50),
            plot_bgcolor='white',
            paper_bgcolor='white',
            hovermode='closest'
        )
        
        return fig
    
    def create_metrics_radar_chart(
        self,
        district_data: pd.Series,
        strategy: BaseStrategy,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Crea radar chart de métricas de un distrito.
        
        Args:
            district_data: Serie con datos del distrito
            strategy: Estrategia usada
            title: Título del gráfico (opcional)
        
        Returns:
            Figura de Plotly
        """
        # Métricas a mostrar
        metrics = {
            'Seguridad': district_data.get('safety', 0),
            'Transporte': district_data.get('transport', 0),
            'Espacios Verdes': district_data.get('green', 0),
            'Servicios': district_data.get('services', 0)
        }
        
        categories = list(metrics.keys())
        values = list(metrics.values())
        
        # Cerrar el polígono
        categories_closed = categories + [categories[0]]
        values_closed = values + [values[0]]
        
        # Obtener pesos de la estrategia
        weights = strategy.get_weights()
        weights_values = [
            weights.get('safety', 0),
            weights.get('transport', 0),
            weights.get('green', 0),
            weights.get('services', 0)
        ]
        weights_closed = weights_values + [weights_values[0]]
        
        # Crear figura
        fig = go.Figure()
        
        # Traza de valores del distrito
        fig.add_trace(go.Scatterpolar(
            r=values_closed,
            theta=categories_closed,
            fill='toself',
            name='Valores del Distrito',
            line=dict(color='#1976D2', width=2),
            fillcolor='rgba(25, 118, 210, 0.3)'
        ))
        
        # Traza de pesos de la estrategia (normalizado)
        max_weight = max(weights_values) if max(weights_values) > 0 else 1
        weights_normalized = [w / max_weight for w in weights_values] + [weights_values[0] / max_weight]
        
        fig.add_trace(go.Scatterpolar(
            r=weights_normalized,
            theta=categories_closed,
            fill='toself',
            name='Importancia (Estrategia)',
            line=dict(color='#FFA726', width=2, dash='dash'),
            fillcolor='rgba(255, 167, 38, 0.1)'
        ))
        
        # Título
        if title is None:
            district_name = district_data.get('district_name', 'Distrito')
            title = f"Métricas - {district_name}"
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1],
                    gridcolor='#e0e0e0'
                ),
                angularaxis=dict(
                    gridcolor='#e0e0e0'
                )
            ),
            title=dict(
                text=title,
                font=dict(size=16, color='#333')
            ),
            showlegend=True,
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.2,
                xanchor="center",
                x=0.5
            ),
            height=450,
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_score_distribution(
        self,
        scores_df: pd.DataFrame,
        strategy: BaseStrategy,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Crea histograma de distribución de scores.
        
        Args:
            scores_df: DataFrame con scores
            strategy: Estrategia usada
            title: Título del gráfico (opcional)
        
        Returns:
            Figura de Plotly
        """
        # Obtener color según estrategia
        strategy_name = strategy.get_name().lower().replace(' ', '_').replace('/', '_')
        color = self.color_schemes.get(strategy_name, self.color_schemes['default'])
        
        # Crear figura
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=scores_df['score'],
            nbinsx=15,
            marker=dict(
                color=color,
                line=dict(color='white', width=1)
            ),
            opacity=0.75,
            name='Distritos',
            hovertemplate='Score: %{x:.3f}<br>Cantidad: %{y}<extra></extra>'
        ))
        
        # Agregar línea de promedio
        mean_score = scores_df['score'].mean()
        
        fig.add_vline(
            x=mean_score,
            line_dash="dash",
            line_color="red",
            annotation_text=f"Promedio: {mean_score:.3f}",
            annotation_position="top"
        )
        
        # Título
        if title is None:
            title = f"Distribución de Scores - {strategy.get_name()}"
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, color='#333')
            ),
            xaxis=dict(
                title="Score",
                range=[0, 1],
                gridcolor='#e0e0e0'
            ),
            yaxis=dict(
                title="Número de Distritos",
                gridcolor='#e0e0e0'
            ),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False,
            bargap=0.1
        )
        
        return fig
    
    def create_comparison_table(
        self,
        top_districts: pd.DataFrame,
        columns: Optional[List[str]] = None
    ) -> go.Figure:
        """
        Crea tabla comparativa de distritos.
        
        Args:
            top_districts: DataFrame con distritos a comparar
            columns: Columnas a mostrar (opcional)
        
        Returns:
            Figura de Plotly
        """
        if columns is None:
            columns = ['district_name', 'score', 'rank', 'safety', 'transport', 'green', 'services']
        
        # Filtrar solo columnas existentes
        available_columns = [col for col in columns if col in top_districts.columns]
        df_filtered = top_districts[available_columns].copy()
        
        # Formatear valores numéricos
        for col in df_filtered.columns:
            if col in ['score', 'safety', 'transport', 'green', 'services']:
                df_filtered[col] = df_filtered[col].apply(lambda x: f'{x:.3f}')
            elif col == 'rank':
                df_filtered[col] = df_filtered[col].apply(lambda x: f'#{int(x)}')
        
        # Renombrar columnas para mostrar
        column_names = {
            'district_name': 'Distrito',
            'score': 'Score',
            'rank': 'Ranking',
            'safety': 'Seguridad',
            'transport': 'Transporte',
            'green': 'Verde',
            'services': 'Servicios'
        }
        
        df_filtered = df_filtered.rename(columns=column_names)
        
        # Colores alternados para filas
        fill_colors = []
        for i in range(len(df_filtered)):
            if i % 2 == 0:
                fill_colors.append('#f5f5f5')
            else:
                fill_colors.append('white')
        
        # Crear tabla
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=list(df_filtered.columns),
                fill_color='#1976D2',
                font=dict(color='white', size=12, family='Arial'),
                align='left',
                height=30
            ),
            cells=dict(
                values=[df_filtered[col] for col in df_filtered.columns],
                fill_color=[fill_colors],
                font=dict(color='#333', size=11, family='Arial'),
                align='left',
                height=25
            )
        )])
        
        fig.update_layout(
            title=dict(
                text="Comparación Detallada de Distritos",
                font=dict(size=16, color='#333')
            ),
            height=300 + (len(df_filtered) * 25),
            margin=dict(l=20, r=20, t=60, b=20)
        )
        
        return fig
    
    def create_metrics_comparison_chart(
        self,
        scores_df: pd.DataFrame,
        district_names: List[str],
        strategy: BaseStrategy
    ) -> go.Figure:
        """
        Crea gráfico de barras agrupadas comparando métricas de múltiples distritos.
        
        Args:
            scores_df: DataFrame con scores
            district_names: Lista de nombres de distritos a comparar
            strategy: Estrategia usada
        
        Returns:
            Figura de Plotly
        """
        # Filtrar distritos
        districts_data = scores_df[scores_df['district_name'].isin(district_names)].copy()
        
        if len(districts_data) == 0:
            # Retornar figura vacía si no hay datos
            return go.Figure()
        
        # Métricas a comparar
        metrics = ['safety', 'transport', 'green', 'services']
        metric_labels = {
            'safety': 'Seguridad',
            'transport': 'Transporte',
            'green': 'Espacios Verdes',
            'services': 'Servicios'
        }
        
        # Crear figura
        fig = go.Figure()
        
        colors = ['#2E7D32', '#1976D2', '#FFA726', '#D32F2F']
        
        for i, metric in enumerate(metrics):
            fig.add_trace(go.Bar(
                name=metric_labels[metric],
                x=districts_data['district_name'],
                y=districts_data[metric],
                marker=dict(color=colors[i]),
                text=districts_data[metric].apply(lambda x: f'{x:.2f}'),
                textposition='auto'
            ))
        
        fig.update_layout(
            title=dict(
                text=f"Comparación de Métricas - {strategy.get_name()}",
                font=dict(size=16, color='#333')
            ),
            xaxis=dict(
                title="Distrito",
                tickangle=-45
            ),
            yaxis=dict(
                title="Valor",
                range=[0, 1],
                gridcolor='#e0e0e0'
            ),
            barmode='group',
            height=450,
            plot_bgcolor='white',
            paper_bgcolor='white',
            legend=dict(
                orientation="h",
                yanchor="bottom",
                y=-0.4,
                xanchor="center",
                x=0.5
            ),
            margin=dict(b=120)
        )
        
        return fig
    
    def create_correlation_heatmap(
        self,
        scores_df: pd.DataFrame,
        title: Optional[str] = None
    ) -> go.Figure:
        """
        Crea heatmap de correlación entre métricas.
        
        Args:
            scores_df: DataFrame con scores
            title: Título del gráfico (opcional)
        
        Returns:
            Figura de Plotly
        """
        # Seleccionar métricas
        metrics = ['safety', 'transport', 'green', 'services', 'score']
        df_metrics = scores_df[metrics].copy()
        
        # Calcular correlación
        corr_matrix = df_metrics.corr()
        
        # Labels
        metric_labels = {
            'safety': 'Seguridad',
            'transport': 'Transporte',
            'green': 'Verde',
            'services': 'Servicios',
            'score': 'Score Final'
        }
        
        labels = [metric_labels[m] for m in metrics]
        
        # Crear heatmap
        fig = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=labels,
            y=labels,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values,
            texttemplate='%{text:.2f}',
            textfont={"size": 10},
            colorbar=dict(
                title="Correlación",
                thickness=15,
                len=0.7
            )
        ))
        
        # Título
        if title is None:
            title = "Correlación entre Métricas"
        
        fig.update_layout(
            title=dict(
                text=title,
                font=dict(size=16, color='#333')
            ),
            height=450,
            width=500,
            xaxis=dict(side='bottom'),
            yaxis=dict(autorange='reversed'),
            paper_bgcolor='white'
        )
        
        return fig
    
    def create_multi_strategy_comparison(
        self,
        all_scores: Dict[str, pd.DataFrame],
        district_name: str
    ) -> go.Figure:
        """
        Compara scores de un distrito bajo diferentes estrategias.
        
        Args:
            all_scores: Dict con {strategy_name: scores_df}
            district_name: Nombre del distrito a analizar
        
        Returns:
            Figura de Plotly
        """
        # Extraer scores del distrito
        strategy_scores = {}
        
        for strategy_name, scores_df in all_scores.items():
            district_data = scores_df[scores_df['district_name'] == district_name]
            if len(district_data) > 0:
                strategy_scores[strategy_name] = district_data.iloc[0]['score']
        
        if len(strategy_scores) == 0:
            return go.Figure()
        
        # Crear gráfico
        fig = go.Figure()
        
        strategies = list(strategy_scores.keys())
        scores = list(strategy_scores.values())
        
        colors = [self.color_schemes.get(s, self.color_schemes['default']) for s in strategies]
        
        fig.add_trace(go.Bar(
            x=strategies,
            y=scores,
            marker=dict(color=colors),
            text=[f'{s:.3f}' for s in scores],
            textposition='auto'
        ))
        
        fig.update_layout(
            title=dict(
                text=f"Scores de '{district_name}' por Estrategia",
                font=dict(size=16, color='#333')
            ),
            xaxis=dict(
                title="Estrategia",
                tickangle=-30
            ),
            yaxis=dict(
                title="Score",
                range=[0, 1],
                gridcolor='#e0e0e0'
            ),
            height=400,
            plot_bgcolor='white',
            paper_bgcolor='white',
            showlegend=False
        )
        
        return fig