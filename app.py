from typing import List
import numpy as np
import pandas as pd
from datetime import date
import streamlit as st
import streamlit.components.v1 as components
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from tensorflow.keras.preprocessing import sequence
from tensorflow.keras.models import load_model as load_keras_model

CLASS = {0:'정상', 1:'경증', 2:'치매'}


def make_input_data(df: pd.DataFrame, email: str) -> np.ndarray:
    to_pad = 93
    sequences = []

    for one_seq in [np.array(df[df.EMAIL == email].drop(['EMAIL','요약 날짜'],axis=1))]:
        n = to_pad - len(sequences)
        to_concat = np.repeat(one_seq[-1], n).reshape(51, n).transpose()
        new_one_seq = np.concatenate([one_seq, to_concat])
        sequences.append(new_one_seq)
    final_seq = np.stack(sequences)

    seq_len = 72
    final_seq = sequence.pad_sequences(final_seq, maxlen=seq_len, padding='post', dtype='float', truncating='post')
    return final_seq


def main():

    model = load_keras_model('best_model.h5')
    st.set_page_config(layout="wide")

    ##############################################################
    ########################### Header ###########################
    ##############################################################

    icon, upload = st.columns([1,3])
    with icon:
        st.image('https://www.freeiconspng.com/thumbs/human-icon-png/person-outline-icon-png-person-outline-icon-png-person-17.png', width=200)
    with upload:
        file = st.file_uploader('upload csv', type=['csv','xlsx'], accept_multiple_files=False, key='file')
        if file:
            df = pd.read_csv(file)

    icon, email, sdate, pred = st.columns([1,1,1,1])
    with email:
        if file:
            email = st.selectbox('이메일 주소', df.EMAIL.drop_duplicates().tolist(), key='email')
            select_df = df[df['EMAIL'] == email].copy()
        else:
            st.write('이메일 주소')
    with sdate:
        date_list = ['전체']+df['요약 날짜'].tolist() if file else [date.today().strftime('%Y-%m-%d')]
        sdate = st.selectbox('일자', date_list, key='sdate')
    with pred:
        if file:
            input_data = make_input_data(df, email)
            pred = model.predict(input_data)
            output = (CLASS[np.argmax(pred)], np.round(np.max(pred[0])*100,2))
            st.write(f'분석결과 {output[1]}% 확률로 {output[0]} 입니다.')
        else:
            st.write('파일을 업로드 해주세요.')

    ##############################################################
    ########################### Result ###########################
    ##############################################################

    if file:
        st.markdown('---')
        if sdate != '전체':
            select_df = df[(df['EMAIL'] == email) & (df['요약 날짜'] == sdate)]
        else:
            select_df = df[(df['EMAIL'] == email)]

        ##############################################################
        ######################## Graph Chart #########################
        ##############################################################

        left, center, right = st.columns([1,1,1])
        with left:
            labels = ['깊은 수면 시간','램수면 시간','잠 시간']
            values = [select_df[label].mean().round(2) for label in labels]
            values[2] = values[2] - values[0] - values[1]
            sleep_time_chart = go.Figure(go.Pie(labels=labels,values=values))
            st.plotly_chart(sleep_time_chart,use_container_width=True)
        with center:
            labels = ['매일 움직인 거리', '매일 걸음 수']
            values = [select_df[label].mean().round(2) for label in labels]
            dist_step_chart = go.Figure(go.Bar(x=values,y=labels,orientation='h'))
            st.plotly_chart(dist_step_chart,use_container_width=True)
        with right:
            labels = ['고강도 활동 시간', '중강도 활동 시간', '저강도 활동 시간']
            values = [select_df[label].mean().round(2) for label in labels]
            act_time_chart = go.Figure(go.Bar(x=values,y=labels,orientation='h'))
            st.plotly_chart(act_time_chart,use_container_width=True)


        ##############################################################
        ######################## Polar Chart #########################
        ##############################################################

        st.markdown('---')
        radar_left, radar_right = st.columns([1,1])
        with radar_left:
            labels = ['활동 점수', '활동 목표달성 점수', '활동 유지 점수', '운동 빈도 점수', '운동 볼륨 점수']
            values = [select_df[label].mean().round(2) for label in labels]
            active_df = pd.DataFrame(dict(theta=labels,r=values))
            active_score_chart = px.line_polar(active_df, r='r', theta='theta', line_close=True, range_r=[0,100])
            st.write(active_score_chart)
        with radar_right:
            labels = ['램수면 점수', '깊은 수면 점수', '수면 시기 점수', '수면 방해 점수', '수면 효율 점수', '수면 잠복 점수'   ]
            values = [select_df[label].mean().round(2) for label in labels]
            sleep_df = pd.DataFrame(dict(theta=labels,r=values))
            sleep_score_chart = px.line_polar(sleep_df, r='r', theta='theta', line_close=True, range_r=[0,100])
            st.write(sleep_score_chart)

        st.markdown('---')
        st.dataframe(select_df)
    else:
        pass


if __name__ == '__main__':
    main()
