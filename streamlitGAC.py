import os
import streamlit as st
import requests
import pandas as pd
import json
import openai

openai.api_key = os.environ["OPENAI_API_KEY"]
client = openai.OpenAI()
#list = pd.DataFrame(client.models.list())

#Configure the page title, favicon, layout, etc
st.set_page_config(page_title="GAC UN Sustainable Development", layout="wide")

def getData():
    df = pd.read_csv(r"projects.csv", index_col=False)
    return df[["Title"," Description","Country","Executing Agency Partner","DAC Sector","Expected Results","Progress and Results Achieved"]]

def getUNSDG(data):
    response = client.chat.completions.create(
        temperature=0,
        seed=1234,
        #model="gpt-4",
        #model="gpt-3.5-turbo",
        model='gpt-4-1106-preview',

    messages=[
    {"role": "system", "content": """
    You are a sustainable development expert with the United Nations.
    You work with government officials to help them translate sustainable development goals into national policies.
    You will be provided with information about government projects and you will explain which of the UN Sustainable Development goals are related to the project.
    Your response should be formatted as a bulleted list using markdown.
    The goals should be listed in order of their relatedness with the project. 
    Each bullet should start with the SDG Goal number and name.
    The SDG goal number and name should be typed in bold font, followed by an explanation of why you think the project is aligned to this goal. Reference the sub goals in cases where there is a clear connection with the subgoal and the project. Also note 
    
    """},
    {"role": "user", "content": str(data)}
    ]
    )
    return response.choices[0].message.content


def getUNSDG2(prompt):
    data = pd.DataFrame({"promptText": [prompt]})
    API_URL = 'https://cfds-ccm-prod.orm.datarobot.com/predApi/v1.0/deployments/{deployment_id}/predictions'
    API_KEY = os.environ["DATAROBOT_API_TOKEN"]
    DATAROBOT_KEY = os.environ["DATAROBOT_KEY"]
    deployment_id = '659c47ddae0a988d8d01d16f'
    headers = {
        'Content-Type': 'application/json; charset=UTF-8',
        'Authorization': 'Bearer {}'.format(API_KEY),
        'DataRobot-Key': DATAROBOT_KEY,
    }
    url = API_URL.format(deployment_id=deployment_id)
    predictions_response = requests.post(
        url,
        data=data.to_json(orient='records'),
        headers=headers
    )

    return predictions_response.json()["data"][0]["prediction"]


def mainPage():
    with st.sidebar:
        data = getData()
        selected_project = st.selectbox(label="Choose a Project", options=data["Title"].unique())

    st.image("headImage.png")
    st.header("Project Details")
    project = data.loc[data["Title"]==selected_project].set_index("Title").iloc[0]
    st.table(project)
    with st.spinner("processing..."):
        response = getUNSDG2(project)
    st.subheader("Alignment to UN Sustainable Development Goals")
    st.write(response)



#Main app
def _main():
    hide_streamlit_style = """
    <style>
    # MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
    st.markdown(hide_streamlit_style, unsafe_allow_html=True) # This let's you hide the Streamlit branding
    mainPage()

if __name__ == "__main__":
    _main()
