import geopandas
import matplotlib.pyplot as plt
from geopandas.plotting import *

from .. import tabletools


class GeoPlot:
    def __init__(self, filename, kind = 'global', **kwargs):
        self.data_table = self._loadDataTable(filename, filters)
        self.geometry_table = self._loadGeometry(kind)
        
        self._generateMapParameters(**kwargs)
        
    def _loadDataTable(self, filename, filters):
        if filters is None: filters = []
    
        table = tabletools.Table(filename).df
        for key, value in filters:
            table = table[table[key] == value]
        table = tabletools.Table(table)
        return table
    
    def _loadGeometry(self, kind, region_code_column, value_column):
        
        if kind == 'global' or kind == 'world':
            geometry_filename = geopandas.datasets.get_path('naturalearth_lowres')
        elif kind == 'USA' or kind == 'United States':
            pass
        
        geometry_table = geopandas.read_file(geometry_filename)
        
        geometry_table['values'] = [
            self.data_table(region_code_column,code, value_column, ignore = True) 
            for code in cart['iso_a3'].values
        ]
        
        return geometry_table
    
    def _generateMapParameters(self, **kwargs):
		pass
    
    def plot(self, **kwargs):
        
        fig, ax = plt.subplots(figsize = (20, 10))
        _value_columns = 'values'
        
        missing_values = map_table[map_table['values'].isnull()]
        map_table = map_table.dropna(how = 'any')
        
        ax = self.geometry_table.plot(
            column = 'values', 
            scheme = 'quantiles', 
            legend = True, 
            k = 5,
            cmap = 'Blues',
            figsize = (20, 10)
        )

        ax = missing_values.plot(
            column = 'values',
            ax = ax,
            color = '#D0D0D0'
        )
        ax = plot_dataframe(self.geometry_table, *args, **kwargs)
        ax = plot_dataframe(missing_values, *args, **kwargs)
        
        return ax
