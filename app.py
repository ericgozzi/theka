import streamlit as st



from theka import ask_theka





st.title("Play Among Books")


topic = st.text_input("Topic:")
question = st.text_input('Question:')


if topic and question:
    question = question.lower().split()
    answers = ask_theka(topic, question)
    for a in answers:
        st.markdown(a)






