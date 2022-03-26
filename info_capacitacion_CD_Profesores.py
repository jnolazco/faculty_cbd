import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go 
from plotly.subplots import make_subplots
import plotly.graph_objects as go
from wordcloud import WordCloud, STOPWORDS
import matplotlib.pyplot as plt

import firebase_admin
from firebase_admin import credentials, firestore

#pathKeys = "/content/drive/My Drive/Computadora_Virtual/Hub/Oportunidades/Capacitación Profesores/Información Capacitación 2/Keys/" # download kes; each project has different keys.
#pathKeys = "./"

if not firebase_admin._apps:
    cred = credentials.Certificate(pathKeys +"capacitacionprofesorestec-firebase-adminsdk-zqbzr-c79859d941.json") #
    firebase_admin.initialize_app(cred)

db = firestore.client()

@st.cache(persist=True)
def load_cp_data_firebase():
    posts_ref = list(db.collection(u'facultyCapacityDevelopment').stream())
    users_dict = list(map(lambda x: x.to_dict(), posts_ref))
    cp_data = pd.DataFrame(users_dict)

    return cp_data

cp_data = load_cp_data_firebase()

###############################################################################################
########################################    PREPROCESSING ########################################
####  1. In the original file, a number of columns has the same name and the information is on theses
####     columns, but in different rows, therefere the first step is to collapse all these columns
####     with the same name in one columns keeping the same name.
####  2. Original file has very large names, therefore to make the rest of the code more legible,
####     the column names are re-named.
###############################################################################################

###  1.a. Colapsing Campis in a column  ###
cp_data = cp_data.fillna('')
cp_data['CampusT'] = cp_data[['Campus:','Campus:.1', 'Campus:.2', 'Campus:.3']].apply(lambda x: ''.join(x), axis=1)
cp_data.drop(['Campus:','Campus:.1', 'Campus:.2', 'Campus:.3'], axis=1, inplace=True)

###  1.a. Colapsing Schools's columns' in a column  ###
cp_data['EscuelaT'] = cp_data[['¿A qué escuela perteneces?','¿A qué escuela perteneces?.1', '¿A qué escuela perteneces?.2','¿A qué escuela perteneces?.3']].apply(lambda x: ''.join(x), axis=1)
cp_data.drop(['¿A qué escuela perteneces?','¿A qué escuela perteneces?.1', '¿A qué escuela perteneces?.2','¿A qué escuela perteneces?.3'], axis=1, inplace=True)

### 2. renaming  ###
cp_data=cp_data.rename({'Seleccione los cursos de Certificación  "Microsoft Azure"  que va a tomar como capacitación: ':'Azure Microsoft', #c1
                'Seleccione los cursos de Certificación  "AWS Machine Learning"  que va a tomar como capacitación:':'AWS ML',
                'Seleccione los cursos de la especialidad "Python for Everybody" (University of Michigan) que va a tomar como capacitación:':'Python (U. Michigan)', #c3
                'Seleccione los cursos de la especialidad "Big Data – Introducción al uso práctico de datos masivos" (Universidad Autónoma de Barcelona) que va a tomar como capacitación:':'BigData (U.A.Barcelona)',
                'Seleccione el curso "Manipulación de Datos y Big Data" que va a tomar como capacitación:':'BigData', #c5
                'Seleccione los cursos de la especialidad "Diseño e investigación de experiencia de usuario" (University of Michigan) que va a tomar como capacitación:':'UX/UI (U.Michigan)', #c6
                'Seleccione los cursos de la especialidad "Diseño de interfaz de usuario" (University of Minnesota) que va a tomar como capacitación:':'UX/UI (U.Minnessota)', #c7
                'Seleccione los cursos de la especialidad "Statisctics with Python" (University of Michigan) que va a tomar como capacitación:':'Statistics with Pyton (U.Michigan)', #c8
                'Seleccione los cursos "Visualización y Estadística" que va a tomar como capacitación:':'Visualiation/Statistics', #c9
                'Seleccione los cursos de la especialidad "Ciencias de los Datos Aplicada con Python" (University of Michigan) que va a tomar como capacitación:':'Data Science (U.Michigan)', #c10
                'Seleccione el curso de la especialidad "AWS" (Amazon) que va a tomar como capacitación: *No es de COURSERA, nosotros los inscribimos directamente.':'AWS Services', #c11
                'Seleccione los cursos de la especialidad "Requirements Engineering: Secure Software Specifications" (University of Colorado) que va a tomar como capacitación:':''}, axis='columns')
########################################  END: PREPROCESSING ########################################


######################################## Lists definitions ######################################## 
cursos_Microsoft_Azu=['Fundamentos de AZURE AZ','Inteligencia Artiificial IA','Azure Data DP', 'Power Platform PL']
cursos_AWS_ML = ['AWS Academy Machine Learning Foundations (20 horas)','AWS Academy Data Analytis (7.5 horas)']
cursos_Py_UMich = ['Programming for Everybody (Getting Started with Python) - 19 horas', 'Python Data Structures - 19 horas','Using Python to Access Web Data','Using Databases with Python - 15 horas','Using Databases with Python - 15 horas', 'Capstone: Retrieving, Processing, and Visualizing Data with Python - 9 horas']
cursos_BigData_UABar = ['Big Data: el impacto de los datos masivos en la sociedad actual - 7 horas', 'Big Data: adquisición y almacenamiento de datos - 11 horas','Big Data: procesamiento y análisis - 13 horas','Big Data: visualización de datos - 9 horas', 'Capstone: Retrieving, Processing, and Visualizing Data with Python - 9 horas','Big Data: capstone project - 13 horas','Big Data Analysis with Scala and Spark (Ecole Polytechnique Federal de Lousanne) - 28 horas']
curso_BigData = ['Big Data Analysis with Scala and Spark (Ecole Polytechnique Federal de Lousanne) - 28 horas']
cursos_UXUI_UMich = ['Introduction to User Experience Principles and Processes - 11 horas', 'Understanding User Needs - 10 horas','Evaluating Designs with Users - 8 horas','UX Design: From Concept to Prototype - 14 horas']
cursos_UXUI_UMin = ['Introduction to UI Design - 14 horas','User Research and Design - 8 horas','Prototyping and Design - 11 horas','Evaluating User Interfaces - 12 horas','UI Design Capstone - 17 horas']
cursos_StatPy_UMich = ['Understanding and Visualizing Data with Python - 20 horas','Inferential Statistical Analysis with Python - 18 horas','Fitting Statistical Models to Data with Python - 15 horas']
cursos_VisStat = ['Understanding and Visualizing Data with Python - 20 horas', 'Inferential Statistical Analysis with Python - 18 horas','Fitting Statistical Models to Data with Python - 15 horas','Visual Elements of User Interface Design (California Institute of Arts) - 16 horas','Applied Plotting, Charting & Data Representation in Python (University of Michigan) - 20 horas']
cursos_DS_UMich = ['Introduction to Data Science in Python - 31 horas', 'Applied Plotting, Charting & Data Representation in Python - 20 horas','Applied Machine Learning in Python - 34 horas','Applied Text Mining in Python - 29 horas','Applied Social Network Analysis in Python - 29 horas','Fundamentals of Reinforcement Learning - 15 horas','Sample-based Learning Methods - 22 horas','Prediction and Control with Function Approximation - 22 horas','A Complete Reinforcement Learning System (Capstone) - 23 horas']

especialidades = ['Azure Microsoft', 'AWS ML', 'Python (U. Michigan)', 'BigData (U.A.Barcelona)','BigData (BigData)','UX/UI (U.Michigan)','UX/UI (U.Minnessota)','Statistics with Pyton (U.Michigan)']

#################### END: Lists definitions ######################################## 


def curse_given_speciality(select_Especialidad, keynumber):
    if   (select_Especialidad=='Azure Microsoft'): # Azure
         select_column='Azure Microsoft'
         select_curso = st.sidebar.selectbox('Cursos',cursos_Microsoft_Azu, key=keynumber) # Read the bottom
    elif (select_Especialidad=='AWS ML'): 
         select_column='AWS ML'
         select_curso = st.sidebar.selectbox('Cursos', cursos_AWS_ML,       key=keynumber) # Read the bottom
    elif (select_Especialidad=='Python (U. Michigan)'): 
         select_column='Python (U. Michigan)'
         select_curso = st.sidebar.selectbox('Cursos', cursos_Py_UMich,     key=keynumber) # Read the bottom
    elif (select_Especialidad=='BigData (U.A.Barcelona)'): 
         select_column='BigData (U.A.Barcelona)'
         select_curso = st.sidebar.selectbox('Cursos', cursos_BigData_UABar,key=keynumber) # Read the bottom
    elif (select_Especialidad=='BigData'): 
         select_column='BigData (BigData)'
         select_curso = st.sidebar.selectbox('Cursos', curso_BigData,       key=keynumber) # Read the bottom
    elif (select_Especialidad=='UX/UI (U.Michigan)'): 
         select_column='UX/UI (U.Michigan)'
         select_curso = st.sidebar.selectbox('Cursos', cursos_UXUI_UMich,   key=keynumber) # Read the bottom
    elif (select_Especialidad=='UX/UI (U.Minnessota)'): 
         select_column='UX/UI (U.Minnessota)'
         select_curso = st.sidebar.selectbox('Cursos', cursos_UXUI_UMin,    key=keynumber) # Read the bottom
    elif (select_Especialidad=='Statistics with Pyton (U.Michigan)'): 
         select_column='Statistics with Pyton (U.Michigan)'
         select_curso = st.sidebar.selectbox('Cursos', cursos_StatPy_UMich, key=keynumber) # Read the bottom
    elif (select_Especialidad=='Visualiation/Statistics'): 
         select_column='Visualiation/Statistics'
         select_curso = st.sidebar.selectbox('Cursos', cursos_VisStat,      key=keynumber) # Read the bottom
    elif (select_Especialidad=='Data Science (U.Michigan)'): 
         select_column='Data Science (U.Michigan)'
         select_curso = st.sidebar.selectbox('Cursos', cursos_DS_UMich,     key=keynumber)     # Read the bottom
    return (select_column, select_curso)

st.title("Capacity Building in Data Science (Decembre, 2020)")
st.sidebar.title("Capacity Building in Data Science")
st.markdown("This application is a dashboard used "
            "to know the Capacity Building in Data Science generated on Decembre, 2020")
st.sidebar.markdown("This application is a dashboard used "
            "to know the Capacity Building in Data Science generated on Decembre, 2020")


#####  selectbox definition ######
st.sidebar.markdown("### Number of faculty members per Region")
select = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='1') # Read the bottom

##select_Area = st.sidebar.selectbox('Visualization type', ['Ciencia de Datos', 'Ingeniería de Datos'], key='2') # Read the bottom
select_Especialidad = st.sidebar.selectbox('Especialidad', especialidades, key='2') # Read the bottom

##if (select_Area=='Cienia de Datos'):
select_column, select_curso = curse_given_speciality(select_Especialidad,'3')

cp_data_x = cp_data[cp_data[select_Especialidad].str.contains(select_curso[0:10],na=False)]

region_count = cp_data_x['Región:'].value_counts()

region_count = pd.DataFrame({'Region':region_count.index, 'Faculty members':region_count.values})

if not st.sidebar.checkbox("Hide", True, key=1):
    st.markdown("### Number of Faculty per Region")
    if select == 'Bar plot':
        fig = px.bar(region_count, x='Region', y='Faculty members', color='Faculty members', height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(region_count, values='Faculty members', names='Region')
        st.plotly_chart(fig)

##################################################################################
#############################  multiselect definition    ########################
##################################################################################
st.sidebar.markdown("### Number of faculty members per Region")
select = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='4') # Read the bottom

select_Especialidad = st.sidebar.selectbox('Especialidad', especialidades, key='5') # Read the bottom

select_column, select_curso = curse_given_speciality(select_Especialidad,'6')

e1=['Azure Microsoft','AWS ML']
c1=['Inteligencia Arti','AWS Academy Data']

cp_data_x = cp_data[cp_data[e1[0]].str.contains(select_curso[0:10],na=False)]
region_count1 = cp_data_x['Región:'].value_counts()
region_count1 = pd.DataFrame({'Region':region_count1.index, 'Microsoft Azure':region_count1.values})

cp_data_x2 = cp_data[cp_data[e1[1]].str.contains('AWS Academy Data', na=False)]
region_count2 = cp_data_x2['Región:'].value_counts()
region_count2 = pd.DataFrame({'Region':region_count2.index, 'AWS ML':region_count2.values})

if not st.sidebar.checkbox("Hide", True, key=4):
    st.markdown("### Number of Faculty per Region")
    if select == 'Bar plot':
        fm_Mcsft_Az = go.Bar(name=region_count1.columns[1], x=region_count1['Region'], y=region_count1['Microsoft Azure'])
        fm_AWS_ML   = go.Bar(name=region_count2.columns[1], x=region_count2['Region'],  y=region_count2['AWS ML'])
        plot = go.Figure(data=[fm_Mcsft_Az, fm_AWS_ML])
        st.plotly_chart(plot)
    else: # falta actualizar este "else"
        fig = px.pie(region_count, values='Faculty members', names='Region')
        st.plotly_chart(fig)
##################################################################################


#####  selectbox definition ######

st.sidebar.subheader("### Number of faculty members per Campus")

## select_curso = st.sidebar.multiselect('Cursos:',cursos_Microsoft_Azure, key='3') # Read the bottom

select_campus = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='2')
campus_count = cp_data['CampusT'].value_counts()
campus_count = pd.DataFrame({'Campus':campus_count.index, 'Faculty members':campus_count.values})
if not st.sidebar.checkbox("Hide", True, key=2):
    st.markdown("### Number of Faculty per Campus")
    if select_campus == 'Bar plot':
        fig = px.bar(campus_count, x='Campus', y='Faculty members', color='Faculty members', height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(campus_count, values='Faculty members', names='Campus')
        st.plotly_chart(fig)



st.sidebar.subheader("### Number of faculty members per Academic Departament")

select_dpto = st.sidebar.selectbox('Visualization type', ['Bar plot', 'Pie chart'], key='3')
dpto_count = cp_data['Departamento al que perteneces:'].value_counts()
dpto_count = pd.DataFrame({'Departamento':dpto_count.index, 'Faculty members':dpto_count.values})
if not st.sidebar.checkbox("Hide", True, key=3):
    st.markdown("### Number of Faculty per Campus")
    if select_dpto == 'Bar plot':
        fig = px.bar(dpto_count, x='Departamento', y='Faculty members', color='Faculty members', height=500)
        st.plotly_chart(fig)
    else:
        fig = px.pie(dpto_count, values='Faculty members', names='Departamento')
        st.plotly_chart(fig)

st.sidebar.header("Word Cloud")
word_region = st.sidebar.radio('Display word cloud for what sentiment?', ('Región Monterrey', 'Región Centro/Sur', 'Región Ciudad de México', 'Región Occidente'))
if not st.sidebar.checkbox("Close", True, key='4'):
    st.subheader('Word cloud for %s region' % (word_region))
    df = cp_data[cp_data['Región:']==word_region]
    words = ' '.join(df['Comentarios'])
    processed_words = ' '.join([word for word in words.split() if 'http' not in word and not word.startswith('@') and word != 'RT'])
    wordcloud = WordCloud(stopwords=STOPWORDS, background_color='white', width=800, height=640).generate(processed_words)
    plt.imshow(wordcloud)
    plt.xticks([])
    plt.yticks([])
    st.pyplot()
    
