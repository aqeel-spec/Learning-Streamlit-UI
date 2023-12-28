from PIL import Image
# import module
import streamlit as st
 
# Title
st.title("Hello GeeksForGeeks !!!")
st.subheader("Welcome to Streamlit")
st.write("Hello World")

st.text("This is a text")


# success
st.success("Success")
 
# success
st.info("Information")
 
# success
st.warning("Warning")
 
# success
st.error("Error")
 
# Exception - This has been added later
exp = ZeroDivisionError("Trying to divide by Zero")
st.exception(exp)


# Write text
st.write("Text with write")
 
# Writing python inbuilt function range()
st.write(range(10))


# Display Images
 
# import Image from pillow to open images
img = Image.open("career_2.jpg")
 
# display image using streamlit
# width is used to set the width of an image
st.image(img, width=200)

if st.checkbox("Show/Hide"):
 
    # display the text if the checkbox returns True value
    st.text("Showing the widget")

# second argument is the options for the radio button
status = st.radio("Select Gender: ", ('Male', 'Female'))
 
# conditional statement to print 
# Male if male is selected else print female
# show the result using the success function
if (status == 'Male'):
    st.success("Male")
else:
    st.success("Female")

# second argument takes options
hobby = st.selectbox("Hobbies: ",
                     ['Dancing', 'Reading', 'Sports'])
 
# print the selected hobby
st.write("Your hobby is: ", hobby)

# second argument takes the options to show
hobbies = st.multiselect("Hobbies: ",
                         ['Dancing', 'Reading', 'Sports'])
 
# write the selected options
st.write("You selected", len(hobbies), 'hobbies')