#%%

"""
Grupo: "How DER You?"
Integrantes: Mario Sigal Aguirre, Augusto Guarnaccio, Azul Barracchia
Evaluación de modelos de clasificación sobre el dataset Fashion MNIST
"""

#%% Importación de bibliotecas

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.neighbors import KNeighborsRegressor
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
from sklearn.model_selection import GridSearchCV
import random
from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import f1_score

#%% Importación de datos

fashion_mnist = pd.read_csv('./fashion-mnist.csv')
fashion_mnist.head()

#%% Definición de funciones

# Función que trasforma la fila de una prenda en específico, con sus 784 
# pixeles, en una imagen. 0 <= num_fila < 60000
def visualizar_prenda(num_fila):
    etiqueta = ['Remera/top', 'Pantalones', 'Suéter', 'Vestido', 'Abrigo', 'Sandalias', 'Camisa', 'Zapatillas', 'Cartera', 'Botas']
    data = fashion_mnist.values
    pixel_values = data[num_fila][1:]
    
    # Convertir los valores de píxeles a una matriz de 28x28
    image_array = np.array(pixel_values).reshape(28, 28) 
    
    # Mostrar la imagen usando matplotlib
    plt.imshow(image_array, cmap='gray')  # 'gray' para mostrar la imagen en escala de grises
    plt.title(etiqueta[data[num_fila][0]])
    plt.axis('off')
    plt.show()
    
#%% Testeo de la función

visualizar_prenda(3)
#%% ===========================================================================
# =============================================================================
# Análisis exploratorio
# =============================================================================
# =============================================================================
#%% Exploración del dataframe

fashion_mnist.info() # cantidad de filas, columnas y tipo de datos
fashion_mnist['label'].unique() # cuántas son las labels
fashion_mnist['label'].value_counts() # qué cantidad hay de cada categoría
#%% Imagen promedio de cada prenda junto a la construcción del data frame de los 
# promedios de cada prenda

fashion_mnist_promedios_prenda = pd.DataFrame()
etiqueta = ['Remera/top', 'Pantalones', 'Suéter', 'Vestido', 'Abrigo', 'Sandalias', 'Camisa', 'Zapatillas', 'Cartera', 'Botas']
for j in range(10):
    prenda = fashion_mnist[fashion_mnist['label'] == j]
    fashion_mnist_promedios_prenda.at[j,'label'] = j
    imagen = np.zeros(784)
    for i in range(1, 785):
        fashion_mnist_promedios_prenda.at[j, f'pixel{i}'] = prenda[f'pixel{i}'].mean()
        imagen[i-1] = prenda[f'pixel{i}'].mean()
    plt.title(etiqueta[j])
    image_array = np.array(imagen).reshape(28, 28) 
    plt.imshow(image_array, cmap='plasma')  
    plt.axis('off')
    plt.show()

del imagen, prenda, j, i, image_array, etiqueta
#%% Nuevo dataFrame con los valores promedio de todas las prendas juntas

fashion_mnist_promedios = pd.DataFrame()
fashion_mnist_promedios['label'] = [10] 
for i in range(1,785):
    fashion_mnist_promedios[f'pixel{i}'] = [fashion_mnist[f'pixel{i}'].mean()]

del i 
#%% Imagen de los valores promedios de todas las prendas juntas

etiqueta = ['Remera/top', 'Pantalones', 'Suéter', 'Vestido', 'Abrigo', 'Sandalias', 'Camisa', 'Zapatillas', 'Cartera', 'Botas']
imagen_prom = np.zeros(784)
for i in range(1, 785):
    imagen_prom[i-1] = fashion_mnist_promedios[f'pixel{i}']
image_array = np.array(imagen_prom).reshape(28, 28) 
plt.title('Imagen promedio')
plt.imshow(image_array, cmap='Blues')  
plt.axis('off')
plt.show()

del etiqueta, i, image_array, imagen_prom
#%% ===========================================================================
# Representación visual de la comparación entre dos prendas promedio, 
# pantalones y zapatillas 
# =============================================================================
#%% Imagenes superpuestas

etiqueta = ['Remera/top', 'Pantalones', 'Suéter', 'Vestido', 'Abrigo', 'Sandalias',
            'Camisa', 'Zapatillas', 'Cartera', 'Botas']

num_fila1 = 1 #pantalones
num_fila2 = 7 #zapatillas

data = fashion_mnist_promedios_prenda.values
pixeles1 = data[num_fila1][1:]
imagen1 = np.array(pixeles1).reshape(28, 28)
pixeles2 = data[num_fila2][1:]
imagen2 = np.array(pixeles2).reshape(28, 28)
plt.imshow(imagen1, cmap='Grays')  
plt.axis('off')
plt.imshow(imagen2, cmap='Blues', alpha=0.5)  
plt.axis('off')
plt.title(f'{etiqueta[int(data[num_fila1][0])]} vs {etiqueta[int(data[num_fila2][0])]}')
plt.show()

del imagen1, imagen2
#%% Gráfico de valor de pixel promedio por fila

# Calculo de promedio de filas, para poder visualizar 28 valores en vez de 784
prom_filas1 = np.zeros(28)
prom_filas2 = np.zeros(28)
j = 0
for i in range(1,758,28):
    prom1 = data[num_fila1][i:i+27].mean()
    prom2 = data[num_fila2][i:i+27].mean()
    prom_filas1[j] = prom1
    prom_filas2[j] = prom2
    j += 1

# Grafico de los valores de promedios de las filas de ambas prendas
sns.scatterplot(x=np.arange(1,29), y=prom_filas1)
sns.scatterplot(x=np.arange(1,29), y=prom_filas2).set(
                    title='Tonalidad promedio por fila de pantalones y zapatillas', 
                    xlabel='Fila de imagen', ylabel='Promedio de fila de pixeles')
plt.xticks(np.arange(0,29,2))
plt.legend(labels=['Pantalones', 'Zapatillas'], title='Prenda')

del prom_filas1, prom_filas2, j, i, prom1, prom2
del pixeles1, pixeles2, num_fila1, num_fila2
#%% ===========================================================================
# Representación visual de la comparación entre suéter y camisa
# =============================================================================
#%% Imagenes superpuestas

num_fila1 = 2 #suéter
num_fila2 = 6 #camisa

pixeles1 = data[num_fila1][1:]
imagen1 = np.array(pixeles1).reshape(28, 28)
pixeles2 = data[num_fila2][1:]
imagen2 = np.array(pixeles2).reshape(28, 28)
plt.imshow(imagen1, cmap='Grays')  
plt.axis('off')
plt.imshow(imagen2, cmap='Blues', alpha=0.5)  
plt.axis('off')
plt.title(f'{etiqueta[int(data[num_fila1][0])]} vs {etiqueta[int(data[num_fila2][0])]}')
plt.show()

del imagen1, imagen2
#%% Gráfico de valor de pixel promedio por fila

# Calculo de promedio de filas, para poder visualizar 28 valores en vez de 784
prom_filas1 = np.zeros(28)
prom_filas2 = np.zeros(28)
j = 0
for i in range(1,758,28):
    prom1 = data[num_fila1][i:i+27].mean()
    prom2 = data[num_fila2][i:i+27].mean()
    prom_filas1[j] = prom1
    prom_filas2[j] = prom2
    j += 1
    
# Grafico de los valores de promedios de las filas de ambas prendas
sns.scatterplot(x=np.arange(1,29), y=prom_filas1)
sns.scatterplot(x=np.arange(1,29), y=prom_filas2).set(
                    title='Tonalidad promedio por fila de suéter y camisa', 
                    xlabel='Fila de imagen', ylabel='Promedio de fila de pixeles')
plt.xticks(np.arange(0,29,2))
plt.legend(labels=['Suéter', 'Camisa'], title='Prenda')

del num_fila1, num_fila2, data, pixeles1, pixeles2, etiqueta
del i, j, prom1, prom2, prom_filas1, prom_filas2
#%% ===========================================================================
# Comparación entre prendas de una misma clase
# =============================================================================
#%% Imagenes de desvio estandar de todas las prendas

etiqueta = ['Remera/top', 'Pantalones', 'Suéter', 'Vestido', 'Abrigo', 'Sandalias',
            'Camisa', 'Zapatillas', 'Cartera', 'Botas']

for j in range(10):
    prenda = fashion_mnist[fashion_mnist['label'] == j]
    imagen = np.zeros(784)
    for i in range(1, 785):
        imagen[i-1] = prenda[f'pixel{i}'].std()
    plt.title(etiqueta[j])
    image_array = np.array(imagen).reshape(28, 28) 
    plt.imshow(image_array, cmap='plasma')  
    plt.axis('off')
    plt.show()
    
del j, i, etiqueta,prenda,image_array, imagen
#%% =============================================================================
# Visualizacion del desvio de sandialias
# =============================================================================
#%% Comparación del promedio de las filas del promedio general, con el promedio 
# de las filas de 10 sandalias al azar

data1 = fashion_mnist_promedios_prenda.values
num_fila = 5 # sandalias
prom_filas1 = np.zeros(28)
j = 0
for i in range(1,758,28):
    prom = data1[num_fila][i:i+27].mean()
    prom_filas1[j] = prom
    j += 1

data2 = fashion_mnist[fashion_mnist['label'] == 5].values
data2 = data2[:10,1:]
prom_filas2 = np.zeros((10,28))

for k in range(10):
    j = 0
    for i in range(1,758,28):
        prom = data2[k][i:i+27].mean()
        prom_filas2[k,j] = prom
        j += 1

sns.scatterplot(x=np.arange(1,29), y=prom_filas1).set(
                        title='Tonalidad promedio por fila de 10 sandalias contra el promedio', 
                        xlabel='Fila de imagen', ylabel='Promedio de pixel')
for i in range(10):
    sns.scatterplot(x=np.arange(1,29), y=prom_filas2[i,:], marker='x')

plt.xticks(np.arange(0,29,2))
plt.legend(labels=['Promedio de todas las sandalias'])

del i, j, data1, data2, k, num_fila, prom, prom_filas1, prom_filas2
#%% ===========================================================================
# Visualizacion del desvio de pantalones
# =============================================================================
#%% Comparación del promedio de las filas del promedio general, con el promedio 
# de las filas de 10 pantalones al azar

data1 = fashion_mnist_promedios_prenda.values
num_fila = 1 # pantalones
prom_filas1 = np.zeros(28)
j = 0
for i in range(1,758,28):
    prom = data1[num_fila][i:i+27].mean()
    prom_filas1[j] = prom
    j += 1

data2 = fashion_mnist[fashion_mnist['label'] == 1].values
data2 = data2[:10,1:]
prom_filas2 = np.zeros((10,28))

for k in range(10):
    j = 0
    for i in range(1,758,28):
        prom = data2[k][i:i+27].mean()
        prom_filas2[k,j] = prom
        j += 1

sns.scatterplot(x=np.arange(1,29), y=prom_filas1).set(
                        title='Tonalidad promedio por fila de 10 pantalones contra el promedio', 
                        xlabel='fila de imagen', ylabel='promedio de pixel')
for i in range(10):
    sns.scatterplot(x=np.arange(1,29), y=prom_filas2[i,:], marker='x')

plt.xticks(np.arange(0,29,2))
plt.legend(labels=['promedio de todos los pantalones'])

del data1, data2, i, j, k, num_fila,  prom, prom_filas1, prom_filas2
#%% ===========================================================================
# =============================================================================
# kNN
# =============================================================================
# =============================================================================
#%% Nos quedamos con la porción del data set a utilizar y nos fijamos si está balanceado

remeras_pantalones = fashion_mnist[fashion_mnist['label'] <= 1]    
remeras_pantalones['label'].value_counts() # Sí, esta balanceado
#%% Dividimos en datatest y datatrain manteniendo la distribución de las clases
X = remeras_pantalones.drop(columns = ['label'])
y = remeras_pantalones[['label']]

X_train, X_test, y_train, y_test = train_test_split(X, y , test_size= 0.15, random_state= 7, stratify= y)
#%% Agarramos 3 atributos con diferentes criterios

# Media max remeras, media max pantalones, maxima diferencia promedio entre la media de dos pixeles
pixel_max_remeras = fashion_mnist_promedios_prenda[fashion_mnist_promedios_prenda['label']==0].idxmax(axis='columns')
pixel_max_pantalones = fashion_mnist_promedios_prenda[fashion_mnist_promedios_prenda['label']==1].idxmax(axis='columns')
diferencias = fashion_mnist_promedios_prenda[fashion_mnist_promedios_prenda['label'] <= 1].diff(axis=0)
diferencias = diferencias.drop(columns = 'label')
diferencias = diferencias[diferencias['pixel1'] < 0] # me quedo con la fila de numeros
diferencias = diferencias.abs()
max_dif = diferencias.idxmax(axis='columns')[1]
pixel_max_remeras = pixel_max_remeras[0]
pixel_max_pantalones = pixel_max_pantalones[1]

max_medias= X_train[[pixel_max_remeras, pixel_max_pantalones, max_dif]]

# =============================================================================
# Maxima diferencia

diferencias = fashion_mnist_promedios_prenda[fashion_mnist_promedios_prenda['label'] <= 1].diff(axis=0)
diferencias = diferencias.drop(columns = 'label')
diferencias = diferencias[diferencias['pixel1'] < 0] # me quedo con la fila de numeros
diferencias = diferencias.abs()
atributo1 = diferencias.idxmax(axis='columns')[1]
diferencias = diferencias.drop(columns = atributo1)
atributo2 = diferencias.idxmax(axis='columns')[1]
diferencias = diferencias.drop(columns = atributo2)
atributo3 = diferencias.idxmax(axis='columns')[1]

max_diferencias = X_train[[atributo1, atributo2, atributo3]]

# =============================================================================
# Espacio entre pantalones

atributo1 = 'pixel406'
atributo2 = 'pixel547'
atributo3 = 'pixel742'

espacio_pantalones = X_train[[atributo1, atributo2, atributo3]]

# =============================================================================
# Mangas de remera

atributo1 = 'pixel231'
atributo2 = 'pixel247'
atributo3 = 'pixel92'

mangas_remera = X_train[[atributo1, atributo2, atributo3]]

# =============================================================================
# Primeros pixeles

primeros_pixeles = X_train[['pixel1', 'pixel2', 'pixel3']]

# =============================================================================
# Últimos pixeles

ultimos_pixeles = X_train[['pixel784', 'pixel783', 'pixel782']]

# =============================================================================
# Pixeles random

random.seed(0)
numeros_random = [random.randint(1, 785) for _ in range(3)]

pixeles_random = X_train[[f'pixel{numeros_random[0]}', f'pixel{numeros_random[1]}', f'pixel{numeros_random[2]}']]

# =============================================================================
# KNNs
X_trains_armados = [max_medias, max_diferencias, espacio_pantalones, mangas_remera, primeros_pixeles, ultimos_pixeles, pixeles_random]
resultados = []
for i in range(7):
    hyper_params = {'n_neighbors' : [10,11,12,13,14,15,16,17,18,19,20]}
    kneigh = KNeighborsRegressor()
    clf = GridSearchCV(estimator=kneigh, param_grid=hyper_params, cv = 5)
    search = clf.fit(X_trains_armados[i], y_train)
    resultados.append(search.best_params_)
    resultados.append(search.best_score_)

# Armamos una tabla con los resultados del GridSearch
X_trains_armados = ['max_medias', 'max_diferencias', 'espacio_pantalones', 'mangas_remera', 'primeros_pixeles', 'ultimos_pixeles', 'pixeles_random']
resultado = pd.DataFrame(columns=['nombre_subconjunto', 'mejor_k', 'mejor_score'])
for i in range(7):
    resultado.at[i, 'nombre_subconjunto'] = str(X_trains_armados[i])
    resultado.at[i, 'mejor_k'] = resultados[2*i]['n_neighbors']
    resultado.at[i, 'mejor_score'] = resultados[2*i+1]

# =============================================================================
# Probamos para distinta cantidad de atributos según el criterio de diferencia máxima

atributos_prueba = []
for cant_atributos in [7,74,185,371,557]:
    diferencias = fashion_mnist_promedios_prenda[fashion_mnist_promedios_prenda['label'] <= 1].diff(axis=0)
    diferencias = diferencias.drop(columns = 'label')
    diferencias = diferencias[diferencias['pixel1'] < 0] # me quedo con la fila de numeros
    diferencias = diferencias.abs()
    atributos = []
    for _ in range(cant_atributos):
        atributo = diferencias.idxmax(axis='columns')[1]
        diferencias = diferencias.drop(columns = atributo)
        atributos.append(atributo)
    atributos_prueba.append(atributos)

scores = []
for i in range(5):
    max_diferencias = X_train[atributos_prueba[i]]
    test = X_test[atributos_prueba[i]]
    kneigh = KNeighborsRegressor(n_neighbors=18)
    kneigh.fit(max_diferencias, y_train)
    scores.append(kneigh.score(test, y_test))

# Grafico de los scores
plt.scatter([7,74,185,371,557], scores)
plt.xlabel('Cantidad de atributos utilizados')
plt.ylabel('Score')
plt.title('Presición de KNN por cantidad de atributos')

del atributo1, atributo2, atributo3, atributos, atributo, atributos_prueba
del cant_atributos, clf, diferencias, espacio_pantalones, hyper_params, i, kneigh
del mangas_remera, max_dif, max_diferencias, max_medias, numeros_random,
del pixel_max_pantalones, pixel_max_remeras, pixeles_random, primeros_pixeles
del resultado, resultados, scores, search, test, ultimos_pixeles, X_trains_armados
#%% Probamos el método de KNN para distintas cantidades de atributos y distintas ks

pixeles = np.arange(1,785)
random.shuffle(pixeles)
atributos_prueba = []
for cant_atributos in range(5,785,10):
    atributos = []
    for i in range(cant_atributos):
        atributo = f'pixel{pixeles[i]}'
        atributos.append(atributo)
    atributos_prueba.append(atributos)
    random.shuffle(pixeles)

scores = pd.DataFrame(columns= ['cant_atributos', 'k', 'score'])
j = 0
cant = 5
for i in range(78):
    data_random = X_train[atributos_prueba[i]]
    test = X_test[atributos_prueba[i]]
    for k in range(1,10):
        scores.at[j,'cant_atributos'] = cant
        scores.at[j,'k'] = k
        kneigh = KNeighborsRegressor(n_neighbors=k)
        kneigh.fit(data_random, y_train)
        scores.at[j,'score'] = kneigh.score(test, y_test)
        j += 1
    cant += 10
            
# Grafico de los scores
sns.scatterplot(x=scores['cant_atributos'], y=scores['score'], hue=scores['k'], palette='Set2')
plt.xticks(np.arange(5,785,50))
plt.title('Presición de KNN por cantidad de atributos y k')

del X, y, X_train, X_test, y_train, y_test, remeras_pantalones, atributo, i, j, k, test
del atributos, atributos_prueba, cant, cant_atributos, data_random, kneigh, pixeles, scores
#%%
# =============================================================================
# =============================================================================
# Árbol de decisión
# =============================================================================
# =============================================================================
#%% Dividimos en data train y data test  

X = fashion_mnist.drop(columns = ['label'])
y = fashion_mnist[['label']]

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size= 0.15, random_state= 7, stratify= y)
#%% Primero armamos un arbol de altura infinita para ver la maxima profundidad del arbol

arbol_altura_inf=DecisionTreeClassifier()
arbol_altura_inf.fit(X_train, y_train)
print(arbol_altura_inf.get_depth())

del arbol_altura_inf
#%% Ahora que sabemos que la maxima profundidad es 51, probamos evaluando valores de altura posibles
# entre 4 y 51, criterios gini y entropy y dada la gran gran cantidad de datos vamos a usar solo 5 folds

profundidad =np.arange(4,51)
hyper_params = {'criterion' :["gini", "entropy"], 'max_depth' : profundidad}
mejor_arbol = DecisionTreeClassifier()
clf = GridSearchCV(estimator=mejor_arbol, param_grid=hyper_params, cv = 5)
search = clf.fit(X_train, y_train)
print(search.best_params_)
print(search.best_score_)
 
del mejor_arbol, profundidad, hyper_params, clf, search
#%% Ahora que conocemos los mejores parametros vamos a armar el mejor arbol

arbol_final=DecisionTreeClassifier(criterion='entropy', max_depth=12)
arbol_final.fit(X_train, y_train)
#%% Vamos a evaluar nuestro arbol. Para eso vamos a medir la accuracy, la precision y el recall

y_pred = arbol_final.predict(X_test)

# Score
print(arbol_final.score(X_test, y_test))
print(accuracy_score(y_test, y_pred))

# Accuracy
 
# Precision
print(precision_score(y_test,y_pred, average='micro'))

print(recall_score(y_test, y_pred , average='micro'))

print(f1_score(y_test, y_pred, average='micro'))

# Medir precisión y recall???

del X, y, X_train, X_test, y_train, y_test, y_pred, arbol_final
#%%
del fashion_mnist, fashion_mnist_promedios, fashion_mnist_promedios_prenda
