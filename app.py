import streamlit as st
import pandas as pd
from datetime import datetime
import os.path

# Set page configuration
st.set_page_config(page_title="Book Tracker", layout="wide")

# App title and description
st.title("📚 Family Book Tracker")
st.markdown("Keep track of all the books you've read and your thoughts about them.")

# Initialize session state for the book database if it doesn't exist
if 'book_df' not in st.session_state:
    # Check if a saved CSV exists
    if os.path.isfile('book_tracker_data.csv'):
        st.session_state.book_df = pd.read_csv('book_tracker_data.csv')
    else:
        st.session_state.book_df = pd.DataFrame(columns=[
            'Title', 'Author', 'Date Finished', 'Reader', 'Rating', 'Notes'
        ])

# Create two columns for layout
col1, col2 = st.columns([1, 2])

# Form for adding a new book
with col1:
    st.header("Add a New Book")
    with st.form("book_form"):
        title = st.text_input("Book Title")
        author = st.text_input("Author")
        date_finished = st.date_input("Date Finished", datetime.now())
        reader = st.text_input("Reader")
        rating = st.slider("Rating (1-5 stars)", 1, 5, 3)
        notes = st.text_area("Notes and Thoughts")
        
        submit_button = st.form_submit_button("Add Book")
        
        if submit_button and title and author:
            # Add the new book to the dataframe
            new_book = {
                'Title': title,
                'Author': author,
                'Date Finished': date_finished.strftime('%Y-%m-%d'),
                'Reader': reader,
                'Rating': rating,
                'Notes': notes
            }
            
            st.session_state.book_df = pd.concat([
                st.session_state.book_df, 
                pd.DataFrame([new_book])
            ], ignore_index=True)
            
            # Save to CSV
            st.session_state.book_df.to_csv('book_tracker_data.csv', index=False)
            st.success("Book added successfully!")

# Display the book database
with col2:
    st.header("Your Reading History")
    
    # Add filters
    st.subheader("Filter Books")
    col_filter1, col_filter2 = st.columns(2)
    
    with col_filter1:
        reader_filter = st.multiselect(
            "Filter by Reader",
            options=sorted(st.session_state.book_df['Reader'].unique()) if not st.session_state.book_df.empty else []
        )
    
    with col_filter2:
        rating_filter = st.multiselect(
            "Filter by Rating",
            options=sorted(st.session_state.book_df['Rating'].unique()) if not st.session_state.book_df.empty else []
        )
    
    # Apply filters
    filtered_df = st.session_state.book_df
    if reader_filter:
        filtered_df = filtered_df[filtered_df['Reader'].isin(reader_filter)]
    if rating_filter:
        filtered_df = filtered_df[filtered_df['Rating'].isin(rating_filter)]
    
    # Display the filtered dataframe
    if not filtered_df.empty:
        st.dataframe(
            filtered_df.sort_values(by='Date Finished', ascending=False),
            use_container_width=True,
            column_config={
                "Rating": st.column_config.NumberColumn(
                    "Rating",
                    format="⭐" * 5,
                ),
                "Notes": st.column_config.TextColumn(
                    "Notes",
                    width="large",
                ),
            }
        )
    else:
        st.info("No books added yet. Use the form to add your first book!")

# Add a download button for the data
st.download_button(
    label="Download Book Data as CSV",
    data=st.session_state.book_df.to_csv(index=False).encode('utf-8'),
    file_name='book_tracker_export.csv',
    mime='text/csv',
)

# Add footer
st.markdown("---")
st.markdown("*Book Tracker*")
