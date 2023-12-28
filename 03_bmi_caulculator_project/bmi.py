# import the streamlit library
import streamlit as st

# Give a title to out app
st.title('Welcome to BMI Calculator')

# Take a weight input as kgs
weight = st.number_input('Enter your weight in kgs')

# Take height input
# radio button to choose height format
status = st.radio("Select your height format: ", ('cms', 'meters', 'feet'))

# compare status value
if (status == 'cms'):
    # now take the height in centimeters
    height = st.number_input('Centimeters')

    try:
        bmi = weight / ((height/100)**2)
    except:
        st.text("Enter some value of height")
elif(status == "meters"):
    # now take the height in meters
    height = st.number_input('Meters')

    try:
        bmi = weight / (height**2)
    except:
        st.text("Enter some value of height")
else:
    # now take the height in feet
    height = st.number_input('Feet')
    # 1 meter = 3.28084 feet
    try:
        bmi = weight / ((height/3.28084)**2)
    except:
        st.text("Enter some value of height")

# check if the button is pressed or not
if st.button('Calculate BMI'):
    st.success('Your BMI is {}'.format(bmi))

    # give the interpretation of BMI index
    if (bmi < 16):
        st.error("You are Extremely Underweight")
    elif (bmi >= 16 and bmi < 18.5):
        st.warning("You are Underweight")
    elif (bmi >= 18.5 and bmi < 25):
        st.success("You are Healthy")
    elif (bmi >= 25 and bmi < 30):
        st.warning("You are Overweight")
    elif (bmi >= 30):
        st.error("You are Extremely Overweight")
        