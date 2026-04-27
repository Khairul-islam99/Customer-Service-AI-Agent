import os
import psycopg2
from dotenv import load_dotenv
from langchain_core.tools import tool
from pydantic import BaseModel, Field

# Load environment variables from the .env file
load_dotenv()

def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""
    return psycopg2.connect(os.getenv("DB_URL"))

# TOOL 1: Search Properties

class SearchInput(BaseModel):
    location: str = Field(description="Location to search (e.g., Cox's Bazar).")

@tool("search_available_properties", args_schema=SearchInput)
def search_available_properties(location: str) -> str:
    """Searches for available properties in a specific location."""
    try:
        # Open connection and cursor (automatically closed after 'with' block)
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT title, price_per_night_bdt FROM listings WHERE location = %s AND is_available = TRUE;", (location,))
            results = cur.fetchall()
            if not results:
                return f"No properties found in {location}."
            
            return "\n".join([f"- {r[0]} (BDT {r[1]})" for r in results])
    except Exception as e:
        return f"Error: {e}"
    
# TOOL 2: Get Property Details

class DetailsInput(BaseModel):
    property_name: str = Field(description="Name of the property.")

@tool("get_listing_details", args_schema=DetailsInput)
def get_listing_details(property_name: str) -> str:
    """Gets detailed information for a specific property."""
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            cur.execute("SELECT location, price_per_night_bdt, is_available FROM listings WHERE title ILIKE %s;", (property_name,))
            res = cur.fetchone()
            
            if not res:
                return "Property not found."
            
            return f"Location: {res[0]}, Price: BDT {res[1]}, Available: {res[2]}"
    except Exception as e:
        return f"Error: {e}"


# TOOL 3: Create Booking

class BookingInput(BaseModel):
    property_name: str = Field(description="Name of the property.")
    guest_name: str = Field(description="Name of the guest.")
    check_in_date: str = Field(description="Check-in date (YYYY-MM-DD).")
    check_out_date: str = Field(description="Check-out date (YYYY-MM-DD).")

@tool("create_booking", args_schema=BookingInput)
def create_booking(property_name: str, guest_name: str, check_in_date: str, check_out_date: str) -> str:
    """Creates a booking for a property."""
    try:
        with get_db_connection() as conn, conn.cursor() as cur:
            # Step 1: Verify property exists and is available
            cur.execute("SELECT id FROM listings WHERE title ILIKE %s AND is_available = TRUE;", (property_name,))
            listing = cur.fetchone()
            
            if not listing:
                return "Property is not available."
            
            # Step 2: Insert the booking record
            cur.execute(
                "INSERT INTO bookings (listing_id, guest_name, check_in_date, check_out_date) VALUES (%s, %s, %s, %s) RETURNING id;",
                (listing[0], guest_name, check_in_date, check_out_date)
            )
            booking_id = cur.fetchone()[0]
            
            # Step 3: Mark the property as unavailable
            cur.execute("UPDATE listings SET is_available = FALSE WHERE id = %s;", (listing[0],))
            
            # Commit the transaction to save changes
            conn.commit()
            
            return f"Booking confirmed! ID: {booking_id}"
    except Exception as e:
        return f"Error: {e}"