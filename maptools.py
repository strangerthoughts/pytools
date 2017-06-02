import geopandas
import matplotlib.pyplot as plt



if __name__ == "__main__":
    filename = ""
    shapepath = geopandas.datasets.get_path("naturalearth_lowres")
    shape = geopandas.read_file(shapepath)
    shape.plot()
    plt.show()
    print(shape)
