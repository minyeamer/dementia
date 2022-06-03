import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.figure_factory as ff
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, date


def main():

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
        else:
            st.write('이메일 주소')
    with sdate:
        if file:
            sdate = st.selectbox('일자', ['전체']+df['요약 날짜'].tolist(), key='sdate')
        else:
            st.write('일자')
        # st.write(date.today().strftime('%Y-%m-%d'))
    with pred:
        if file:
            st.write('분석결과 치매일 확률은 23.54% 입니다.')
        else:
            st.write('파일을 업로드 해주세요.')


    ##############################################################
    ########################### Result ###########################
    ##############################################################

    if file:
        st.markdown('---')
        if sdate != '전체':
            df = df[(df['EMAIL'] == email) & (df['요약 날짜'] == sdate)]
        else:
            df = df[(df['EMAIL'] == email)]
        st.dataframe(df)
        st.markdown('---')

        ##############################################################
        ######################## Graph Chart #########################
        ##############################################################

        left, center, right = st.columns([1,1,1])
        with left:
            labels = ['깊은 수면 시간','램수면 시간','잠 시간']
            values = [df[label].mean().round(2) for label in labels]
            values[2] = values[2] - values[0] - values[1]
            sleep_time_chart = go.Figure(go.Pie(labels=labels,values=values))
            st.plotly_chart(sleep_time_chart,use_container_width=True)
        with center:
            labels = ['매일 움직인 거리', '매일 걸음 수']
            values = [df[label].mean().round(2) for label in labels]
            dist_step_chart = go.Figure(go.Bar(x=values,y=labels,orientation='h'))
            st.plotly_chart(dist_step_chart,use_container_width=True)
        with right:
            labels = ['고강도 활동 시간', '중강도 활동 시간', '저강도 활동 시간']
            values = [df[label].mean().round(2) for label in labels]
            act_time_chart = go.Figure(go.Bar(x=values,y=labels,orientation='h'))
            st.plotly_chart(act_time_chart,use_container_width=True)


        ##############################################################
        ######################## Polar Chart #########################
        ##############################################################

        st.markdown('---')
        radar_left, radar_right = st.columns([1,1])
        with radar_left:
            labels = ['활동 점수', '활동 목표달성 점수', '활동 유지 점수', '운동 빈도 점수', '운동 볼륨 점수']
            values = [df[label].mean().round(2) for label in labels]
            active_df = pd.DataFrame(dict(theta=labels,r=values))
            active_score_chart = px.line_polar(active_df, r='r', theta='theta', line_close=True, range_r=[0,100])
            st.write(active_score_chart)
        with radar_right:
            labels = ['램수면 점수', '깊은 수면 점수', '수면 시기 점수', '수면 방해 점수', '수면 효율 점수', '수면 잠복 점수'   ]
            values = [df[label].mean().round(2) for label in labels]
            sleep_df = pd.DataFrame(dict(theta=labels,r=values))
            sleep_score_chart = px.line_polar(sleep_df, r='r', theta='theta', line_close=True, range_r=[0,100])
            st.write(sleep_score_chart)
    else:
        pass


if __name__ == '__main__':
    main()
