# streamlit_app.py
import streamlit as st
from sqlalchemy import text


# convert this  2023-09-14 17:15:22.973407 into a datetime object.
from datetime import datetime


# Initialize connection.
conn = st.connection("postgresql", type="sql")

# Perform query.
df = conn.query('SELECT * FROM APPOINTMENT' , ttl="10m" )

# Separate error handling from main logic
def add_pet_owners():
    """
    Creates the pet_owners table and inserts sample data
    """
    try:
        with conn.session as s:
            s.execute(
                text('CREATE TABLE IF NOT EXISTS pet_owners (person TEXT, pet TEXT);')
            )
            s.execute(
                text('DELETE FROM pet_owners;')
            )
            pet_owners = {'jerry': 'fish', 'barbara': 'cat', 'alex': 'puppy'}
            for k , v in pet_owners.items():
                s.execute(
                    text("INSERT INTO pet_owners (person, pet) VALUES (:person, :pet)"),
                    params={"person": k, "pet": v},
                )
            # s.execute(
            #     text("INSERT INTO pet_owners (person, pet) VALUES (:person, :pet)"),
            #     params={"person": "jerry", "pet": "fish"},
            # )

            s.commit()
        st.write("Successfully added pet owners!")
    except Exception as e:
        st.error(f"Error adding pet owners: {e}")

if st.button("Add More Sample Pet Owners"):
    add_pet_owners()
# Query and display the data you inserted
pet_owners = conn.query('SELECT * FROM pet_owners' , ttl=20 )
st.dataframe(pet_owners)

  
# Dispying existence data from database
for row in df.itertuples():
    # Now use strftime
    desired_format = "%d-%m-%Y %H:%M:%S"

    st.title(f"Name : {row.firstname} {row.lastname}")
    st.write(f"Email : {row.email}")
    st.write(f"ROLE : {row.role}")
    st.write(f"PHONE : {row.phone}")
    st.write(f"Created At: {row.created_at.strftime(desired_format)}")
# Print results.
st.header("Fetch all old data from database")
st.dataframe(df)  