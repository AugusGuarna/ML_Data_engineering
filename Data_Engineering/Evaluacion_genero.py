"""


Integrantes: Barracchia, Azul ; Guarnaccio, Augusto ; Sigal Aguirre, Mario.

Contenido: importación de dataframes originales, limpieza de estos, armado 
dataframes con datos de calidad y relevantes a nuestro objetivo, consultas
hechas con SQL, gráficos con matplotlib y seaborn.

"""


import pandas as pd
from inline_sql import sql, sql_val
import matplotlib.pyplot as plt
import seaborn as sns

# Dataframes originales
# =============================================================================
operadores_organicos= pd.read_csv('./TablasOriginales/padron-de-operadores-organicos-certificados.csv')

establecimientos_productivos = pd.read_csv('./TablasOriginales/distribucion_establecimientos_productivos_sexo.csv')

localidades = pd.read_csv('./TablasOriginales/localidad_bahra.csv')

clae = pd.read_csv('./TablasOriginales/clae_agg.csv')



# Ejercicio e)
# =============================================================================

df_Operadores_organicos = pd.DataFrame(columns=['id','establecimiento', 'razón_social', 'id_provincia', 'id_departamento'])

df_Producto = pd.DataFrame(columns=['producto', 'clae2']) 

df_Departamento = pd.DataFrame(columns=['id', 'departamento', 'id_provincia'])

df_Provincia = pd.DataFrame(columns=['id', 'provincia'])

df_Establecimiento_productivo = pd.DataFrame(columns=['id', 'clae2', 'proporción_mujeres', 'id_departamento'])

df_CLAE = pd.DataFrame(columns=[ 'clae2', 'clae2_desc'])

# Relación entre operadores orgánicos y producto

df_Relacion_Produce = pd.DataFrame(columns=['id_op_or', 'producto'])


# Ejercicio f) - Limpieza 

# Limpieza operadores orgánicos
# =============================================================================
# Agregamos una clave
for i in range(len(operadores_organicos)):
    operadores_organicos.at[i, 'id'] = i


limpieza_operadores_organicos = """
                                SELECT id, REGEXP_REPLACE(establecimiento, '\\bNC\\b', 'ESTABLECIMIENTO ÚNICO') AS establecimiento, 
                                    "razón social" AS razón_social, departamento, 
                                    REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(productos,':',','), ' Y ',', '),'+',','),'-',','),'?',',') AS productos,
                                    provincia_id AS id_provincia
                                FROM operadores_organicos;
                                """
operadores_organicos = sql^limpieza_operadores_organicos


limpieza_operadores_organicos = """
                                SELECT *, TRIM(UNNEST(string_to_array(productos, ','))) AS producto
                                FROM operadores_organicos
                                """
operadores_organicos = sql^limpieza_operadores_organicos


limpieza_operadores_organicos = """
                                SELECT id, establecimiento, razón_social, departamento, 
                                    id_provincia, REPLACE(REPLACE(REPLACE(producto, '(', ''), ')', ''), '.', '') AS producto
                                FROM operadores_organicos
                                ORDER BY id_provincia ASC
                                """
operadores_organicos = sql^limpieza_operadores_organicos


# Limpieza localidades
# =============================================================================
limpieza_localidades = """
                        SELECT DISTINCT 
                            nombre_geografico AS asentamiento,    
                            REPLACE(codigo_indec_departamento,'02001,02002,02003,02004,02005,02006,02007,02008,02009,02010,02011,02012,02013,02014,02015', '02001') AS id_departamento,
                            REPLACE(nombre_departamento,'Comuna 1,Comuna 10,Comuna 11,Comuna 12,Comuna 13,Comuna 14,Comuna 15,Comuna 2,Comuna 3,Comuna 4,Comuna 5,Comuna 6,Comuna 7,Comuna 8,Comuna 9', 'CIUDAD AUTONOMA BUENOS AIRES') AS departamento,
                            codigo_indec_provincia AS id_provincia, 
                            nombre_provincia AS provincia
                        FROM localidades                         
                        ORDER BY id_provincia ASC, id_departamento ASC
                        """
localidades = sql^limpieza_localidades   


limpieza_localidades = """
                       SELECT id_departamento, id_provincia, provincia,
                           REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(UPPER(asentamiento),'Á','A'),'É','E'),'Í','I'),'Ó','O'),'Ú','U') AS asentamiento,
                           REPLACE(REPLACE(REPLACE(REPLACE(REPLACE(UPPER(departamento),'Á','A'),'É','E'),'Í','I'),'Ó','O'),'Ú','U') AS departamento
                       FROM localidades
                       """
localidades = sql^limpieza_localidades

# Buscamos los departamentos con el mismo id pero de distintas provincias para cambiarlos a mano

consultaAux = """
              SELECT DISTINCT id_departamento, departamento, id_provincia, provincia
              FROM localidades
              """

repetidos = sql^consultaAux
consultaAux = """
            SELECT DISTINCT id_departamento, count(id_departamento) AS cant
            FROM repetidos
            GROUP BY id_departamento
            HAVING cant > 1
            """
repetidos = sql^consultaAux


# Cambiamos los ids a mano

dataframe_chiquito= """
                    SELECT * 
                    FROM localidades
                    WHERE id_departamento in (10070,86084,26007,74056)
                    ORDER BY departamento ASC, asentamiento ASC
                    """
localidades1 = sql^dataframe_chiquito

localidades_sin_id_repetido = """
                              SELECT * 
                              FROM localidades
                              EXCEPT
                              SELECT *
                              FROM localidades1
                              """
localidades = sql^localidades_sin_id_repetido

# Cambiamos valores a mano

localidades1.at[0,'id_departamento'] = '95001'
localidades1.at[5,'id_departamento'] = '95002'
localidades1.at[22 ,'id_departamento'] = '95003'
localidades1.at[23 ,'id_departamento'] = '95003' # Son dos asentamientos de un mismo departamento
localidades1.at[34 ,'id_departamento'] = '95004'

localidades_sin_repetidos = """
                            SELECT * 
                            FROM localidades
                        UNION
                            SELECT *
                            FROM localidades1
                            """
localidades = sql^localidades_sin_repetidos


# Limpieza clae
# =============================================================================
limpieza_clae = """
                SELECT DISTINCT clae2, clae2_desc
                FROM clae
                WHERE letra = 'A' or clae2 in (10,11,13,20,21,999)
                ORDER BY clae2 ASC
              """
clae = sql^limpieza_clae

# Limpieza establecimientos productivos
# =============================================================================
limpieza_establecimiento_productivo = """
                                        SELECT *
                                        FROM establecimientos_productivos as ep
                                        WHERE ep.clae2 IN (
                                            SELECT clae2
                                            FROM clae
                                            )
                                        ORDER BY ID ASC, clae2 ASC
                                      """
establecimiento_productivo = sql^limpieza_establecimiento_productivo

limpieza_establecimiento_productivo = """
                                       SELECT *,
                                            CASE 
                                               WHEN provincia != 'CABA' 
                                                   THEN in_departamentos
                                                   ELSE '2001'
                                            END AS id_departamento
                                        FROM establecimiento_productivo
                                      """
                                      
establecimiento_productivo = sql^limpieza_establecimiento_productivo    

limpieza_establecimiento_productivo = """
                                       SELECT *,
                                            CASE 
                                               WHEN id_departamento < 10000 
                                                   THEN CONCAT('0', id_departamento)
                                                   ELSE id_departamento
                                            END AS id_departamento_final
                                        FROM establecimiento_productivo
                                      """
                                      
establecimiento_productivo = sql^limpieza_establecimiento_productivo 

limpieza_establecimiento_productivo = """
                                       SELECT *,
                                            CASE
                                               WHEN id_departamento_final = 94008 
                                               THEN 94007
                                               WHEN id_departamento_final = 94015 
                                               THEN 94014
                                               ELSE id_departamento_final
                                            END AS id_departamento_final2
                                        FROM establecimiento_productivo
                                      """
establecimiento_productivo = sql^limpieza_establecimiento_productivo  

limpieza_establecimiento_productivo =  """
                                        SELECT ID AS id, id_departamento_final2 AS id_departamento,
                                            clae2, proporcion_mujeres
                                        FROM establecimiento_productivo
                                        """
establecimiento_productivo = sql^limpieza_establecimiento_productivo                                         


# Armado de los dataframes

# Armado dataframe de operadores orgánicos
# =============================================================================                               
armado_operadores_organicos = """
                              SELECT DISTINCT id, establecimiento, razón_social, departamento, id_provincia
                              FROM operadores_organicos
                              ORDER BY id ASC
                              """
df_Operadores_organicos = sql^armado_operadores_organicos

# Más adelante cuando se hagan las relaciones se pondrá el id_departamento reemplazando departamento

# Armado dataframe de departamento
# =============================================================================
armado_departamento = """
                      SELECT DISTINCT id_departamento AS id, departamento, id_provincia
                      FROM localidades                         
                      """
df_Departamento = sql^armado_departamento


# Armado dataframe de provincia
# =============================================================================
armado_provincia = """
                      SELECT DISTINCT id_provincia AS id, provincia 
                      FROM localidades
                     """
df_Provincia= sql^armado_provincia

# Armado dataframe establecimiento productivo
# =============================================================================
armado_establecimiento_productivo = """
                                    SELECT *
                                    FROM establecimiento_productivo
                                    """
df_Establecimiento_productivo = sql^armado_establecimiento_productivo


# Armado dataframe de CLAE
# =============================================================================
armado_clae = """
                SELECT *
                FROM clae
                """
df_CLAE = sql^armado_clae


# Armado dataframe de producto
# =============================================================================
armado_producto = """
                 SELECT DISTINCT producto
                 FROM operadores_organicos
                 ORDER BY producto ASC
                 """
df_Producto = sql^armado_producto    
# =============================================================================
# Para asignar la clae correspondiente a cada producto, como no encontramos un patrón
# ni una buena forma de hacerlo con las queries decidimos hacerlo a mano. 
# En lo personal preferimos hacerlo con pandas porque simplemente era copiar y pegar
# unas lineas de codigo lo que resultaba más rápido y menos tedioso que tener que hacerlo
# con un excel.
# =============================================================================
df_Producto['clae2'] = None

df_Producto.at[0, 'clae2'] = 1
df_Producto.at[1, 'clae2'] = 10
df_Producto.at[2, 'clae2'] = 10
df_Producto.at[3, 'clae2'] = 10
df_Producto.at[4, 'clae2'] = 10
df_Producto.at[5, 'clae2'] = 10
df_Producto.at[6, 'clae2'] = 10
df_Producto.at[7, 'clae2'] = 10
df_Producto.at[8, 'clae2'] = 10
df_Producto.at[9, 'clae2'] = 10
df_Producto.at[10, 'clae2'] = 20
df_Producto.at[11, 'clae2'] = 10
df_Producto.at[12, 'clae2'] = 10
df_Producto.at[13, 'clae2'] = 10
df_Producto.at[14, 'clae2'] = 10
df_Producto.at[15, 'clae2'] = 10
df_Producto.at[16, 'clae2'] = 10
df_Producto.at[17, 'clae2'] = 10
df_Producto.at[18, 'clae2'] = 10
df_Producto.at[19, 'clae2'] = 21
df_Producto.at[20, 'clae2'] = 21
df_Producto.at[21, 'clae2'] = 21
df_Producto.at[22, 'clae2'] = 21
df_Producto.at[23, 'clae2'] = 21
df_Producto.at[24, 'clae2'] = 21
df_Producto.at[25, 'clae2'] = 21
df_Producto.at[26, 'clae2'] = 10
df_Producto.at[27, 'clae2'] = 10
df_Producto.at[28, 'clae2'] = 10
df_Producto.at[29, 'clae2'] = 10
df_Producto.at[30, 'clae2'] = 10
df_Producto.at[31, 'clae2'] = 10
df_Producto.at[32, 'clae2'] = 10
df_Producto.at[33, 'clae2'] = 1
df_Producto.at[34, 'clae2'] = 1
df_Producto.at[35, 'clae2'] = 1
df_Producto.at[36, 'clae2'] = 1
df_Producto.at[37, 'clae2'] = 1
df_Producto.at[38, 'clae2'] = 1
df_Producto.at[39, 'clae2'] = 1
df_Producto.at[40, 'clae2'] = 1
df_Producto.at[41, 'clae2'] = 1
df_Producto.at[42, 'clae2'] = 1
df_Producto.at[43, 'clae2'] = 1
df_Producto.at[44, 'clae2'] = 10
df_Producto.at[45, 'clae2'] = 1
df_Producto.at[46, 'clae2'] = 1
df_Producto.at[47, 'clae2'] = 3
df_Producto.at[48, 'clae2'] = 10
df_Producto.at[49, 'clae2'] = 1
df_Producto.at[50, 'clae2'] = 1
df_Producto.at[51, 'clae2'] = 1
df_Producto.at[52, 'clae2'] = 1
df_Producto.at[53, 'clae2'] = 1
df_Producto.at[54, 'clae2'] = 1
df_Producto.at[55, 'clae2'] = 1
df_Producto.at[56, 'clae2'] = 1
df_Producto.at[57, 'clae2'] = 1
df_Producto.at[58, 'clae2'] = 1
df_Producto.at[59, 'clae2'] = 1
df_Producto.at[60, 'clae2'] = 20
df_Producto.at[61, 'clae2'] = 20
df_Producto.at[62, 'clae2'] = 20
df_Producto.at[63, 'clae2'] = 1
df_Producto.at[64, 'clae2'] = 1
df_Producto.at[65, 'clae2'] = 1
df_Producto.at[66, 'clae2'] = 1
df_Producto.at[67, 'clae2'] = 1
df_Producto.at[68, 'clae2'] = 1
df_Producto.at[69, 'clae2'] = 1
df_Producto.at[70, 'clae2'] = 1
df_Producto.at[71, 'clae2'] = 1
df_Producto.at[72, 'clae2'] = 1
df_Producto.at[73, 'clae2'] = 1
df_Producto.at[74, 'clae2'] = 1
df_Producto.at[75, 'clae2'] = 1
df_Producto.at[76, 'clae2'] = 1
df_Producto.at[77, 'clae2'] = 1
df_Producto.at[78, 'clae2'] = 1
df_Producto.at[79, 'clae2'] = 1
df_Producto.at[80, 'clae2'] = 999
df_Producto.at[81, 'clae2'] = 13
df_Producto.at[82, 'clae2'] = 1
df_Producto.at[83, 'clae2'] = 1
df_Producto.at[84, 'clae2'] = 1
df_Producto.at[85, 'clae2'] = 1
df_Producto.at[86, 'clae2'] = 1
df_Producto.at[87, 'clae2'] = 1
df_Producto.at[88, 'clae2'] = 1
df_Producto.at[89, 'clae2'] = 1
df_Producto.at[90, 'clae2'] = 1
df_Producto.at[91, 'clae2'] = 1
df_Producto.at[92, 'clae2'] = 1
df_Producto.at[93, 'clae2'] = 1
df_Producto.at[94, 'clae2'] = 1
df_Producto.at[95, 'clae2'] = 1
df_Producto.at[96, 'clae2'] = 1
df_Producto.at[97, 'clae2'] = 1
df_Producto.at[98, 'clae2'] = 1
df_Producto.at[99, 'clae2'] = 1
df_Producto.at[100, 'clae2'] = 1
df_Producto.at[101, 'clae2'] = 1
df_Producto.at[102, 'clae2'] = 1
df_Producto.at[103, 'clae2'] = 1
df_Producto.at[104, 'clae2'] = 1
df_Producto.at[105, 'clae2'] = 1
df_Producto.at[106, 'clae2'] = 1
df_Producto.at[107, 'clae2'] = 1
df_Producto.at[108, 'clae2'] = 1
df_Producto.at[109, 'clae2'] = 1
df_Producto.at[110, 'clae2'] = 1
df_Producto.at[111, 'clae2'] = 1
df_Producto.at[112, 'clae2'] = 1
df_Producto.at[113, 'clae2'] = 1
df_Producto.at[114, 'clae2'] = 1
df_Producto.at[115, 'clae2'] = 21
df_Producto.at[116, 'clae2'] = 1
df_Producto.at[117, 'clae2'] = 1
df_Producto.at[118, 'clae2'] = 1
df_Producto.at[119, 'clae2'] = 1
df_Producto.at[120, 'clae2'] = 1
df_Producto.at[121, 'clae2'] = 1
df_Producto.at[122, 'clae2'] = 1
df_Producto.at[123, 'clae2'] = 1
df_Producto.at[124, 'clae2'] = 10 
df_Producto.at[125, 'clae2'] = 10
df_Producto.at[126, 'clae2'] = 10
df_Producto.at[127, 'clae2'] = 1
df_Producto.at[128, 'clae2'] = 1
df_Producto.at[129, 'clae2'] = 1
df_Producto.at[130, 'clae2'] = 1
df_Producto.at[131, 'clae2'] = 1
df_Producto.at[132, 'clae2'] = 1
df_Producto.at[133, 'clae2'] = 1
df_Producto.at[134, 'clae2'] = 1
df_Producto.at[135, 'clae2'] = 1
df_Producto.at[136, 'clae2'] = 1
df_Producto.at[137, 'clae2'] = 1
df_Producto.at[138, 'clae2'] = 1
df_Producto.at[139, 'clae2'] = 1
df_Producto.at[140, 'clae2'] = 1
df_Producto.at[141, 'clae2'] = 1
df_Producto.at[142, 'clae2'] = 999
df_Producto.at[143, 'clae2'] = 999
df_Producto.at[144, 'clae2'] = 999
df_Producto.at[145, 'clae2'] = 10
df_Producto.at[146, 'clae2'] = 10
df_Producto.at[147, 'clae2'] = 1
df_Producto.at[148, 'clae2'] = 1
df_Producto.at[149, 'clae2'] = 10
df_Producto.at[150, 'clae2'] = 10
df_Producto.at[151, 'clae2'] = 10
df_Producto.at[152, 'clae2'] = 21
df_Producto.at[153, 'clae2'] = 21
df_Producto.at[154, 'clae2'] = 21
df_Producto.at[155, 'clae2'] = 1
df_Producto.at[156, 'clae2'] = 1
df_Producto.at[157, 'clae2'] = 1
df_Producto.at[158, 'clae2'] = 1
df_Producto.at[159, 'clae2'] = 1
df_Producto.at[160, 'clae2'] = 1
df_Producto.at[161, 'clae2'] = 10
df_Producto.at[162, 'clae2'] = 10
df_Producto.at[163, 'clae2'] = 1
df_Producto.at[164, 'clae2'] = 1
df_Producto.at[165, 'clae2'] = 10
df_Producto.at[166, 'clae2'] = 21
df_Producto.at[167, 'clae2'] = 21
df_Producto.at[168, 'clae2'] = 21
df_Producto.at[169, 'clae2'] = 21
df_Producto.at[170, 'clae2'] = 1
df_Producto.at[171, 'clae2'] = 1
df_Producto.at[172, 'clae2'] = 1
df_Producto.at[173, 'clae2'] = 10
df_Producto.at[174, 'clae2'] = 1
df_Producto.at[175, 'clae2'] = 1
df_Producto.at[176, 'clae2'] = 11
df_Producto.at[177, 'clae2'] = 20
df_Producto.at[178, 'clae2'] = 1
df_Producto.at[179, 'clae2'] = 1
df_Producto.at[180, 'clae2'] = 10
df_Producto.at[181, 'clae2'] = 10
df_Producto.at[182, 'clae2'] = 10
df_Producto.at[183, 'clae2'] = 10
df_Producto.at[184, 'clae2'] = 10
df_Producto.at[185, 'clae2'] = 10
df_Producto.at[186, 'clae2'] = 999
df_Producto.at[187, 'clae2'] = 1
df_Producto.at[188, 'clae2'] = 3
df_Producto.at[189, 'clae2'] = 20
df_Producto.at[190, 'clae2'] = 20
df_Producto.at[191, 'clae2'] = 20
df_Producto.at[192, 'clae2'] = 20
df_Producto.at[193, 'clae2'] = 999
df_Producto.at[194, 'clae2'] = 1
df_Producto.at[195, 'clae2'] = 2
df_Producto.at[196, 'clae2'] = 10
df_Producto.at[197, 'clae2'] = 1
df_Producto.at[198, 'clae2'] = 10
df_Producto.at[199, 'clae2'] = 1
df_Producto.at[200, 'clae2'] = 1
df_Producto.at[201, 'clae2'] = 1
df_Producto.at[202, 'clae2'] = 1
df_Producto.at[203, 'clae2'] = 1
df_Producto.at[204, 'clae2'] = 1
df_Producto.at[205, 'clae2'] = 1
df_Producto.at[206, 'clae2'] = 10
df_Producto.at[207, 'clae2'] = 1
df_Producto.at[208, 'clae2'] = 1
df_Producto.at[209, 'clae2'] = 1
df_Producto.at[210, 'clae2'] = 1
df_Producto.at[211, 'clae2'] = 999
df_Producto.at[212, 'clae2'] = 10
df_Producto.at[213, 'clae2'] = 1
df_Producto.at[214, 'clae2'] = 1
df_Producto.at[215, 'clae2'] = 1
df_Producto.at[216, 'clae2'] = 1
df_Producto.at[217, 'clae2'] = 10
df_Producto.at[218, 'clae2'] = 21
df_Producto.at[219, 'clae2'] = 1
df_Producto.at[220, 'clae2'] = 1
df_Producto.at[221, 'clae2'] = 1
df_Producto.at[222, 'clae2'] = 1
df_Producto.at[223, 'clae2'] = 1
df_Producto.at[224, 'clae2'] = 1
df_Producto.at[225, 'clae2'] = 0
df_Producto.at[226, 'clae2'] = 1
df_Producto.at[227, 'clae2'] = 1
df_Producto.at[228, 'clae2'] = 999
df_Producto.at[229, 'clae2'] = 1
df_Producto.at[230, 'clae2'] = 2
df_Producto.at[231, 'clae2'] = 2
df_Producto.at[232, 'clae2'] = 1
df_Producto.at[233, 'clae2'] = 10
df_Producto.at[234, 'clae2'] = 10
df_Producto.at[235, 'clae2'] = 10
df_Producto.at[236, 'clae2'] = 10
df_Producto.at[237, 'clae2'] = 10
df_Producto.at[238, 'clae2'] = 10
df_Producto.at[239, 'clae2'] = 10
df_Producto.at[240, 'clae2'] = 10
df_Producto.at[241, 'clae2'] = 10
df_Producto.at[242, 'clae2'] = 10
df_Producto.at[243, 'clae2'] = 10
df_Producto.at[244, 'clae2'] = 10
df_Producto.at[245, 'clae2'] = 10
df_Producto.at[246, 'clae2'] = 10
df_Producto.at[247, 'clae2'] = 10
df_Producto.at[248, 'clae2'] = 10
df_Producto.at[249, 'clae2'] = 10
df_Producto.at[250, 'clae2'] = 1
df_Producto.at[251, 'clae2'] = 1
df_Producto.at[252, 'clae2'] = 1
df_Producto.at[253, 'clae2'] = 1
df_Producto.at[254, 'clae2'] = 1
df_Producto.at[255, 'clae2'] = 1
df_Producto.at[256, 'clae2'] = 21
df_Producto.at[257, 'clae2'] = 1
df_Producto.at[258, 'clae2'] = 1
df_Producto.at[259, 'clae2'] = 1
df_Producto.at[260, 'clae2'] = 1
df_Producto.at[261, 'clae2'] = 1
df_Producto.at[262, 'clae2'] = 1
df_Producto.at[263, 'clae2'] = 1
df_Producto.at[264, 'clae2'] = 1
df_Producto.at[265, 'clae2'] = 1
df_Producto.at[266, 'clae2'] = 1
df_Producto.at[267, 'clae2'] = 1
df_Producto.at[268, 'clae2'] = 999
df_Producto.at[269, 'clae2'] = 3
df_Producto.at[270, 'clae2'] = 1
df_Producto.at[271, 'clae2'] = 1
df_Producto.at[272, 'clae2'] = 11
df_Producto.at[273, 'clae2'] = 11
df_Producto.at[274, 'clae2'] = 11
df_Producto.at[275, 'clae2'] = 11
df_Producto.at[276, 'clae2'] = 11
df_Producto.at[277, 'clae2'] = 11
df_Producto.at[279, 'clae2'] = 11
df_Producto.at[280, 'clae2'] = 11
df_Producto.at[281, 'clae2'] = 11
df_Producto.at[282, 'clae2'] = 11
df_Producto.at[283, 'clae2'] = 11
df_Producto.at[284, 'clae2'] = 11
df_Producto.at[285, 'clae2'] = 11
df_Producto.at[286, 'clae2'] = 11
df_Producto.at[287, 'clae2'] = 11
df_Producto.at[288, 'clae2'] = 11
df_Producto.at[289, 'clae2'] = 11
df_Producto.at[290, 'clae2'] = 11
df_Producto.at[291, 'clae2'] = 11
df_Producto.at[292, 'clae2'] = 11
df_Producto.at[293, 'clae2'] = 11
df_Producto.at[294, 'clae2'] = 11
df_Producto.at[295, 'clae2'] = 11
df_Producto.at[296, 'clae2'] = 11
df_Producto.at[297, 'clae2'] = 11
df_Producto.at[298, 'clae2'] = 11
df_Producto.at[299, 'clae2'] = 11
df_Producto.at[300, 'clae2'] = 11
df_Producto.at[301, 'clae2'] = 1
df_Producto.at[302, 'clae2'] = 1
df_Producto.at[303, 'clae2'] = 10
df_Producto.at[304, 'clae2'] = 1
df_Producto.at[305, 'clae2'] = 13
df_Producto.at[306, 'clae2'] = 13
df_Producto.at[307, 'clae2'] = 13
df_Producto.at[308, 'clae2'] = 1
df_Producto.at[309, 'clae2'] = 2
df_Producto.at[310, 'clae2'] = 1
df_Producto.at[311, 'clae2'] = 1
df_Producto.at[312, 'clae2'] = 1
df_Producto.at[313, 'clae2'] = 1
df_Producto.at[314, 'clae2'] = 1
df_Producto.at[315, 'clae2'] = 1
df_Producto.at[316, 'clae2'] = 1
df_Producto.at[317, 'clae2'] = 1
df_Producto.at[318, 'clae2'] = 1
df_Producto.at[319, 'clae2'] = 1
df_Producto.at[320, 'clae2'] = 1
df_Producto.at[321, 'clae2'] = 1
df_Producto.at[322, 'clae2'] = 1
df_Producto.at[323, 'clae2'] = 1
df_Producto.at[324, 'clae2'] = 1
df_Producto.at[325, 'clae2'] = 1
df_Producto.at[326, 'clae2'] = 1
df_Producto.at[327, 'clae2'] = 1
df_Producto.at[328, 'clae2'] = 11
df_Producto.at[329, 'clae2'] = 1
df_Producto.at[330, 'clae2'] = 1
df_Producto.at[331, 'clae2'] = 1
df_Producto.at[332, 'clae2'] = 1
df_Producto.at[333, 'clae2'] = 10
df_Producto.at[334, 'clae2'] = 10
df_Producto.at[335, 'clae2'] = 10
df_Producto.at[336, 'clae2'] = 10
df_Producto.at[337, 'clae2'] = 10
df_Producto.at[338, 'clae2'] = 1
df_Producto.at[339, 'clae2'] = 1
df_Producto.at[340, 'clae2'] = 1
df_Producto.at[341, 'clae2'] = 10
df_Producto.at[342, 'clae2'] = 2
df_Producto.at[343, 'clae2'] = 21
df_Producto.at[344, 'clae2'] = 21
df_Producto.at[345, 'clae2'] = 1
df_Producto.at[346, 'clae2'] = 3
df_Producto.at[347, 'clae2'] = 1
df_Producto.at[348, 'clae2'] = 1
df_Producto.at[349, 'clae2'] = 1
df_Producto.at[350, 'clae2'] = 1
df_Producto.at[351, 'clae2'] = 1
df_Producto.at[352, 'clae2'] = 10
df_Producto.at[353, 'clae2'] = 1
df_Producto.at[354, 'clae2'] = 1
df_Producto.at[355, 'clae2'] = 1
df_Producto.at[356, 'clae2'] = 1
df_Producto.at[357, 'clae2'] = 1
df_Producto.at[358, 'clae2'] = 1
df_Producto.at[359, 'clae2'] = 1
df_Producto.at[360, 'clae2'] = 1
df_Producto.at[361, 'clae2'] = 10
df_Producto.at[362, 'clae2'] = 10
df_Producto.at[363, 'clae2'] = 999
df_Producto.at[364, 'clae2'] = 1
df_Producto.at[365, 'clae2'] = 1
df_Producto.at[366, 'clae2'] = 10
df_Producto.at[367, 'clae2'] = 1
df_Producto.at[368, 'clae2'] = 1
df_Producto.at[369, 'clae2'] = 1
df_Producto.at[370, 'clae2'] = 1
df_Producto.at[371, 'clae2'] = 10
df_Producto.at[372, 'clae2'] = 10
df_Producto.at[373, 'clae2'] = 10
df_Producto.at[374, 'clae2'] = 1
df_Producto.at[375, 'clae2'] = 1
df_Producto.at[376, 'clae2'] = 1
df_Producto.at[377, 'clae2'] = 1
df_Producto.at[378, 'clae2'] = 999
df_Producto.at[379, 'clae2'] = 2
df_Producto.at[380, 'clae2'] = 2
df_Producto.at[381, 'clae2'] = 10
df_Producto.at[382, 'clae2'] = 999
df_Producto.at[383, 'clae2'] = 1
df_Producto.at[384, 'clae2'] = 1
df_Producto.at[385, 'clae2'] = 1
df_Producto.at[386, 'clae2'] = 1
df_Producto.at[387, 'clae2'] = 1
df_Producto.at[388, 'clae2'] = 1
df_Producto.at[389, 'clae2'] = 1
df_Producto.at[390, 'clae2'] = 1
df_Producto.at[391, 'clae2'] = 1
df_Producto.at[392, 'clae2'] = 1 
df_Producto.at[393, 'clae2'] = 1
df_Producto.at[394, 'clae2'] = 1
df_Producto.at[395, 'clae2'] = 999
df_Producto.at[396, 'clae2'] = 999
df_Producto.at[397, 'clae2'] = 1
df_Producto.at[398, 'clae2'] = 1
df_Producto.at[399, 'clae2'] = 1
df_Producto.at[400, 'clae2'] = 1
df_Producto.at[401, 'clae2'] = 1
df_Producto.at[402, 'clae2'] = 1
df_Producto.at[403, 'clae2'] = 10
df_Producto.at[404, 'clae2'] = 1
df_Producto.at[405, 'clae2'] = 999
df_Producto.at[406, 'clae2'] = 10
df_Producto.at[407, 'clae2'] = 10
df_Producto.at[408, 'clae2'] = 10
df_Producto.at[409, 'clae2'] = 10
df_Producto.at[410, 'clae2'] = 10
df_Producto.at[411, 'clae2'] = 10
df_Producto.at[412, 'clae2'] = 1
df_Producto.at[413, 'clae2'] = 1
df_Producto.at[414, 'clae2'] = 1
df_Producto.at[415, 'clae2'] = 1
df_Producto.at[416, 'clae2'] = 1
df_Producto.at[417, 'clae2'] = 1
df_Producto.at[418, 'clae2'] = 3
df_Producto.at[419, 'clae2'] = 1
df_Producto.at[420, 'clae2'] = 1
df_Producto.at[421, 'clae2'] = 1
df_Producto.at[422, 'clae2'] = 1
df_Producto.at[423, 'clae2'] = 1
df_Producto.at[424, 'clae2'] = 10
df_Producto.at[425, 'clae2'] = 1
df_Producto.at[426, 'clae2'] = 3
df_Producto.at[427, 'clae2'] = 1
df_Producto.at[428, 'clae2'] = 1
df_Producto.at[429, 'clae2'] = 1
df_Producto.at[430, 'clae2'] = 1
df_Producto.at[431, 'clae2'] = 1
df_Producto.at[432, 'clae2'] = 1
df_Producto.at[433, 'clae2'] = 999
df_Producto.at[434, 'clae2'] = 1
df_Producto.at[435, 'clae2'] = 1
df_Producto.at[436, 'clae2'] = 1
df_Producto.at[437, 'clae2'] = 1
df_Producto.at[438, 'clae2'] = 1
df_Producto.at[439, 'clae2'] = 1
df_Producto.at[440, 'clae2'] = 1
df_Producto.at[441, 'clae2'] = 10
df_Producto.at[442, 'clae2'] = 1
df_Producto.at[443, 'clae2'] = 1
df_Producto.at[444, 'clae2'] = 1
df_Producto.at[445, 'clae2'] = 999
df_Producto.at[446, 'clae2'] = 10
df_Producto.at[447, 'clae2'] = 10
df_Producto.at[448, 'clae2'] = 10
df_Producto.at[449, 'clae2'] = 10
df_Producto.at[450, 'clae2'] = 10
df_Producto.at[451, 'clae2'] = 10
df_Producto.at[452, 'clae2'] = 10
df_Producto.at[453, 'clae2'] = 10
df_Producto.at[454, 'clae2'] = 10
df_Producto.at[455, 'clae2'] = 10
df_Producto.at[456, 'clae2'] = 10
df_Producto.at[457, 'clae2'] = 10
df_Producto.at[458, 'clae2'] = 10
df_Producto.at[459, 'clae2'] = 10
df_Producto.at[460, 'clae2'] = 10
df_Producto.at[461, 'clae2'] = 10
df_Producto.at[462, 'clae2'] = 10
df_Producto.at[463, 'clae2'] = 10
df_Producto.at[464, 'clae2'] = 10
df_Producto.at[465, 'clae2'] = 10
df_Producto.at[466, 'clae2'] = 10
df_Producto.at[467, 'clae2'] = 10
df_Producto.at[468, 'clae2'] = 10
df_Producto.at[469, 'clae2'] = 10
df_Producto.at[470, 'clae2'] = 10
df_Producto.at[471, 'clae2'] = 10
df_Producto.at[472, 'clae2'] = 10
df_Producto.at[473, 'clae2'] = 10
df_Producto.at[474, 'clae2'] = 10
df_Producto.at[475, 'clae2'] = 10
df_Producto.at[476, 'clae2'] = 10
df_Producto.at[477, 'clae2'] = 10
df_Producto.at[478, 'clae2'] = 10
df_Producto.at[479, 'clae2'] = 10
df_Producto.at[480, 'clae2'] = 10
df_Producto.at[481, 'clae2'] = 10
df_Producto.at[482, 'clae2'] = 1
df_Producto.at[483, 'clae2'] = 1
df_Producto.at[484, 'clae2'] = 1
df_Producto.at[485, 'clae2'] = 1
df_Producto.at[486, 'clae2'] = 1
df_Producto.at[487, 'clae2'] = 10
df_Producto.at[488, 'clae2'] = 10
df_Producto.at[489, 'clae2'] = 1
df_Producto.at[490, 'clae2'] = 10 
df_Producto.at[491, 'clae2'] = 1
df_Producto.at[492, 'clae2'] = 1
df_Producto.at[493, 'clae2'] = 1
df_Producto.at[494, 'clae2'] = 1
df_Producto.at[495, 'clae2'] = 1
df_Producto.at[496, 'clae2'] = 1
df_Producto.at[497, 'clae2'] = 1
df_Producto.at[498, 'clae2'] = 1
df_Producto.at[499, 'clae2'] = 1
df_Producto.at[500, 'clae2'] = 1
df_Producto.at[501, 'clae2'] = 1
df_Producto.at[502, 'clae2'] = 2
df_Producto.at[503, 'clae2'] = 1
df_Producto.at[504, 'clae2'] = 1
df_Producto.at[505, 'clae2'] = 1
df_Producto.at[506, 'clae2'] = 1
df_Producto.at[507, 'clae2'] = 1
df_Producto.at[508, 'clae2'] = 1
df_Producto.at[509, 'clae2'] = 1
df_Producto.at[510, 'clae2'] = 1
df_Producto.at[511, 'clae2'] = 1
df_Producto.at[512, 'clae2'] = 1
df_Producto.at[513, 'clae2'] = 1
df_Producto.at[514, 'clae2'] = 21
df_Producto.at[515, 'clae2'] = 21
df_Producto.at[516, 'clae2'] = 1
df_Producto.at[517, 'clae2'] = 11
df_Producto.at[518, 'clae2'] = 999
df_Producto.at[519, 'clae2'] = 999
df_Producto.at[520, 'clae2'] = 11
df_Producto.at[521, 'clae2'] = 1
df_Producto.at[522, 'clae2'] = 1
df_Producto.at[523, 'clae2'] = 1
df_Producto.at[524, 'clae2'] = 1
df_Producto.at[525, 'clae2'] = 10
df_Producto.at[526, 'clae2'] = 1
df_Producto.at[527, 'clae2'] = 999
df_Producto.at[528, 'clae2'] = 10
df_Producto.at[529, 'clae2'] = 11
df_Producto.at[530, 'clae2'] = 11
df_Producto.at[531, 'clae2'] = 11
df_Producto.at[532, 'clae2'] = 11
df_Producto.at[533, 'clae2'] = 11
df_Producto.at[534, 'clae2'] = 11
df_Producto.at[535, 'clae2'] = 11
df_Producto.at[536, 'clae2'] = 11
df_Producto.at[537, 'clae2'] = 11
df_Producto.at[538, 'clae2'] = 11
df_Producto.at[539, 'clae2'] = 11
df_Producto.at[540, 'clae2'] = 11
df_Producto.at[541, 'clae2'] = 11
df_Producto.at[542, 'clae2'] = 11
df_Producto.at[543, 'clae2'] = 11
df_Producto.at[544, 'clae2'] = 1
df_Producto.at[545, 'clae2'] = 1
df_Producto.at[546, 'clae2'] = 1
df_Producto.at[547, 'clae2'] = 1
df_Producto.at[548, 'clae2'] = 1
df_Producto.at[549, 'clae2'] = 1
df_Producto.at[550, 'clae2'] = 1
df_Producto.at[551, 'clae2'] = 21
df_Producto.at[552, 'clae2'] = 13
df_Producto.at[553, 'clae2'] = 1
df_Producto.at[554, 'clae2'] = 1
df_Producto.at[555, 'clae2'] = 1
df_Producto.at[556, 'clae2'] = 1
df_Producto.at[557, 'clae2'] = 10
df_Producto.at[558, 'clae2'] = 1
df_Producto.at[559, 'clae2'] = 10
df_Producto.at[560, 'clae2'] = 3
df_Producto.at[561, 'clae2'] = 3
df_Producto.at[562, 'clae2'] = 1
df_Producto.at[563, 'clae2'] = 1
df_Producto.at[564, 'clae2'] = 10
df_Producto.at[565, 'clae2'] = 10
df_Producto.at[566, 'clae2'] = 10
df_Producto.at[567, 'clae2'] = 10
df_Producto.at[568, 'clae2'] = 10
df_Producto.at[569, 'clae2'] = 1
df_Producto.at[570, 'clae2'] = 1
df_Producto.at[571, 'clae2'] = 1
df_Producto.at[572, 'clae2'] = 999
df_Producto.at[573, 'clae2'] = 1
df_Producto.at[574, 'clae2'] = 1
df_Producto.at[575, 'clae2'] = 1
df_Producto.at[576, 'clae2'] = 10
df_Producto.at[577, 'clae2'] = 11
df_Producto.at[578, 'clae2'] = 11
df_Producto.at[579, 'clae2'] = 11
df_Producto.at[580, 'clae2'] = 1
df_Producto.at[581, 'clae2'] = 10
df_Producto.at[582, 'clae2'] = 10
df_Producto.at[583, 'clae2'] = 10 
df_Producto.at[584, 'clae2'] = 10
df_Producto.at[585, 'clae2'] = 10
df_Producto.at[586, 'clae2'] = 10
df_Producto.at[587, 'clae2'] = 10
df_Producto.at[588, 'clae2'] = 10
df_Producto.at[589, 'clae2'] = 10
df_Producto.at[590, 'clae2'] = 10
df_Producto.at[591, 'clae2'] = 1
df_Producto.at[592, 'clae2'] = 1
df_Producto.at[593, 'clae2'] = 1
df_Producto.at[594, 'clae2'] = 1
df_Producto.at[595, 'clae2'] = 1
df_Producto.at[596, 'clae2'] = 1
df_Producto.at[597, 'clae2'] = 1
df_Producto.at[598, 'clae2'] = 1


# Relaciones entre entidades
# =============================================================================
# Agregamos id_departamento
agregar_id_departamento1 = """
                           SELECT DISTINCT oo.*, dep.id_departamento
                           FROM df_Operadores_organicos AS oo
                           LEFT OUTER JOIN localidades AS dep
                           ON oo.departamento = dep.departamento AND oo.id_provincia = dep.id_provincia
                           """

df_Operadores_organicos= sql^agregar_id_departamento1

is_null = """
          SELECT DISTINCT id, establecimiento, razón_social, departamento, id_provincia
          FROM df_Operadores_organicos
          WHERE id_departamento IS NULL
          """
Operadores_organicos_null = sql^is_null


cambiar_null = """
           SELECT DISTINCT oo.*, asen.id_departamento AS id_departamento
           FROM Operadores_organicos_null AS oo
           LEFT OUTER JOIN localidades AS asen
           ON oo.departamento = asen.asentamiento AND oo.id_provincia = asen.id_provincia
           """
Operadores_organicos_null = sql^cambiar_null

nulls_a_descartar = """
                        SELECT DISTINCT *
                        FROM Operadores_organicos_null
                        WHERE id_departamento IS NULL
                    """
Nulls_a_descartar = sql^nulls_a_descartar

is_not_null = """
              SELECT id, establecimiento, razón_social, departamento, id_provincia, id_departamento,
              FROM df_Operadores_organicos
              WHERE id_departamento IS NOT NULL
              """
Operadores_organicos_not_null = sql^is_not_null

remover_nulls = """
                SELECT * 
                FROM Operadores_organicos_null
                EXCEPT
                SELECT *
                FROM Nulls_a_descartar
                """
Operadores_organicos_null = sql^remover_nulls

union = """
        SELECT id, establecimiento, razón_social, id_provincia, id_departamento,
        FROM Operadores_organicos_not_null
        UNION
        SELECT id, establecimiento, razón_social, id_provincia, id_departamento,
        FROM Operadores_organicos_null
        ORDER BY id ASC
        """
df_Operadores_organicos = sql^union

# Relación entre producto y operadores orgánicos 
# =============================================================================
relacion_es_producido_por = """ 
                            SELECT id AS id_op_or, producto
                            FROM operadores_organicos
                           """

df_Relacion_Produce = sql^relacion_es_producido_por


# Exportamos las tablas limpias en formato .csv
# =============================================================================

df_CLAE.to_csv('./TablasLimpias/CLAE.csv')
df_Departamento.to_csv('./TablasLimpias/Departamento.csv')
df_Establecimiento_productivo.to_csv('./TablasLimpias/Establecimiento_productivo.csv')
df_Operadores_organicos.to_csv('./TablasLimpias/Operadores_organicos.csv')
df_Producto.to_csv('./TablasLimpias/Producto.csv')
df_Provincia.to_csv('./TablasLimpias/Provincia.csv')
df_Relacion_Produce.to_csv('./TablasLimpias/Relacion_Produce.csv')


# Ejercicio h)
# =============================================================================

# Consulta 1
# =============================================================================

consultah1_1 = """
                SELECT DISTINCT producto, id_provincia
                FROM df_Relacion_Produce
                INNER JOIN df_Operadores_organicos 
                ON id = id_op_or
                """
producto_id_provincia = sql^consultah1_1

consultah1_2 = """
                SELECT pip.producto, dp.provincia
                FROM producto_id_provincia AS pip
                INNER JOIN df_Provincia AS dp
                ON pip.id_provincia = dp.id
                """
producto_provincia = sql^consultah1_2       
        
consultah1_3 = """
                SELECT producto, count(producto) as cantidad
                FROM producto_provincia
                GROUP BY producto
                ORDER BY cantidad desc
               """
cantidad_productos = sql^consultah1_3

consultah1_4 = """
                SELECT pd.producto, pd.provincia 
                FROM producto_provincia AS pd
                INNER JOIN cantidad_productos AS cp
                ON pd.producto = cp.producto
                ORDER BY cp.cantidad DESC, pd.producto ASC
                """
producto_provincia_ordenado = sql^consultah1_4
print(producto_provincia_ordenado)
producto_provincia_ordenado.to_csv('./TablasEjercicios/H1_producto_provincia_ordenado.csv')
# Consulta 2
# =============================================================================

consultah2_1 =  """
                SELECT clae2, count(clae2) as cantidad
                FROM df_Establecimiento_productivo
                GROUP BY clae2
                """
clae2_cantidad = sql^consultah2_1

consultah2_2 = """
                SELECT dc.clae2, dc.clae2_desc
                FROM df_CLAE AS dc
                WHERE dc.clae2 = (
                    SELECT cd1.clae2
                    FROM clae2_cantidad AS cd1
                    WHERE cd1.cantidad = (
                        SELECT max(cd2.cantidad)
                        FROM clae2_cantidad AS cd2
                        )
                    )
                """
clae2_establecimiento_productivo = sql^consultah2_2
print(clae2_establecimiento_productivo)
clae2_establecimiento_productivo.to_csv('./TablasEjercicios/H2_clae2_establecimiento_productivo.csv')

# Consulta 3
# =============================================================================

consultah3_1 =  """
                SELECT producto, count(producto) as cantidad
                FROM df_Relacion_Produce
                GROUP BY producto
                """
producto_cantidad = sql^consultah3_1

# ¿Qué producto es el más producido?

consultah3_2 = """
                SELECT pc1.producto
                FROM producto_cantidad AS pc1
                WHERE pc1.cantidad = (
                    SELECT max(pc2.cantidad)
                    FROM producto_cantidad AS pc2
                    )
                """
producto_mas_producido = sql^consultah3_2
print(producto_mas_producido)
producto_mas_producido.to_csv('./TablasEjercicios/H3_1_producto_mas_producido.csv')
# ¿Qué Provincia-Departamento los producen?

consultah3_3 = """
                SELECT drp.id_op_or
                FROM df_Relacion_Produce AS drp
                WHERE drp.producto = (
                    SELECT pmp.producto
                    FROM producto_mas_producido AS pmp
                    )
                """
operador_organico_producto = sql^consultah3_3

consultah3_4 = """
                SELECT id_provincia, id_departamento
                FROM df_Operadores_organicos
                INNER JOIN operador_organico_producto
                ON id_op_or = id
                """
ids_provincia_departamento = sql^consultah3_4

consultah3_5 = """
                SELECT DISTINCT provincia, id_departamento
                FROM df_Provincia
                INNER JOIN ids_provincia_departamento
                ON id = id_provincia
                """
id_provincia_departamento = sql^consultah3_5

consultah3_6 = """
                SELECT provincia, departamento
                FROM id_provincia_departamento
                INNER JOIN df_Departamento
                ON id = id_departamento
                """
provincia_departamento_producto_mas_producido = sql^consultah3_6
print(provincia_departamento_producto_mas_producido)
provincia_departamento_producto_mas_producido.to_csv('./TablasEjercicios/H3_2_provincia_departamento_producto_mas_producido.csv')
# Consulta 4
# =============================================================================

consultah4_1 = """
                SELECT DISTINCT id
                FROM df_Departamento
            EXCEPT
                SELECT DISTINCT id_departamento AS id
                FROM df_Operadores_organicos
                """
id_departamentos_sin_op_or = sql^consultah4_1

# ¿Cuántos son? 
consultah4_2 = """
                SELECT count(id) AS deptos_sin_op_or
                FROM id_departamentos_sin_op_or
                """
cant_deptos_sin_op_or = sql^consultah4_2
print(cant_deptos_sin_op_or)
cant_deptos_sin_op_or.to_csv('./TablasEjercicios/H4_1_cant_deptos_sin_op_or.csv')
# ¿Cuales son?
consultah4_2 = """
                SELECT dd.departamento
                FROM id_departamentos_sin_op_or AS idsoo
                INNER JOIN df_Departamento AS dd
                ON idsoo.id = dd.id
                """
departamentos_sin_op_or = sql^consultah4_2

print(departamentos_sin_op_or)
departamentos_sin_op_or.to_csv('./TablasEjercicios/H4_2_departamentos_sin_op_or.csv')
# Consulta 5
# =============================================================================
consultah5_1 = """
                SELECT ep.id, ep.proporcion_mujeres, dd.id_provincia
                FROM df_Establecimiento_productivo AS ep
                INNER JOIN df_Departamento AS dd
                ON ep.id_departamento = dd.id
                """
proporcion_mujeres_departamento = sql^consultah5_1

consultah5_2 = """
                SELECT ep.id, ep.proporcion_mujeres, pp.provincia
                FROM proporcion_mujeres_departamento AS ep
                INNER JOIN df_Provincia AS pp
                ON ep.id_provincia = pp.id
                """
proporcion_mujeres_provincia = sql^consultah5_2

consultah5_3 = """
                SELECT provincia, AVG(proporcion_mujeres) AS promedio, STDDEV(proporcion_mujeres) AS desvio
                FROM proporcion_mujeres_provincia
                GROUP BY provincia
                """
promedio_desvio = sql^consultah5_3

consultah5_4 = """
                SELECT AVG(proporcion_mujeres) AS promedio_pais
                FROM proporcion_mujeres_provincia
                """
promedio_prop_mujeres_pais = sql^consultah5_4

promedioPropPais = float(promedio_prop_mujeres_pais['promedio_pais'])

consultah5_5 = """
                SELECT *, 
                    CASE
                        WHEN promedio > $promedioPropPais
                        THEN 'mayor'
                        ELSE 'menor'
                    END AS mayor_o_menor_promedio_pais
                FROM promedio_desvio
                """
tabla_prop_mujeres_prom_desvio_mayor_menor = sql^consultah5_5
print(tabla_prop_mujeres_prom_desvio_mayor_menor)
tabla_prop_mujeres_prom_desvio_mayor_menor.to_csv('./TablasEjercicios/H5_tabla_prop_mujeres_prom_desvio_mayor_menor.csv')
# Consulta 6
# =============================================================================
consultah6_1 = """
                SELECT id_departamento, count(id) AS cant_establecimientos_prod
                FROM df_Establecimiento_productivo
                GROUP BY id_departamento
                ORDER BY cant_establecimientos_prod DESC
                """
cant_establecimientos_productivos_depto = sql^consultah6_1

consultah6_2 = """
                SELECT id_departamento, count(id) AS cant_operadores_org
                FROM df_Operadores_organicos
                GROUP BY id_departamento
                ORDER BY cant_operadores_org DESC
                """
cant_operadores_organicos_depto = sql^consultah6_2

consultah6_3 = """
                SELECT depto.id, depto.departamento, depto.id_provincia, 
                    cep.cant_establecimientos_prod, coo.cant_operadores_org
                FROM df_Departamento AS depto
                LEFT OUTER JOIN cant_establecimientos_productivos_depto AS cep
                ON cep.id_departamento = depto.id
                
                LEFT OUTER JOIN cant_operadores_organicos_depto AS coo
                ON coo.id_departamento = depto.id"""

cantidades_depto = sql^consultah6_3

consultah6_4 = """
                SELECT cd.departamento, prov.provincia, 
                    CASE WHEN cant_establecimientos_prod IS NULL THEN 0
                        ELSE cant_establecimientos_prod
                    END AS cant_establecimientos_prod,
                    CASE WHEN cant_operadores_org IS NULL THEN 0
                        ELSE cant_operadores_org
                    END AS cant_operadores_org
                FROM cantidades_depto AS cd
                INNER JOIN df_Provincia AS prov
                ON cd.id_provincia = prov.id
                """
cantidades_depto_prov = sql^consultah6_4
print(cantidades_depto_prov)
cantidades_depto_prov.to_csv('./TablasEjercicios/H6_cantidades_depto_prov.csv')

# Ejercicio I) - Visualización
# =============================================================================
# Esta consulta la usaremos en la mayoria de las visualizaciones
ConsultaDepto_Prov = """ 
               SELECT dep.id AS id_departamento, dep.departamento, 
                   prov.id AS id_provincia, prov.provincia
               FROM df_Departamento AS dep
               INNER JOIN df_Provincia AS prov
               ON dep.id_provincia = prov.id
               """
Departamento_Provincia = sql^ConsultaDepto_Prov

# Gráfico 1
# =============================================================================
Consultai1_1 = """
               SELECT ep.id, dp.provincia
               FROM df_Establecimiento_productivo AS ep
               INNER JOIN Departamento_Provincia AS dp
               ON ep.id_departamento = dp.id_departamento
               """
est_prod_provincia = sql^Consultai1_1

est_prod_provincia['provincia'].value_counts().plot.bar().set(title='Establecimientos productivos por provincia', xlabel='Provincias', ylabel='Cantidad de establecimientos productivos')
plt.show()
plt.close()

# Gráfico 2
# =============================================================================
Consultai2_1 = """
               SELECT rp.producto, rp.id_op_or, op.id_provincia
               FROM df_Relacion_Produce AS rp
               INNER JOIN df_Operadores_organicos AS op
               ON op.id = rp.id_op_or
               """
producto_idop_idporv= sql^Consultai2_1

Consultai2_2 = """
               SELECT ii.id_op_or, pp.provincia, count(ii.producto) AS productos_por_operador
               FROM producto_idop_idporv AS ii
               INNER JOIN df_Provincia AS pp
               ON ii.id_provincia = pp.id
               GROUP BY ii.id_op_or, pp.provincia
               """
cant_prod_por_prov = sql^Consultai2_2

sns.boxplot(data = cant_prod_por_prov, x = 'provincia' , y = 'productos_por_operador').set(title= 'Cantidad de productos que produce un operador por provincia', xlabel = 'Provincias' , ylabel='Cantidad de productos producidos \n por un operador')
plt.xticks(rotation = 90)
plt.show()
plt.close()

# Como hay datos operadores organicos que producen muchos mas productos del 
# promedio, la visualizacion anterios mustra los datos de manera "desproporcionada".
# Para una visualizacion mas clara usar la variable "cant_prod_por_prov_hasta_10"
# en vez de "cant_prod_por_prov"

Consultai2_3 = """
               SELECT *
               FROM cant_prod_por_prov
               WHERE productos_por_operador <= 10
               """
cant_prod_por_prov_hasta_10 = sql^Consultai2_3

sns.boxplot(data = cant_prod_por_prov_hasta_10, x = 'provincia' , y = 'productos_por_operador').set(title= 'Cantidad de productos que produce un operador por provincia', xlabel = 'Provincias' , ylabel='Cantidad de productos producidos \n por un operador')
plt.xticks(rotation = 90)
plt.show()
plt.close()


# Gráfico 3
# =============================================================================
# Los establecimientos productivos que tienen clae 2 e {1,2,3,10,20,21} ya los 
# tenemos filtrados, son los del df_Establecimiento_productivo

# Cantidad de establecimientos productivos por provincia
Consultai3_1 = """
               SELECT dp.provincia, count(dp.provincia) AS cantidad
               FROM df_Operadores_organicos AS oo
               INNER JOIN Departamento_Provincia AS dp
               ON oo.id_departamento = dp.id_departamento
               GROUP BY provincia
               """
cantidad_op_or_por_provincia = sql^Consultai3_1

# Nos quedamos con los datos de establecimientos productivos que estan en departamentos con operadores organicos 
Consultai3_2 = """
                SELECT *
                FROM df_Establecimiento_productivo
                EXCEPT
                SELECT ep.*
                FROM df_Establecimiento_productivo as ep
                INNER JOIN id_departamentos_sin_op_or as i
                ON ep.id_departamento = i.id
              """
establecimientos_productivos_organicos = sql^Consultai3_2

# Promedio de proporcion de mujeres por provincia
Consultai3_3 = """
               SELECT AVG(ep.proporcion_mujeres) AS proporcion_mujeres, dp.provincia
               FROM establecimientos_productivos_organicos AS ep
               INNER JOIN Departamento_Provincia AS dp
               ON ep.id_departamento = dp.id_departamento
               GROUP BY dp.provincia
               """
proporcion_mujeres_por_provincia = sql^Consultai3_3

Consultai3_4 = """
               SELECT p.proporcion_mujeres, c.cantidad, c.provincia
               FROM cantidad_op_or_por_provincia AS c
               INNER JOIN proporcion_mujeres_por_provincia AS p
               ON c.provincia = p.provincia
               """
proporcion_cantidad_provincia = sql^Consultai3_4

sns.scatterplot(data=proporcion_cantidad_provincia, x="proporcion_mujeres", y="cantidad", hue="provincia").set(title='Relación entre la cantidad de operadores orgánicos \n y la proporción de mujeres empleadas por estableciomientos productivos \n en cada provincia', xlabel = 'Porcion de mujeres empleadas por estableciomientos productivos \n en promedio por provincia' , ylabel='Cantidad de operadores organicos por provincia')
x_coord = 1.2  # Coordenada X
y_coord = 0.5  # Coordenada Y
plt.legend(loc='center left', bbox_to_anchor=(x_coord, y_coord))
plt.xlim(0, 1)
plt.show()

# Gráfico 4
# =============================================================================
Consultai4_1 = """
               SELECT ep.proporcion_mujeres, dp.provincia
               FROM df_Establecimiento_productivo AS ep
               INNER JOIN Departamento_Provincia AS dp
               ON ep.id_departamento = dp.id_departamento
               """
proporcion_mujeres_provincia = sql^Consultai4_1

sns.violinplot(data = proporcion_mujeres_provincia, x = 'provincia' , y = 'proporcion_mujeres').set(title='Distribución de la proporción de mujeres empleadas \n en establecimientos productivos por provincia', xlabel='Provincias', ylabel='Proporción de mujeres empleadas \n en establecimientos productivos')
plt.xticks(rotation = 90)
plt.show()
plt.close()


