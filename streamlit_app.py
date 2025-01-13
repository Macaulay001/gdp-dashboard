import streamlit as st
import time
from fpdf import FPDF
import base64
from streamlit_option_menu import option_menu
import os
from PIL import Image
import pandas as pd
from datetime import timedelta
import sqlite3
from num2words import num2words
DB_FILE = "dojmac_global1.db"
conn = sqlite3.connect(DB_FILE)
c = conn.cursor()

st.set_page_config("DOJMAC GLOBAL ENTERPRISES",
#    page_icon=Image.open('icons.ico'),
#    layout="wide",
#    initial_sidebar_state="expanded",
)

# Create tables if they don't exist
c.execute("""
CREATE TABLE IF NOT EXISTS sales (
    date TEXT, 
    invoice_number TEXT UNIQUE DEFAULT '000000',
    vendor_name TEXT,
    customer_name TEXT,
    particulars TEXT,
    maruwa_supreme_quantity_owo REAL,
    maruwa_supreme_quantity_pieces REAL,
    maruwa_supreme_total_price REAL,
    tvs_quantity_owo REAL,
    tvs_quantity_pieces REAL,
    tvs_total_price REAL,
    honda_quantity_owo REAL,
    honda_quantity_pieces REAL,
    honda_total_price REAL,
    bajaj_quantity_owo REAL,
    bajaj_quantity_pieces REAL,
    bajaj_total_price REAL,
    lagatha_quantity_owo REAL,
    lagatha_quantity_pieces REAL,
    lagatha_total_price REAL,
    orobo_quantity_owo REAL,
    orobo_quantity_pieces REAL,
    orobo_total_price REAL,
    maruwa_special_quantity_owo REAL,
    maruwa_special_quantity_pieces REAL,
    maruwa_special_total_price REAL,
    TVS_special_quantity_owo REAL,
    TVS_special_quantity_pieces REAL,
    TVS_special_total_price REAL,
    honda_special_quantity_owo REAL,
    honda_special_quantity_pieces REAL,
    honda_special_total_price REAL,
    onirun_quantity_owo REAL,
    onirun_quantity_pieces REAL,
    onirun_total_price REAL,
    wewe_quantity_owo REAL,
    wewe_quantity_pieces REAL,
    wewe_total_price REAL,
    total_price REAL          
          
)
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS awo (
        date TEXT,
        vendor_name TEXT,
        details TEXT,
        price REAL,
        quantity_incoming INTEGER,
        quantity_outgoing INTEGER,
        balance REAL,
        rate  REAL
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS vendors (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        name TEXT UNIQUE,
        invoice_number TEXT
          
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS customers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE,
        balance REAL DEFAULT 0.0,
        phone_number TEXT
    )
""")

c.execute("""
    CREATE TABLE IF NOT EXISTS expenses (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        expense_type TEXT,
        amount REAL DEFAULT 0.0,
        bank_cash TEXT,
        deposits REAL DEFAULT 0.0,
        balance REAL DEFAULT 0.0
        
    )
""")


def create_customer_table(customer_name):
    table_name = customer_name.replace(" ", "_").lower()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_number TEXT,
            date TEXT,
            name TEXT,
            phone_number TEXT,
            details TEXT,
            debit REAL,
            credit REAL,
            balance REAL
        )
    """)
    
    conn.commit()


def create_vendor_table(Vendor_name):
    table_name = Vendor_name.replace(" ", "_").lower()
    c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT,
            vendor_name TEXT,
            details TEXT,
            price REAL,
            quantity_incoming INTEGER,
            quantity_outgoing INTEGER,
            balance REAL,
            rate  REAL,
            type TEXT
        )
    """)
    
    conn.commit()

def download_db():
    """Generate a link to download the current SQLite database."""
    with open(DB_FILE, "rb") as f:
        db_bytes = f.read()
    b64 = base64.b64encode(db_bytes).decode()
    href = f'<a href="data:file/sqlite;base64,{b64}" download="{DB_FILE}">Click here to download the database</a>'
    return href



def tools():
    st.header("Tools: Manage Vendors, Goods, Customers, and Invoices")
    tabs = st.tabs(["Vendors", "Goods", "Customers", "Daily Accounting", "Download Database"])

    with tabs[0]:
        st.subheader("Manage Vendors")
        vendor_name = st.text_input("Vendor Name")

        if st.button("Add Vendor"):
            try:
                c.execute("INSERT INTO vendors (name) VALUES (?)", (vendor_name,))
                conn.commit()
                st.success(f"Added vendor: {vendor_name}")

                create_vendor_table(vendor_name)
                table_name = vendor_name.replace(" ", "_").lower()
                
                c.execute(f"INSERT INTO {table_name} (vendor_name) VALUES (?)", (vendor_name,))
                conn.commit()


            except sqlite3.IntegrityError:
                st.error("Vendor already exists!")

        if st.button("Delete Vendor"):
            c.execute("DELETE FROM vendors WHERE name = ?", (vendor_name,))
            conn.commit()
            st.success(f"Deleted vendor: {vendor_name}")

    with tabs[1]:
        st.subheader("Manage Goods")
        st.text("Coming Soon")

    with tabs[2]:
        st.subheader("Manage Customers")
        customer_name = st.text_input("Customer Name")
        customer_balance = st.number_input("Customer Balance", min_value=0.0, format="%.2f", key='customer_balance')
        customer_phone_number = st.text_input("Phone Number")

        if st.button("Add Customer"):
            try:
                c.execute("INSERT INTO customers (name, balance, phone_number) VALUES (?, ?, ?)", (customer_name, customer_balance, customer_phone_number))
                conn.commit()
                create_customer_table(customer_name)
                table_name = customer_name.replace(" ", "_").lower() 
                c.execute(f"INSERT INTO {table_name} (name, phone_number, balance) VALUES (?, ?, ?)",
                  (customer_name, customer_phone_number, customer_balance))
                conn.commit()

                st.success(f"Added customer: {customer_name} and created tracking table.")
            except sqlite3.IntegrityError:
                st.error("Customer already exists!")

        if st.button("Delete Customer"):
            c.execute("DELETE FROM customers WHERE name = ?", (customer_name,))
            conn.commit()
            st.success(f"Deleted customer: {customer_name}")

    with tabs[3]:
        st.subheader("Daily Accounting")

        selected_report = st.selectbox("Select Report:", ["Daily Report", "Profit and Loss Report"])

        if selected_report == "Daily Report":
            daily_report()

        if selected_report == "Profit and Loss Report":

            # Select a Vendor
            c.execute("SELECT name FROM vendors")
            vendors = [row[0] for row in c.fetchall()]
            selected_vendor = st.selectbox("Select Awo Vendor", vendors)

            # Input Quantity Processed and Sold
            quantity_processed = st.number_input("Enter Quantity of Awo Processed and Sold", min_value=0)

            # Select Duration
            select_duration = st.selectbox(
                "Select Sales Duration:",
                ["All Time", "Today", "Yesterday", "Last 7 Days", "Last 30 Days", "Custom"]
            )

            # Get the current date
            today = pd.to_datetime("today").date()

            # Initialize date range
            start_date = None
            end_date = today

            # Set the date range based on duration
            if select_duration == "Today":
                start_date = end_date
            elif select_duration == "Yesterday":
                start_date = end_date - timedelta(days=1)
                end_date = start_date
            elif select_duration == "Last 7 Days":
                start_date = end_date - timedelta(days=7)
            elif select_duration == "Last 30 Days":
                start_date = end_date - timedelta(days=30)
            elif select_duration == "Custom":
                start_date = st.date_input("Start Date:", max_value=today)
                end_date = st.date_input("End Date:", max_value=today, value=today)
            elif select_duration == "All Time":
                start_date = None  # No filtering by date

            # Fetch sales for the selected vendor and duration
            if start_date and end_date:
                c.execute(
                    """
                        SELECT * FROM sales 
                        WHERE vendor_name = ? AND date BETWEEN ? AND ?
                    """, (selected_vendor, start_date, end_date))
            else:
                c.execute("SELECT * FROM sales WHERE vendor_name = ?", (selected_vendor,))

            sales_data = c.fetchall()

            if sales_data:
                # Define column names
                columns = [
                    "date", "invoice_number", "vendor_name", "customer_name", "particulars",
                    "maruwa_supreme_quantity_owo", "maruwa_special_quantity_pieces", "maruwa_special_total_price",
                    "tvs_quantity_owo", "tvs_special_quantity_pieces", "tvs_special_total_price",
                    "honda_quantity_owo", "honda_quantity_pieces", "honda_total_price",
                    "bajaj_quantity_owo", "bajaj_quantity_pieces", "bajaj_total_price",
                    "lagatha_quantity_owo", "lagatha_quantity_pieces", "lagatha_total_price",
                    "orobo_quantity_owo", "orobo_quantity_pieces", "orobo_total_price",
                    "maruwa_special_quantity_owo", "maruwa_special_quantity_pieces", "maruwa_special_total_price",
                    "TVS_special_quantity_owo", "TVS_special_quantity_pieces", "TVS_special_total_price",
                    "honda_special_quantity_owo", "honda_special_quantity_pieces", "honda_special_total_price",
                    "onirun_quantity_owo", "onirun_quantity_pieces", "onirun_total_price",
                    "wewe_quantity_owo", "wewe_quantity_pieces", "wewe_total_price", "total_price"
                ]

                # Convert sales data to a DataFrame
                sales_df = pd.DataFrame(sales_data, columns=columns)

                # Display sales data with checkboxes
                st.write(f"Sales for {selected_vendor} and Selected Duration:")
                selected_sales = []
                for idx, row in sales_df.iterrows():
                    selected = st.checkbox(
                        f"Invoice: {row['invoice_number']} | Customer: {row['customer_name']} | Date: {row['date']} | Total: #{row['total_price']:.2f}",
                        key=f"sale_{idx}"
                    )
                    if selected:
                        selected_sales.append(row)

                # Show selected sales if any are selected
                if selected_sales:
                    st.write("Selected Sales:")

                    # Ensure consistent structure for DataFrame
                    cleaned_sales = [
                        {col: row.get(col, None) if isinstance(row, dict) else row[col] for col in columns}
                        for row in selected_sales
                    ]
                    selected_sales_df = pd.DataFrame(cleaned_sales)
                    st.dataframe(selected_sales_df)

                # Check the vendor table for incoming rates
                vendor_table = selected_vendor.replace(" ", "_").lower()
                c.execute(f"SELECT name FROM sqlite_master WHERE type='table' AND name=?", (vendor_table,))
                table_exists = c.fetchone()

                if table_exists:
                    c.execute(f"SELECT rate FROM {vendor_table} WHERE type = 'incoming' LIMIT 1")
                    rate_record = c.fetchone()

                    if rate_record and rate_record[0] is not None:
                        rate = rate_record[0]
                        st.write(f"Rate for {selected_vendor}: #{rate:.2f} per unit")
                    else:
                        st.write(f"No 'incoming' rate found for {selected_vendor}.")
                else:
                    st.write(f"Vendor table '{vendor_table}' does not exist.")

                if st.button("Generate Report"):
                    total_sales_amount = sum(row['total_price'] for row in selected_sales)
                    st.write(f"Total Sales Amount: #{total_sales_amount:.2f}")

                    if quantity_processed > 0:
                        calculated_rate = total_sales_amount / quantity_processed
                        st.write(f"Calculated Sales Rate per AWO: #{calculated_rate:.2f}")

                        if rate:
                            profit_or_loss = calculated_rate - rate
                            if profit_or_loss > 0:
                                st.success(f"Profit per AWO: #{profit_or_loss:.2f}")
                            elif profit_or_loss < 0:
                                st.error(f"Loss per AWO: #{profit_or_loss:.2f}")
                            else:
                                st.info("No profit or loss.")

                            total_profit_or_loss = profit_or_loss * quantity_processed
                            st.write(f"Total Profit/Loss: #{total_profit_or_loss:.2f}")
                    else:
                        st.error("Quantity processed cannot be zero to calculate rates.")
            else:
                st.info(f"No sales found for {selected_vendor} in the selected duration.")

    with tabs[4]:
        st.markdown("### Download Current Database")
        
        if os.path.exists(DB_FILE):
            st.markdown(download_db(), unsafe_allow_html=True)
        else:
            st.error("Database file not found!")

def view_tables():
    st.header("View and Manage Tables")
    tables = ["sales", "awo", "vendors", "customers", "expenses"]
    selected_table = st.selectbox("Select Table to View:", tables, index=0)

    if selected_table == "customers":
        c.execute("SELECT name FROM customers ORDER BY name")
        customers = [row[0] for row in c.fetchall()]
        customer_dropdown = st.selectbox("Select Customer Table:", customers, index=0)

        if customer_dropdown:
            table_name = customer_dropdown.replace(" ", "_").lower()
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            if not df.empty:
                st.dataframe(df)

                row_id = st.number_input("Enter Row ID to Delete:", min_value=1, step=1)
                if st.button("Delete Row"):
                    try:
                        with st.spinner("Deleting row..."):
                            c.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
                            conn.commit()
                            st.success("Row deleted successfully")
                    except sqlite3.Error as e:
                        st.error(f"Error: {e}")
            else:
                st.info("The selected table is empty.")


    elif selected_table == "vendors":
        c.execute("SELECT name FROM vendors ORDER BY name")
        vendors = [row[0] for row in c.fetchall()]
        vendor_dropdown = st.selectbox("Select Vendor Table:", vendors, index=0)

        if vendor_dropdown:
            table_name = vendor_dropdown.replace(" ", "_").lower()
            df = pd.read_sql_query(f"SELECT * FROM {table_name}", conn)
            if not df.empty:
                st.dataframe(df)

                row_id = st.number_input("Enter Row ID to Delete:", min_value=1, step=1)
                if st.button("Delete Row"):
                    try:
                        with st.spinner("Deleting row..."):
                            c.execute(f"DELETE FROM {table_name} WHERE id = ?", (row_id,))
                            conn.commit()
                            st.success("Row deleted successfully")
                    except sqlite3.Error as e:
                        st.error(f"Error: {e}")
            else:
                st.info("The selected table is empty.")

    elif selected_table == "expenses":
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
        if not df.empty:
            st.dataframe(df)

            row_id = st.number_input("Enter Row ID to Delete:", min_value=1, step=1)
            if st.button("Delete Row"):
                try:
                    with st.spinner("Deleting row and adjusting balances..."):
                        # Fetch the row to be deleted
                        c.execute("SELECT amount, bank_cash FROM expenses WHERE id = ?", (row_id,))
                        row_data = c.fetchone()

                        if row_data:
                            amount_to_adjust, bank_or_cash = row_data

                            # Adjust balances for all subsequent rows with the same bank/cash type
                            c.execute("""
                                UPDATE expenses 
                                SET balance = balance - ?
                                WHERE bank_cash = ? AND id > ?
                            """, (amount_to_adjust, bank_or_cash, row_id))
                            conn.commit()

                            # Delete the selected row
                            c.execute("DELETE FROM expenses WHERE id = ?", (row_id,))
                            conn.commit()

                            st.success(f"Row ID {row_id} deleted successfully. Balances adjusted for {bank_or_cash}.")
                        else:
                            st.error("Row not found!")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")
        else:
            st.info("The selected table is empty.")




    else:
        df = pd.read_sql_query(f"SELECT * FROM {selected_table}", conn)
        if not df.empty:
            st.dataframe(df)

            row_id = st.number_input("Enter Row ID to Delete:", min_value=1, step=1)
            if st.button("Delete Row"):
                try:
                    with st.spinner("Deleting row..."):
                        c.execute(f"DELETE FROM {selected_table} WHERE rowid = ?", (row_id,))
                        conn.commit()
                        st.success("Row deleted successfully")
                except sqlite3.Error as e:
                    st.error(f"Error: {e}")
        else:
            st.info("The selected table is empty.")

def deposit():
    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")

    c.execute("SELECT name FROM customers ORDER BY name")
    customers = [row[0] for row in c.fetchall()]
    selected_customer = st.selectbox("Select Customer", customers)

    amount = st.number_input("Enter Amount Deposited", min_value=0.0)

    st.write("From:")
    bank_or_cash = st.selectbox("Select Bank or Cash:", ["Bank", "Cash"])

    details = f"Deposit of #{amount} via {bank_or_cash}"

    if st.button("Upload"):
        try:
            with st.spinner("Saving..."):
                # Update the customer's account table
                table_name = selected_customer.replace(" ", "_").lower()
                c.execute(f"SELECT balance FROM {table_name} ORDER BY id DESC LIMIT 1")
                previous_balance = c.fetchone()
                if previous_balance and previous_balance[0] is not None:
                    new_balance = previous_balance[0] + amount
                else:
                    new_balance = amount

                c.execute(f"INSERT INTO {table_name} (date, details, credit, balance) VALUES (?, ?, ?, ?)",
                          (date, details, amount, new_balance))
                c.execute("UPDATE customers SET balance = balance + ? WHERE name = ?", (amount, selected_customer))
                conn.commit()

                # Insert into expenses table
                

                # Fetch the previous balance for the selected bank/cash
                c.execute("""
                    SELECT balance FROM expenses WHERE bank_cash = ? ORDER BY id DESC LIMIT 1
                """, (bank_or_cash,))
                previous_expenses_balance = c.fetchone()

                print("Previous Expenses Balance for", bank_or_cash, ":", previous_expenses_balance)

                c.execute("""
                    INSERT INTO expenses (date, amount, deposits, bank_cash) 
                    VALUES (?, ?, ?, ?)
                """, (date, amount, "Deposit", bank_or_cash))
                conn.commit()
                # Calculate the new balance
                if previous_expenses_balance and previous_expenses_balance[0] is not None:
                    new_expenses_balance = previous_expenses_balance[0] + amount
                else:
                    new_expenses_balance = amount

                # Update the balance of the latest row for the selected bank/cash
                c.execute("""
                    UPDATE expenses SET balance = ? WHERE id = (
                        SELECT id FROM expenses WHERE bank_cash = ? ORDER BY id DESC LIMIT 1
                    )
                """, (new_expenses_balance, bank_or_cash))
                conn.commit()

                st.success(f"Deposit recorded successfully. New balance for {bank_or_cash}: #{new_expenses_balance:.2f}")
        except sqlite3.Error as e:
            st.error(f"Error: {e}")





def Sales():
    if 'reset' not in st.session_state:
        st.session_state.reset = False

    # Initialize values

    # Initialize values
    maruwa_supreme_quantity1, maruwa_supreme_quantity2 = 0, 0
    tvs_quantity1, tvs_quantity2 = 0, 0
    honda_quantity1, honda_quantity2 = 0, 0
    bajaj_quantity1, bajaj_quantity2 = 0, 0
    lagatha_quantity1, lagatha_quantity2 = 0, 0
    orobo_quantity1, orobo_quantity2 = 0, 0
    maruwa_special_quantity1, maruwa_special_quantity2 = 0, 0
    tvs_special_quantity1, tvs_special_quantity2 = 0, 0
    honda_special_quantity1, honda_special_quantity2 = 0, 0
    onirun_quantity1, onirun_quantity2 = 0, 0
    wewe_quantity1, wewe_quantity2 = 0, 0
    total_price = 0





    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")

    c.execute("SELECT COALESCE(MAX(CAST(invoice_number AS INTEGER)), 0) + 1 FROM sales")
    invoice_number = str(c.fetchone()[0]).zfill(6)

    c.execute("SELECT name FROM vendors")
    vendors = [row[0] for row in c.fetchall()]
    selected_vendor = st.selectbox("Select Vendor", vendors)

    c.execute("SELECT name FROM customers")
    customers = [row[0] for row in c.fetchall()]
    selected_customer = st.selectbox("Select Customer", customers)

    particulars = st.text_input("Particulars")

    goods = ["Maruwa/Supreme", "TVS", "Honda", "Bajaj", "Lagatha", "Orobo", "Maruwa_Supreme_Special", "TVS_Special", "Honda_Special", "Onirun", "Wewe"]
    price1 = [32000, 16000, 8000, 4000, 2000, 1000, 40000, 20000, 10000, 30000, 3000] 
    price2 = [640, 320, 160, 80, 40, 20, 800, 400, 200, 100, 0,0]
    selected_goods = st.multiselect("Select Goods:", goods)

    total_price = 0
    if "Maruwa/Supreme" in selected_goods:
        col1, col2 = st.columns(2)
        with col1:
            maruwa_supreme_quantity1 = st.number_input("Enter Maruwa/Supreme Owo (32000):", min_value=0, key="maruwa_supreme_quantity1")
        with col2:
            maruwa_supreme_quantity2 = st.number_input("Enter Maruwa/Supreme Pieces:", min_value=0, key="maruwa_supreme_quantity2")

        total_price += (maruwa_supreme_quantity1 * price1[0]) + (maruwa_supreme_quantity2 * price2[0])

    if "TVS" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            tvs_quantity1 = st.number_input("Enter TVS Owo (16000):", min_value=0, key="tvs_quantity1")
        with col2:
            tvs_quantity2 = st.number_input("Enter TVS Pieces:", min_value=0, key="tvs_quantity2")

        total_price += (tvs_quantity1 * price1[1]) + (tvs_quantity2 * price2[1])

    if "Honda" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            honda_special_quantity1 = st.number_input("Enter Honda Owo (8000):", min_value=0, key="honda_special_quantity1")
        with col2:
            honda_special_quantity2 = st.number_input("Enter Honda Pieces:", min_value=0, key="honda_special_quantity2")

        total_price += (honda_special_quantity1 * price1[2]) + (honda_special_quantity2 * price2[2])

    if "Bajaj" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            bajaj_quantity1 = st.number_input("Enter Bajaj Owo (4000):", min_value=0, key="bajaj_quantity1")
        with col2:
            bajaj_quantity2 = st.number_input("Enter Bajaj Pieces:", min_value=0, key="bajaj_quantity2")

        total_price += (bajaj_quantity1 * price1[3]) + (bajaj_quantity2 * price2[3])

    if "Lagatha" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            lagatha_quantity1 = st.number_input("Enter Lagatha Owo (2000):", min_value=0, key="lagatha_quantity1")
        with col2:
            lagatha_quantity2 = st.number_input("Enter Lagatha Pieces:", min_value=0, key="lagatha_quantity2")

        total_price += (lagatha_quantity1 * price1[4]) + (lagatha_quantity2 * price2[4])

    if "Orobo" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            orobo_quantity1 = st.number_input("Enter Orobo Owo (#1000):", min_value=0, key="orobo_quantity1")
        with col2:
            orobo_quantity2 = st.number_input("Enter Orobo Pieces:", min_value=0, key="orobo_quantity2")

        total_price += (orobo_quantity1 * price1[5]) + (orobo_quantity2 * price2[5])

    if "Maruwa_Supreme_Special" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            maruwa_special_quantity1 = st.number_input("Enter Maruwa Supreme Special Owo (#40,000):", min_value=0, key="maruwa_special_quantity1")
        with col2:
            maruwa_special_quantity2 = st.number_input("Enter Maruwa Special Pieces:", min_value=0, key="maruwa_special_quantity2")

        total_price += (maruwa_special_quantity1 * price1[6]) + (maruwa_special_quantity2 * price2[6])

    if "TVS_Special" in selected_goods:
        
        col1, col2 = st.columns(2)
        with col1:
            tvs_special_quantity1 = st.number_input("Enter TVS Special Owo (#20,000):", min_value=0, key="tvs_special_quantity1")
        with col2:
            tvs_special_quantity2 = st.number_input("Enter TVS Special Pieces:", min_value=0, key="tvs_special_quantity2")

        total_price += (tvs_special_quantity1 * price1[7]) + (tvs_special_quantity2 * price2[7])

    if "Honda_Special" in selected_goods:
        
        
        col1, col2 = st.columns(2)
        with col1:
            honda_special_quantity1 = st.number_input("Enter Honda Special Owo (#10,000):", min_value=0, key="honda_special_quantity1")
        with col2:
            honda_special_quantity2 = st.number_input("Enter Honda Special Pieces:", min_value=0, key="honda_special_quantity2")

        total_price += (honda_special_quantity1 * price1[8]) + (honda_special_quantity2 * price2[8])

    if "Onirun" in selected_goods:
        
        
        col1, col2 = st.columns(2)
        with col1:
            onirun_quantity1 = st.number_input("Enter Onirun Ike (#30,000):", min_value=0, key="onirun_quantity1")
        with col2:
            onirun_quantity2 = st.number_input("Enter Onirun Pieces:", min_value=0, key="onirun_quantity2")

        total_price += (onirun_quantity1 * price1[9]) + (onirun_quantity2 * price2[9])

    if "Wewe" in selected_goods:
        
        
        
        col1, col2 = st.columns(2)
        with col1:
            wewe_quantity1 = st.number_input("Enter Wewe Ike (#3,000):", min_value=0, key="wewe_quantity1")
        with col2:
            wewe_quantity2 = st.number_input("Enter Wewe Pieces:", min_value=0, key="wewe_quantity2")

        total_price += (wewe_quantity1 * price1[10]) + (wewe_quantity2 * price2[10])


   

    st.subheader(f"Total Price: #{total_price:.2f}")
    total_price_in_words = num2words(total_price, lang='en')
    st.subheader(f"Total Price in Words: {total_price_in_words}")

    if st.button("Save Sales"):
        try:
            with st.spinner("Saving..."):
                c.execute("""
                    INSERT INTO sales (
                        date, invoice_number, vendor_name, customer_name, particulars,
                        maruwa_supreme_quantity_owo, maruwa_special_quantity_pieces, maruwa_special_total_price,
                        tvs_quantity_owo, tvs_special_quantity_pieces, tvs_special_total_price,
                        honda_quantity_owo, honda_quantity_pieces, honda_total_price,
                          bajaj_quantity_owo, bajaj_quantity_pieces, bajaj_total_price,
                          lagatha_quantity_owo, lagatha_quantity_pieces, lagatha_total_price,
                          orobo_quantity_owo, orobo_quantity_pieces, orobo_total_price,
                          maruwa_special_quantity_owo, maruwa_special_quantity_pieces, maruwa_special_total_price,
                          TVS_special_quantity_owo, TVS_special_quantity_pieces, TVS_special_total_price,
                          honda_special_quantity_owo, honda_special_quantity_pieces, honda_special_total_price,
                          onirun_quantity_owo, onirun_quantity_pieces, onirun_total_price,
                          wewe_quantity_owo, wewe_quantity_pieces, wewe_total_price,
                          total_price

                           ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)


                """, (
                    date, invoice_number, selected_vendor, selected_customer, particulars,
                    maruwa_supreme_quantity1, maruwa_supreme_quantity2, (maruwa_supreme_quantity1 * price1[0]) + (maruwa_supreme_quantity2 * price2[0]),
                    tvs_quantity1, tvs_quantity2, (tvs_quantity1 * price1[1]) + (tvs_quantity2 * price2[1]),
                    honda_quantity1, honda_quantity2, (honda_quantity1 * price1[2]) + (honda_quantity2 * price2[2]),
                    bajaj_quantity1, bajaj_quantity2, (bajaj_quantity1 * price1[3]) + (bajaj_quantity2 * price2[3]),
                    lagatha_quantity1, lagatha_quantity2, (lagatha_quantity1 * price1[4]) + (lagatha_quantity2 * price2[4]),
                    orobo_quantity1, orobo_quantity2, (orobo_quantity1 * price1[5]) + (orobo_quantity2 * price2[5]),
                    maruwa_special_quantity1, maruwa_special_quantity2, (maruwa_special_quantity1 * price1[6]) + (maruwa_special_quantity2 * price2[6]),
                    tvs_special_quantity1, tvs_special_quantity2, (tvs_special_quantity1 * price1[7]) + (tvs_special_quantity2 * price2[7]),
                    honda_special_quantity1, honda_special_quantity2, (honda_special_quantity1 * price1[8]) + (honda_special_quantity2 * price2[8]),
                    onirun_quantity1, onirun_quantity2, (onirun_quantity1 * price1[9]) + (onirun_quantity2 * price2[9]),
                    wewe_quantity1, wewe_quantity2, (wewe_quantity1 * price1[10]) + (wewe_quantity2 * price2[10]),
                    total_price
                ))
                conn.commit()

                # Insert into customer's account

                #custom_particulars, make a statement with goods > 0 by reading the db
                particulars = ""

                # Create particulars string for goods with quantities greater than zero
                if maruwa_supreme_quantity1 > 0 or maruwa_supreme_quantity2 > 0:
                    particulars += f"Maruwa/Supreme: {maruwa_supreme_quantity1} Owo, {maruwa_supreme_quantity2} Pieces\n"
                if tvs_quantity1 > 0 or tvs_quantity2 > 0:
                    particulars += f"TVS: {tvs_quantity1} Owo, {tvs_quantity2} Pieces\n"
                if honda_special_quantity1 > 0 or honda_special_quantity2 > 0:
                    particulars += f"Honda: {honda_special_quantity1} Owo, {honda_special_quantity2} Pieces\n"
                if bajaj_quantity1 > 0 or bajaj_quantity2 > 0:
                    particulars += f"Bajaj: {bajaj_quantity1} Owo, {bajaj_quantity2} Pieces\n"
                if lagatha_quantity1 > 0 or lagatha_quantity2 > 0:
                    particulars += f"Lagatha: {lagatha_quantity1} Owo, {lagatha_quantity2} Pieces\n"
                if orobo_quantity1 > 0 or orobo_quantity2 > 0:
                    particulars += f"Orobo: {orobo_quantity1} Owo, {orobo_quantity2} Pieces\n"
                if maruwa_special_quantity1 > 0 or maruwa_special_quantity2 > 0:
                    particulars += f"Maruwa Special: {maruwa_special_quantity1} Owo, {maruwa_special_quantity2} Pieces\n"
                if tvs_special_quantity1 > 0 or tvs_special_quantity2 > 0:
                    particulars += f"TVS Special: {tvs_special_quantity1} Owo, {tvs_special_quantity2} Pieces\n"
                if honda_special_quantity1 > 0 or honda_special_quantity2 > 0:
                    particulars += f"Honda Special: {honda_special_quantity1} Owo, {honda_special_quantity2} Pieces\n"
                if onirun_quantity1 > 0 or onirun_quantity2 > 0:
                    particulars += f"Onirun: {onirun_quantity1} Owo, {onirun_quantity2} Pieces\n"
                if wewe_quantity1 > 0 or wewe_quantity2 > 0:
                    particulars += f"Wewe: {wewe_quantity1} Owo, {wewe_quantity2} Pieces\n"

                

                table_name = selected_customer.replace(" ", "_").lower()
                c.execute(f"SELECT balance FROM {table_name} ORDER BY id DESC LIMIT 1")
                previous_balance = c.fetchone()
                if previous_balance:
                    new_balance = previous_balance[0] - total_price
                else:
                    new_balance = -total_price

                c.execute(f"INSERT INTO {table_name} (date, invoice_number, details, debit, balance) VALUES (?, ?, ?, ?, ?) ",
                          (date, invoice_number, particulars, total_price, new_balance))
                c.execute("UPDATE customers SET balance = ? WHERE name = ?", (new_balance, selected_customer))
                conn.commit()


                st.balloons()
        except sqlite3.IntegrityError:
            st.error("Invoice already exists!")


def awo():
    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")

    c.execute("SELECT name FROM vendors")
    vendors = [row[0] for row in c.fetchall()]
    selected_vendor = st.selectbox("Select Vendor", vendors)

    details = st.text_area("Details")
    choice = st.selectbox("Select Type:", ["RECEIVED", "PROCESSED"])
    table_name = selected_vendor.replace(" ", "_").lower()

    if choice == "RECEIVED":
        quantity = st.number_input("Enter Quantity Received", min_value=0)
        price = st.number_input("Enter Total Price", min_value=0)
        bank_or_cash = st.selectbox("Select Bank or Cash:", ["Bank", "Cash"])
        rate = price / quantity if quantity > 0 else 0
        if st.button("Check Rate"):
            st.success(f"Rate: #{rate:.2f} per AWO")

    if choice == "PROCESSED":
        quantity = st.number_input("Enter Quantity Processed", min_value=0)
        if st.button("Show Remaining AWO"):
            c.execute(f"SELECT SUM(quantity_incoming) - SUM(quantity_outgoing) AS remaining FROM {table_name}")
            remaining = c.fetchone()[0]
            if remaining is not None:
                st.write(f"Remaining AWO for {selected_vendor}: {remaining} units")
            else:
                st.info("No AWO received yet for this vendor.")

    if st.button("Upload"):
        try:
            with st.spinner("Saving..."):
                if choice == "RECEIVED":
                    # Check if there is already a "RECEIVED" entry for the selected vendor
                    c.execute(f"""
                        SELECT COUNT(*) FROM {table_name} WHERE vendor_name = ? AND type = 'incoming'
                    """, (selected_vendor,))
                    existing_entries = c.fetchone()[0]

                    if existing_entries > 0:
                        st.error(f"AWO has already been received from {selected_vendor}. Create a new Vendor.")
                        return

                    # Insert the "RECEIVED" entry
                    c.execute(f"""
                        INSERT INTO {table_name} (date, vendor_name, details, quantity_incoming, price, rate, type, balance)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (date, selected_vendor, details, quantity, price, rate, "incoming", quantity))
                    conn.commit()

                    st.success(f"AWO received from {selected_vendor} successfully recorded.")

                elif choice == "PROCESSED":
                    # Fetch the earliest incoming record
                    c.execute(f"""
                        SELECT id, quantity_incoming, balance FROM {table_name}
                        WHERE type = 'incoming' AND balance > 0
                        ORDER BY date ASC LIMIT 1
                    """)
                    incoming_record = c.fetchone()

                    if incoming_record:
                        record_id, available_quantity, balance = incoming_record

                        if quantity > balance:
                            st.error("Processed quantity exceeds available AWO.")
                            return

                        # Update or delete the incoming record
                        new_balance = balance - quantity
                        if new_balance > 0:
                            c.execute(f"""
                                UPDATE {table_name} 
                                SET balance = ? 
                                WHERE id = ?
                            """, (new_balance, record_id))
                        else:
                            c.execute(f"""
                                DELETE FROM {table_name} 
                                WHERE id = ?
                            """, (record_id,))
                        conn.commit()

                        # Insert the processed record
                        c.execute(f"""
                            INSERT INTO {table_name} (date, vendor_name, details, quantity_outgoing, balance)
                            VALUES (?, ?, ?, ?, ?)
                        """, (date, selected_vendor, details, quantity, new_balance))
                        conn.commit()

                        # Show the remaining AWO
                        c.execute(f"SELECT SUM(quantity_incoming) - SUM(quantity_outgoing) AS remaining FROM {table_name}")
                        remaining = c.fetchone()[0]
                        st.success(f"AWO processed. Remaining AWO for {selected_vendor}: {remaining} units")
                    else:
                        st.error("No AWO available to process.")

        except sqlite3.Error as e:
            st.error(f"Error: {e}")

            st.error(f"Error: {e}")

            
def expenses():

    date = st.date_input("Enter Date:")
    date = date.strftime("%Y-%m-%d")
    st.write("Expenses type:")
    selected_expenses = st.selectbox(
        "Select Expenses Type:", 
        ["Awo Purchases", "Carriage Inward", "Arrangement boys", "Cutting boys", "Tinjo", "Tinse", "Tinge", "Tinka", 
         "Directors expenses", "Firewood", "Buka expenses", "Sack/ Nylon/ Thread", "Miscellaneous", "Others"]
    )
    amount = st.number_input("Enter Amount", min_value=0.0, step=0.01)
    st.write("From:")
    bank_or_cash = st.selectbox("Select Bank or Cash:", ["Bank", "Cash"])

    if st.button("Upload"):
        try:
            with st.spinner("Saving..."):
                # Insert new expense
                
                # Fetch the previous balance for the selected bank/cash
                c.execute("""
                    SELECT balance FROM expenses WHERE bank_cash = ? ORDER BY id DESC LIMIT 1
                """, (bank_or_cash,))
                conn.commit()
                previous_expenses_balance = c.fetchone()
                c.execute("""
                    INSERT INTO expenses (date, amount, expense_type, bank_cash) 
                    VALUES (?, ?, ?, ?)
                """, (date, amount, selected_expenses, bank_or_cash))
                conn.commit()

                # Calculate the new balance
                if previous_expenses_balance:
                    new_expenses_balance = previous_expenses_balance[0] - amount
                else:
                    new_expenses_balance = -amount

                # Update the balance of the latest row
                c.execute("""
                    UPDATE expenses SET balance = ? WHERE id = (
                        SELECT id FROM expenses WHERE bank_cash = ? ORDER BY id DESC LIMIT 1
                    )
                """, (new_expenses_balance, bank_or_cash))

                conn.commit()
                st.success("Uploaded successfully")
        except sqlite3.Error as e:
            st.error(f"Error: {e}")




def daily_report():
    pass

def profit_and_loss_report():
    pass




selected = option_menu(
    menu_title=None,
    options=["Sales", "AWO", "Deposit", "Expenses", "Tools", "View Tables"],
    icons=["house", "bi bi-person-lock", "bi bi-cash", 'bi bi-cash-coin', 'bi bi-tools', 'bi bi-table'],
    menu_icon="cast",
    default_index=0,
    orientation="horizontal",
)

if selected == "Sales":
    Sales()
elif selected == "AWO":
    awo()
elif selected == "Deposit":
    deposit()
elif selected == "Tools":
    tools()
elif selected == "View Tables":
    view_tables()
elif selected == "Expenses":
    expenses()
