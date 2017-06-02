import os
import geopandas
import matplotlib.pyplot as plt

#import local files
from . import tabletools



if __name__ == "__main__":
    #folder = "D:\\Proginoskes\\Documents\\GitHub\\maptools\\shapefiles\\World - All Country Shapefiles\\"
    #shapepath = "shapefiles/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp"

    filename = ""

    shapepath = geopandas.datasets.get_path("naturalearth_lowres")
    shape = geopandas.read_file(shapepath)
    shape.plot()
    plt.show()
    print(shape)
