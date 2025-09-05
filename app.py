import streamlit as st
import pandas as pd
from datetime import datetime
import os.path

# Set page configuration
st.set_page_config(page_title="Book Tracker", layout="wide")

# App title and description
st.title("📚 Reaped Reads - Book Tracker")
st.markdown("Keep track of all the reads you've reaped and your thoughts about them.")

# Initialize session state for the book database if it doesn't exist
if 'book_df' not in st.session_state:
    # Check if a saved CSV exists
    if os.path.isfile('book_tracker_data.csv'):
        st.session_state.book_df = pd.read_csv('book_tracker_data.csv')
    else:
        st.session_state.book_df = pd.DataFrame(columns=[
            'Title', 'Author', 'Date Finished', 'Reader', 'Rating', 'Notes'
        ])

# Function to save the dataframe to CSV
def save_dataframe():
    st.session_state.book_df.to_csv('book_tracker_data.csv', index=False)

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
                'Notes': notes,
                'Stars': '⭐' * rating  # Add a new column for star display
            }
            
            st.session_state.book_df = pd.concat([
                st.session_state.book_df, 
                pd.DataFrame([new_book])
            ], ignore_index=True)
            
            # Save to CSV
            save_dataframe()
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
    
    # Ensure the Stars column exists for existing data
    if 'Stars' not in filtered_df.columns and not filtered_df.empty:
        filtered_df['Stars'] = filtered_df['Rating'].apply(lambda x: '⭐' * int(x))
    
    # Display the filtered dataframe
    if not filtered_df.empty:
        display_df = filtered_df.sort_values(by='Date Finished', ascending=False).reset_index()
        
        # Choose columns to display
        display_columns = ['Title', 'Author', 'Date Finished', 'Reader', 'Stars', 'Notes']
        display_columns = [col for col in display_columns if col in display_df.columns]
        
        st.dataframe(
            display_df[display_columns],
            use_container_width=True,
            column_config={
                "Notes": st.column_config.TextColumn(
                    "Notes",
                    width="large",
                ),
                "Stars": st.column_config.TextColumn(
                    "Rating",
                    width="medium",
                )
            }
        )
        
        # Delete functionality
        st.subheader("Delete a Book")
        
        # Create a selection for books to delete
        book_options = [f"{i+1}. {row['Title']} by {row['Author']}" for i, row in display_df.iterrows()]
        book_to_delete = st.selectbox("Select a book to delete:", [""] + book_options)
        
        if book_to_delete:
            # Extract the index from the selection
            selected_index = int(book_to_delete.split('.')[0]) - 1
            
            # Get the original index from the filtered dataframe
            original_index = display_df.iloc[selected_index]['index']
            
            # Show book details for confirmation
            st.write(f"**Selected book:** {display_df.iloc[selected_index]['Title']} by {display_df.iloc[selected_index]['Author']}")
            
            # Confirmation button
            if st.button("Delete Selected Book", type="primary"):
                # Delete the book from the main dataframe
                st.session_state.book_df = st.session_state.book_df.drop(original_index).reset_index(drop=True)
                save_dataframe()
                st.success("Book deleted successfully!")
                st.experimental_rerun()  # Refresh the app to update the display
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
st.markdown("*Reading Reaper Book Tracker*")
